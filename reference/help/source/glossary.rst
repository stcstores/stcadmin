
.. |mul| unicode:: U+00d7

********
Glossary
********

This is a list of terms used within Cloud Commerce and STC Admin.

.. contents:: Table of Contents

.. _glossary-product_range:

Product Range
=============
Cloud Commerce uses Product Ranges to represent an item in the inventory. They
consist of one or more :ref:`Products <glossary-product>` which represent the
item's :ref:`Variations <glossary-variation>`. If the item does not have
**variations** the **Product Range** will contain a single **Product**.

A **Product Range** also represents a single :ref:`listing <glossary-listing>`.
To include multiple **Products** in a listing they must be in the same **Product
Range**.

You *cannot* delete a **Product Range** once listed. Instead mark it as
:ref:`Inventory <inventory-range_page-end_of_line>`.

.. _glossary-product_range-single_product:

Single Product
______________
A **Single Product** is a :ref:`Product Range <glossary-product_range>`
containing a single :ref:`Product <glossary-product>`, or in other words, an
item with no :ref:`Variations <glossary-variation>`.

.. _glossary-product_range-variation_product:

Variation Product
_________________
A **Variation Product** is a :ref:`Product Range <glossary-product_range>`
containing multiple :ref:`Products <glossary-product>`, or in other words, an
item with :ref:`Variations <glossary-variation>`.

.. _glossary-variation:

Variation
=========
When a product is available in different versions, such as different colours or
sizes, we refer to these versions as **Variations** and a single version as a
**Variation**. Cloud Commerce stores **Variations** as a :ref:`Product Range
<glossary-product_range>` containing multiple :ref:`Products
<glossary-product>`. Each **Product** will represent a single **Variation**. We
refer to these as :ref:`Variation Products
<glossary-product_range-variation_product>`. Cloud Commerce stores products
without **Variations** as a **Product Range** with a single **Product**, we
refer to these as :ref:`Single Products
<glossary-product_range-single_product>`.

.. _glossary-product:

Product
========
Product is the term used by Cloud Commerce for an *Inventory Item* that exists
within a :ref:`Product Range <glossary-product_range>`. They represent
:ref:`Variations <glossary-variation>` and the two terms are interchangeable. A
single item with no *variations* is a single **Product Range** with a single
**Product**.

.. _glossary-selling_channel:

Selling Channel
===============
A **Selling Channel** is an e-commerce platform on which we sell our products.

.. _glossary-listing:

Listing
=======
A **Listing** is the selling page for a :ref:`Product Range
<glossary-product_range>` on a :ref:`Selling Channel
<glossary-selling_channel>`. You can create **Listings** through Cloud Commerce
or through the **Selling Channels** themselves. We encourage you to use Cloud
Commerce over directly listing on the **Channel**.

.. _glossary-locations:

Locations
=========

.. _glossary-locations-warehouse:

Warehouse
_________
Warehouses are how Cloud Commerce recognises the physical location where we
store stock. A Warehouse will contain a number of :ref:`Bays
<glossary-locations-bay>`. A Warehouse exists for each department and that
department's product will usually use **Bays** within that **Warehouse**.

.. _glossary-locations-bay:

Bay
___
Bays are the locations within a :ref:`Warehouse <glossary-locations-warehouse>`
in which a particular :ref:`Product <glossary-product>` resides. A **Product**
can exist in multiple **Bays**, however, they must all belong to the same
**Warehouse**; this **Warehouse** represents the pick list on which the
**Product** will appear. The **Products** in a :ref:`Product Range
<glossary-product_range>` can belong to different **Warehouses**. If stock
physically exists in different **Warehouses** use a normal **Bays** for **Bays**
in the primary picking location and **Backup Bays** secondary locations. Create
new bays using :ref:`The Create Bay Page <inventory-create_bay>`.

.. _glossary-locations-backup_bay:

Backup Bay
__________

Backup bays are secondary picking locations for products. Cloud Commerce must
see them as existing within the same :ref:`Warehouse
<glossary-locations-warehouse>` as the primary **Bays** while physically
existing in a different location. Their names include the physical location of
the stock as well as an abbreviation of the :ref:`department
<glossary-product_range_details-department>` to which the product belongs.

.. _glossary-product_options:

Product Options
===============
Product options are a way of storing information about products in Cloud
Commerce. We use them for three purposes:

.. _glossary-product_options-listing_options:

Listing Options
_______________
Listing Options provide information about the product in it's listing on eBay,
Amazon and stcstores.co.uk. They appear as key/value pairs. Only use **Listing
Options** that are appropriate for the product.

.. _glossary-product_options-variation_options:

Variation Options
_________________
Variation Options work in a similar way to :ref:`Listing Options
<glossary-product_options-listing_options>` except that they separate
:ref:`Variations <glossary-variation>` within a :ref:`Product Range
<glossary-product_range>`. They appear in listings as the drop down box, or
other widget, used to select a particular variation. You can use any **Listing
Option** a **Variation Option**. The most commonly used ones are *Size*,
*Colour*, and *Design*.

.. _glossary-product_options-product_info:

Product Info
_______________
Product Info Options provide information about a :ref:`Product
<glossary-product>` for our internal reference. They do not appear in listings.
STC Admin makes use of some  **Product Info Options**, therefore they *must*
conform to a particular format. For this reason you must edit them in STC Admin,
not Cloud Commerce.

.. _glossary-product_range_details:

Product Range Details
=====================
The details of a :ref:`Product Range <glossary-product_range>` apply to all of
the :ref:`Products <glossary-product>` within it. We store some of these details
as part of the **Product** and *must* match for every **Product** in a
**Range**.

.. _glossary-product_range_details-range_sku:

Range SKU
_________

A **Range SKU** is a unique identifier for a :ref:`Product Range
<glossary-product_range>`. It consists of nine alphanumeric characters separated
into three groups of three by hyphens, similar to a :ref:`Product SKU
<glossary-product_details-sku>` preceded by the characters "*RNG_*", e.g
RNG_007-SXY-NP1. You can find a **Range**'s SKU on it's :ref:`Range Page
<inventory-range_page>`. To create a new **Range SKU** use the :ref:`Generate
SKU Page <inventory-generate_sku>`. A **Range SKU** must **never** change.

.. _glossary-product_range_details-title:

Title
_____
The name of the :ref:`Product Range <glossary-product_range>`. It *must not*
contain key words, this includes colours, sizes etc. You should put this
information in :ref:`Product Options <glossary-product_options>`, it will still
appear in the title in the inventory and on pick lists. You can use an altered
version of the title in :ref:`Listings <glossary-listing>`, except on
stcstores.co.uk. It must be short, clear, concise and grammatically correct.
Proper use of **title case** throughout the title is necessary. An example of a
good **Range Title** might be "Named Toothbrush Holder", a bad title might be
"toothbrush tooth brush holder - RED LARGE". You can edit a **Range Title** on
the :ref:`Description Page <inventory-description_page>` or the :ref:`Product
Editor <product_editor>`.

.. _glossary-product_range_details-department:

Department
__________
The department to which the :ref:`Product Range <glossary-product_range>`
belongs. E.g *Surewear*, *Allsorts*. You can change a **Range**'s **Department**
on the :ref:`Description Page <inventory-description_page>` or the :ref:`Product
Editor <product_editor>`.

.. _glossary-product_range_details-description:

Description
___________
The description of the :ref:`Product Range <glossary-product_range>` used in
listings. It is not possible to have a separate description for each
:ref:`Product <glossary-product>`. If this seems necessary it may be better to
separate the **Range** into individual **Products**. It may seem natural to
start the description with the name of the product, **do not** do this. The
description appears under the title of the listing on every selling channel
except eBay, where Cloud Commerce adds it to the description automatically when
listed. The **Description** has special formatting applied by STC Admin, **do
not** edit the description in Cloud Commerce.

* This is **required** for any item listed online.
* Must **not** start with the title of the product.
* Must **not** include information about **price** or **postage**.
* Do **not** use abbreviations such as "L" for length as this is not
  translatable for foreign listings.
* Sentences must end with full stops.
* Make correct use of capitalisation.
* The description can contain bullet points to highlight key information
  but **MUST NOT** consist **solely** of bullet points.

You can edit a **Range**'s **Description** on the :ref:`Description Page
<inventory-description_page>` or the :ref:`Product Editor <product_editor>`.

.. _glossary-product_range_details-amazon_bullet_points:

Amazon Bullet Points
____________________
These are the bullet points that appear at the top of Amazon listings. When
added to a :ref:`Product Range <glossary-product_range>` they added to the
listing automatically when listed through Cloud Commerce.

* These are far more prominent than the main description.
* Each bullet point should be about one sentence long.
* Can repeat key information from the main description.
* All rules for :ref:`descriptions <glossary-product_range_details-description>`
  also apply to bullet points.

You can edit a **Range**'s **Amazon Bullet Points** on the :ref:`Description
Page <inventory-description_page>` or the :ref:`Product Editor
<product_editor>`.

.. _glossary-product_range_details-amazon_search_terms:

Amazon Search Terms
___________________
The search terms for the Amazon listings of the :ref:`Product Range
<glossary-product_range>`. They consist of key words and phrases that people
might use to find the product. Alternative words and spellings must always
go here, not in the listing title.

You can edit a **Range**'s **Amazon Search Terms** on the :ref:`Description Page
<inventory-description_page>` or the :ref:`Product Editor <product_editor>`.

.. _glossary-product_range_details-end_of_line:

End of Line
___________
Once sold, you cannot delete a :ref:`Product Range <glossary-product_range>` as
it is part of our sales history. Instead they mark them as **End of Line**. Do
this for any **Range** for which every :ref:`Product <glossary-product>` is
permanently out of stock. **Ranges** marked **End of Line** will not show in the
results of the :ref:`Product Search <inventory-product_search>` unless
explicitly included.

.. note::
    Once listed for sale **do not delete** :ref:`Product Ranges
    <glossary-product_range>` or :ref:`Products <glossary-product>`, mark them
    as **End of Line** instead. You can delete them if they are not yet listed
    on *any* channel and where created erroneously.

You can mark a **Range** as **End of Line** on it's :ref:`Range Page
<inventory-range_page>`.

.. _glossary-product_details:

Product Details
===============
The following are attributes of :ref:`Products <glossary-product>` used for
our reference or to provide information for customers in listings.

.. _glossary-product_details-sku:

Product SKU
___________

A **Product SKU** is a unique identifier for a :ref:`Product
<glossary-product>`. It is the most reliable way to search for a particular
**Product**. A **SKU** consists of nine alphanumeric characters separated into
three groups of three by hyphens, e.g PR6-TTH-6UC. You can get a new **SKU**
using the :ref:`Generate SKU Page <inventory-generate_sku>`. A **Product**'s
**SKU** must *never* change and two **Products** *cannot* share a **SKU**. Do
not confuse with :ref:`Range SKUs <glossary-product_range_details-range_sku>`.

.. _glossary-product_details-title:

Title
_____
The title of a :ref:`Product <glossary-product>` *must* always be identical to
the :ref:`Title <glossary-product_range_details-title>` of the :ref:`Product
Range <glossary-product_range>`. You cannot change it in STC Admin unless
updated along with the **Range** title, however it is possible to change this in
Cloud Commerce, *do not* do this. When you update the **Product** STC Admin sets
it's **Title** to that of it's **Range**, removing any extra information placed
there. Consider using :ref:`Listing Options
<glossary-product_options-listing_options>`.

.. _glossary-product_details-barcode:

Barcode
_______
Selling channels use the :ref:`Product <glossary-product>`'s barcode as a unique
identifier by selling channels. Most products come with a barcode from the
manufacturer, however in some circumstances it is preferable to use a new
barcode from our database.

* Must be unique within our inventory.
* Use the manufacturer provided barcode where possible.
* Do not use the manufacturer's barcode if multiple variations use the same one.
* When listing variations do **not** mix our barcodes with manufacturer
  barcodes. If manufacturer barcodes are not available for all variations use
  our own.

A **Product**'s **Barcode** must always match the barcode used in it's listings,
therefore you should generally not change it. If it is necessary to change a
**Barcode** you can do this in the :ref:`Product Editor <product_editor>` or on
the **Product**'s :ref:`Product Page <inventory-product_page>`.

.. _glossary-product_details-purchase_price:

Purchase Price
______________

The price at which we purchase stock of the :ref:`Product <glossary-product>`.
This should always reflect the current price at which we can restock the item.
If the supplier's prices change update the **Purchase Price** using the
:ref:`Product Editor <product_editor>` or the **Product**'s :ref:`Product Page
<inventory-product_page>`.

.. _glossary-product_details-price:

Price
_____

The base price of the :ref:`Product <glossary-product>`. This is the price at
which we sell the product in the UK, *not including* VAT or shipping. You can
change this in the :ref:`Product Editor <product_editor>` or on the
**Product**'s :ref:`Product Page <inventory-product_page>`.

.. _glossary-product_details-vat_rate:

VAT Rate
________

The rate of VAT charged on the :ref:`Product <glossary-product>`. See
`VAT rates on different goods and services <https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services>`_.
You can change this in the :ref:`Product Editor <product_editor>` or on the
**Product**'s :ref:`Product Page <inventory-product_page>`.

.. _glossary-product_details-retail_price:

Retail Price
____________

The price at which we sell the :ref:`Product <glossary-product>` in shops. You
can change this in the :ref:`Product Editor <product_editor>` or on the
**Product**'s :ref:`Product Page <inventory-product_page>`.

.. _glossary-product_details-stock_level:

Stock Level
___________

The quantity of the :ref:`Product <glossary-product>` in stock. You can update a
**Product**'s **Stock Level** from the :ref:`Product Search Results
<inventory-product_search-search-results>`, the **Product**'s :ref:`Product
Range <glossary-product_range>`'s :ref:`Range Page <inventory-range_page>` or
the **Product**'s :ref:`Product Page <inventory-product_page>`. See
:ref:`Updating Stock Levels <inventory-common_tasks-updating_stock_levels>`.

.. _glossary-product_details-location:

Location
________
A list of :ref:`Bays <glossary-locations-bay>` in which the :ref:`Product
<glossary-product>` exists. See :ref:`Locations <glossary-locations>`. You can
change a **Product**'s locations on it's :ref:`Product Page
<inventory-product_page>`, it's :ref:`Range <glossary-product_range>`'s
:ref:`Location Page <inventory-location_page>` or the :ref:`Product Editor
<product_editor>`. See :ref:`Updating a Product's Locations
<inventory-common_tasks-updating_product_locations>`.

.. _glossary-product_details-supplier:

Supplier
________
The company from which we purchase the :ref:`Product <glossary-product>`. Create
new **Suppliers** on the :ref:`Create Supplier Page
<inventory-create_supplier>`. You can change a **Product**'s **Supplier** on
it's :ref:`Product Page <inventory-product_page>` or in the :ref:`Product Editor
<product_editor>`.

.. _glossary-product_details-supplier_sku:

Supplier SKU
____________
The SKU or product code used by the :ref:`Supplier
<glossary-product_details-supplier>` to identify the product. You can change a
**Product**'s **Supplier SKU** on it's :ref:`Product Page
<inventory-product_page>` or in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-weight:

Weight
______
The shipping weight of the :ref:`Product <glossary-product>` in grams. This
includes the estimated weight of packaging. We use this weight to calculate the
cost of shipping, therefore accuracy is important. You can change a
**Product**'s **Weight** on it's :ref:`Product Page <inventory-product_page>` or
in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-dimensions:

Dimensions
__________
The physical size of the :ref:`Product <glossary-product>` in millimetres.

* Length: The largest dimension of the **Product.**
* Width: The second largest dimension of the **Product.**
* Height: The smallest dimension of the **Product.**

You can change a **Product**'s **Dimensions** on it's :ref:`Product Page
<inventory-product_page>` or in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-package_type:

Package Type
____________
Every :ref:`Product <glossary-product>` must have a package type specified.
Cloud Commerce requires this for selecting the correct shipping service to use
when sending the item. It is crucial that you set the package type correctly as
the wrong package type will increase the price at which we can sell an item, or
incur fines from shipping providers.

All size and weight limits are for the fully packed item which may include
bubble wrap and cardboard. If you are unsure what packaging a product will
require, check with the packing department.

The possible **Package Types** are as follows:

.. _glossary-package_types-large_letter:

Large Letter
************
* Must fit 353 |mul| 250 |mul| 25mm.
* Maximum weight 750g.
* A general guide line; anything that can fit through a letter box go
  **Large Letter**.

.. _glossary-package_types-packet:

Packet
******
* Must not exceed 60cm in any dimension.
* Length + Width + Height cannot exceed 90cm.
* If it is possible to package the item as a tube (Umbrellas for example) they
  can be up to 90cm long.
* Maximum weight 2kg.

.. _glossary-package_types-heavy_and_large:

Heavy and Large
***************
* Must not exceed 120cm in any dimension.
* Must not exceed 15kg.
* Most items too heavy to send as a :ref:`Packet <glossary-package_types-packet>`
  can go **Heavy and Large** unless they are *excessively* large.

.. _glossary-package_types-courier:

Courier
*******
* Any item too large or too heavy for either **Packet** or **Heavy and Large**
  must go via **Courier**.
* **Note:** This can sometimes be expensive.

You can change a **Product**'s **Package Type** on it's :ref:`Product Page
<inventory-product_page>` or in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-brand:

Brand
_____
The brand of the :ref:`Product <glossary-product>`. Cloud Commerce requires a
**Brand** for listings, however a place holder such as "Unbranded" is
acceptable. You can change a **Product**'s **Brand** on it's :ref:`Product Page
<inventory-product_page>` or in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-manufacturer:

Manufacturer
____________
The company that manufactures the :ref:`Product <glossary-product>`. Cloud
Commerce requires a **Manufacturer** for listings. If in doubt use the
:ref:`Brand <glossary-product_details-brand>` as the **Manufacturer**. You can
change a **Product**'s **Manufacturer** on it's :ref:`Product Page
<inventory-product_page>` or in the :ref:`Product Editor <product_editor>`.

.. _glossary-product_details-gender:

Gender
______
Gender is a field required by Amazon for listings of clothing items. Do not set
**Gender** for non clothing :ref:`Products <glossary-product>`. The value of
gender must be one of the values accepted by Amazon. You can change a
**Product**'s **Gender** on it's :ref:`Product Page <inventory-product_page>` or
in the :ref:`Product Editor <product_editor>`.
