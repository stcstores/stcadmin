"""Models for managing Shopify listings."""

from collections import defaultdict

from django.db import models, transaction
from django.urls import reverse_lazy
from django.utils import timezone
from shopify_api_py import products, session

from channels import tasks
from inventory.models import (
    BaseProduct,
    ProductImageLink,
    ProductRange,
    ProductRangeImageLink,
)

from .shopify_manager import ShopifyManager


class ShopifyTag(models.Model):
    """Model for Shopify product tags."""

    name = models.CharField(max_length=255, unique=True, db_index=True)

    class Meta:
        """Meta class for the ShopifyTag model."""

        verbose_name = "Shopify Tag"
        verbose_name_plural = "Shopify Tags"
        ordering = ("name",)

    def __str__(self):
        return self.name


class ShopifyListing(models.Model):
    """Model for Shopify product listings."""

    product_range = models.OneToOneField(
        ProductRange,
        on_delete=models.CASCADE,
        related_name="shopify_listing",
        primary_key=False,
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(ShopifyTag, blank=True)
    product_id = models.PositiveBigIntegerField(blank=True, null=True)

    class Meta:
        """Meta class for the ShopifyListing model."""

        verbose_name = "Shopify Listing"
        verbose_name_plural = "Shopify Listings"

    def __str__(self):
        return self.product_range.sku

    def get_absolute_url(self):
        """Return the URL of the edit page for this object."""
        return reverse_lazy("channels:shopify_listing", kwargs={"listing_pk": self.pk})

    def listing_is_active(self):
        """Return True if an active listing for this product can be found, otherwise False."""
        if self.product_id is None:
            return False
        else:
            return ShopifyManager.product_exists(self.product_id)

    def get_last_update(self):
        """Return the latest update instance for this listing."""
        return ShopifyUpdate.objects.filter(listing=self).latest("created_at")

    def upload(self):
        """Create or update the a Shopify listing for this instance."""
        update = ShopifyUpdate.objects.start_upload_listing(self)
        try:
            if self.product_id is None:
                tasks.create_shopify_product.delay(
                    listing_pk=self.pk, update_pk=update.pk
                )
            else:
                tasks.update_shopify_product.delay(
                    listing_pk=self.pk, update_pk=update.pk
                )
        except Exception:
            update.set_error()
            raise


class ShopifyVariation(models.Model):
    """Model for Shopify product variants."""

    listing = models.ForeignKey(
        ShopifyListing, on_delete=models.CASCADE, related_name="variations"
    )
    product = models.OneToOneField(
        BaseProduct,
        on_delete=models.CASCADE,
        related_name="shopify_variation",
        primary_key=False,
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    variant_id = models.PositiveBigIntegerField(blank=True, null=True)
    inventory_item_id = models.PositiveBigIntegerField(blank=True, null=True)

    def __str__(self):
        return self.product.sku

    class Meta:
        """Meta class for the ShopifyVariation model."""

        verbose_name = "Shopify Variation"
        verbose_name_plural = "Shopify Variations"


class ShopifyUpdateManager(models.Manager):
    """Manager for the ShopifyUpdate model."""

    def start_upload_listing(self, listing):
        """Record the start of a create or update operation."""
        if self.filter(listing=listing, completed_at__isnull=True).exists():
            raise Exception(
                "Cannot start operation on Shopify listing while another is ongoing."
            )
        if listing.product_id:
            operation_type = ShopifyUpdate.UPDATE_PRODUCT
        else:
            operation_type = ShopifyUpdate.CREATE_PRODUCT
        update = self.model(listing=listing, operation_type=operation_type)
        update.save()
        return update


class ShopifyUpdate(models.Model):
    """Model for Shopify update records."""

    CREATE_PRODUCT = "Create Product"
    UPDATE_PRODUCT = "Update Product"
    RETRIEVE_PRODUCT = "Retrieve Product"

    listing = models.ForeignKey(
        ShopifyListing, on_delete=models.CASCADE, related_name="update_records"
    )
    operation_type = models.CharField(
        max_length=20,
        choices=(
            (CREATE_PRODUCT, CREATE_PRODUCT),
            (UPDATE_PRODUCT, UPDATE_PRODUCT),
            (RETRIEVE_PRODUCT, RETRIEVE_PRODUCT),
        ),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    error = models.BooleanField(default=False)

    objects = ShopifyUpdateManager()

    class Meta:
        """Meta class for the ShopifyUpdate model."""

        verbose_name = "Shopify Update"
        verbose_name_plural = "Shopify Updates"

    def set_complete(self):
        """Set the update as completed succesfully."""
        self.completed_at = timezone.now()
        self.save()

    def set_error(self):
        """Set the update as completed with an error."""
        self.completed_at = timezone.now()
        self.error = True
        self.save()


class ShopifyListingManager:
    """Provides methods for managing Shopify listings."""

    @classmethod
    @session.shopify_api_session
    def create_listing(cls, shopify_listing_object):
        """Create a new Shopify product based on a ShopifyListing instance.

        Args:
            shopify_listing_object (channels.models.shopify_models.ShopifyListing): The
                ShopifyListing object to base the listing on.
        """
        product_range = shopify_listing_object.product_range
        options = cls._get_options(shopify_listing_object)
        variants = cls._get_variants(shopify_listing_object, options=options)
        shopify_product = products.create_product(
            title=shopify_listing_object.title,
            body_html=shopify_listing_object.description,
            variants=variants,
            options=options,
            tags=[tag.name for tag in shopify_listing_object.tags.all()],
            vendor=product_range.products.variations().first().brand.name,
        )
        with transaction.atomic():
            shopify_listing_object.product_id = shopify_product.id
            shopify_listing_object.save()
            if len(shopify_product.variants) == 1:
                variant = shopify_product.variants[0]
                variation = shopify_listing_object.variations.first()
                cls._set_variant_details(variant=variant, variation=variation)
                variant.save()
            for variant in shopify_product.variants:
                shopify_variation_object = ShopifyVariation.objects.get(
                    product__sku=variant.sku
                )
                shopify_variation_object.variant_id = variant.id
                shopify_variation_object.inventory_item_id = variant.inventory_item_id
                shopify_variation_object.save()
        cls._set_customs_information(shopify_product)
        cls._set_listing_images(shopify_product, product_range)

    @classmethod
    @session.shopify_api_session
    def update_listing(cls, shopify_listing_object):
        """Update a Shopify product listing.

        Args:
            shopify_listing_object (channels.models.shopify_models.ShopifyListing): The
                ShopifyListing object representing the product to update.
        """
        shopify_product = cls._get_shopify_product(shopify_listing_object.product_id)
        cls._set_product_details(
            product=shopify_product, listing=shopify_listing_object
        )
        shopify_product.images = []
        shopify_product.save()
        for variant in shopify_product.variants:
            variation = shopify_listing_object.variations.get(product__sku=variant.sku)
            cls._set_variant_details(variant=variant, variation=variation)
            variant.save()
        cls._set_listing_images(
            shopify_product=shopify_product,
            product_range=shopify_listing_object.product_range,
        )

    @staticmethod
    def _get_shopify_product(product_id):
        return products.get_product_by_id(product_id=product_id)

    @staticmethod
    def _get_options(shopify_listing_object):
        if shopify_listing_object.variations.count == 1:
            return None
        else:
            variation_matrix = (
                shopify_listing_object.product_range.variation_option_values()
            )
            return products.create_options(variation_matrix)

    @staticmethod
    def _get_variants(shopify_listing_object, options=None):
        variants = []
        for variation_object in shopify_listing_object.variations.all():
            product = variation_object.product
            price = float(variation_object.price)
            variation_values = product.variation()
            option_values = []
            for option in options:
                option_values.append(variation_values[option.name])
            variants.append(
                products.create_variation(
                    sku=product.sku,
                    option_values=option_values,
                    barcode=product.barcode,
                    grams=product.weight_grams,
                    price=price,
                )
            )
        return variants

    @staticmethod
    def _set_variant_details(variant, variation):
        variant.sku = variation.product.sku
        variant.barcode = variation.product.barcode
        variant.grams = variation.product.weight_grams
        variant.price = float(variation.price)
        variant.weight_unit = "g"
        variant.tracked = True

    @staticmethod
    def _set_product_details(product, listing):
        product.title = listing.title
        product.body_html = listing.description
        product.vendor = listing.product_range.products.variations().first().brand.name
        product.tags = ",".join(listing.tags.values_list("name", flat=True))

    @staticmethod
    def _set_customs_information(shopify_product):
        for variant in shopify_product.variants:
            product = BaseProduct.objects.get(sku=variant.sku)
            products.set_customs_information(
                inventory_item_id=variant.inventory_item_id,
                country_of_origin_code="CN",
                hs_code=product.hs_code,
            )

    @classmethod
    def _set_listing_images(cls, shopify_product, product_range):
        images = [
            image_link.image
            for image_link in ProductRangeImageLink.objects.filter(
                product_range=product_range
            )
        ]
        variant_images = defaultdict(list)
        for variant in shopify_product.variants:
            product = BaseProduct.objects.get(sku=variant.sku)
            product_images = [
                image_link.image
                for image_link in ProductImageLink.objects.filter(product=product)
            ]
            if len(product_images) > 0:
                variant_images[product_images[0]].append(variant.id)
            images.extend(product_images[1:])
        images = cls.de_duplicate_images(
            [image for image in images if image not in variant_images.keys()]
        )
        for image in images:
            products.add_product_image(
                product_id=shopify_product.id, image_url=image.square_image.url
            )
        for variant_image, variant_ids in variant_images.items():
            products.add_product_image(
                product_id=shopify_product.id,
                image_url=variant_image.square_image.url,
                variant_ids=variant_ids,
            )

    @staticmethod
    def de_duplicate_images(image_list):
        """Return a list of images with duplicates removed."""
        image_ids = []
        de_duplicated_images = []
        for image in image_list:
            if image.id in image_ids:
                continue
            de_duplicated_images.append(image)
            image_ids.append(image.id)
        return de_duplicated_images
