"""Models for managing Shopify listings."""

from collections import defaultdict

from django.db import models, transaction
from shopify_api_py import products, session

from inventory.models import (
    BaseProduct,
    ProductImageLink,
    ProductRange,
    ProductRangeImageLink,
)


class ShopifyTag(models.Model):
    """Model for Shopify product tags."""

    name = models.CharField(max_length=255)

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

    def __str__(self):
        return self.product_range.sku


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
        if shopify_listing_object.product_range.has_variations():
            options = cls._get_options(shopify_listing_object)
            variants = cls._get_variants(shopify_listing_object, options)
        else:
            options = None
            variants = None
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
            for variant in shopify_product.variants:
                shopify_variation_object = ShopifyVariation.objects.get(
                    product__sku=variant.sku
                )
                shopify_variation_object.variant_id = variant.id
                shopify_variation_object.inventory_item_id = variant.inventory_item_id
                shopify_variation_object.save()
        cls._set_customs_information(shopify_product)
        cls._add_images_to_product(shopify_product, product_range)

    @staticmethod
    def _get_options(shopify_listing_object):
        variation_matrix = (
            shopify_listing_object.product_range.variation_option_values()
        )
        return products.create_options(variation_matrix)

    @staticmethod
    def _get_variants(shopify_listing_object, options):
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
    def _set_customs_information(shopify_product):
        for variant in shopify_product.variants:
            product = BaseProduct.objects.get(sku=variant.sku)
            products.set_customs_information(
                inventory_item_id=variant.inventory_item_id,
                country_of_origin_code="CN",
                hs_code=product.hs_code,
            )

    @staticmethod
    def _add_images_to_product(shopify_product, product_range):
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
            images.extend(product_images)
            primary_image = product.get_primary_image()
            if primary_image is not None:
                variant_images[primary_image].append(variant.id)
        images = set([image for image in images if image not in variant_images.keys()])
        for image in images:
            products.add_product_image(
                product_id=shopify_product.id, image_url=image.image_file.url
            )
        for variant_image, variant_ids in variant_images.items():
            products.add_product_image(
                product_id=shopify_product.id,
                image_url=variant_image.image_file.url,
                variant_ids=variant_ids,
            )
