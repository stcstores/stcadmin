
.. contents:: Table of Contents

******************************
Creating Productcs on STCAdmin
******************************

How to Create a New Product Range
=================================

The product creation process consists of a number of pages containing forms
in which you will enter the details of the product. The top of each of these
pages will show a list of pages required to complete the product and allow
you to jump to other pages. Some pages may not appear or may not allow you to
jump to them depending on the type of product you are creating and how far
through the process you have gotten.

To begin creating a product navigate to
`STC Admin`_ and go to the
`Inventory <{% url 'inventory:product_search' %}>`_ section and select
`New Product <{% url 'product_editor:basic_info' %}>`_.

.. _STC Admin: http://stcadmin.stcstores.co.uk

If you have already created a product you will see forms are still filled
with the details of that product. This is so that a product can be re-created
if there is an error during product creation. To start a new product click the
*Clear New Product* button at the top of the page. This will clear the current
product and take you to the first page of the product creation process, the
`Basic Info`_ page. This page allows you to enter basic detail of the product
range as well as information relevent to listings that needs to be identcal
for every product in the range.

After completing this page click the continue button underneath the form. This
will take you to the `Product Info`_ page. On this page you will enter all the
details of the product, or one of them if you are creating a variation product
range. At the bottom of the form you will see buttons to *Create Single Product*
or *Create Variation Product*. Select *Create Single Product*, if your
new Product Range contains a single Product, or the *Create Variation Product*
button, if it contains more than one Product.

Creating Single Products
________________________

After selecting *Create Single Product* you will be taken to the
`Listing Options`_ page.

Pages
=====

Basic Info
__________

The basic info page collects information required for both single and
variation products and that will be the same for every variation in a range.

Fields:

* `Title`_
* `Department`_
* `Description`_
* `Amazon Bullet Points`_
* `Amazon Search Terms`_


Product Info
____________

The product info page collects information required for a single variation.
When creating a single product this is where you will put the bulk of the
details. When creating variations this page will set default values for the
Variation Info page where you can alter it for each variation.

Fields:

* `Barcode`_
* `Purchase Price`_
* `Price`_
* `Retail Price`_
* `Stock Level`_
* `Location`_
* `Supplier`_
* `Supplier SKU`_
* `Weight`_
* `Dimensions`_
* `Package Type`_
* `Brand`_
* `Manufacturer`_
* `Gender`_

Listing Options
_______________

The Listing Options page allows you to use *Product Options* to add details
to your product listings. The `Variation Listing Options`_ page performs the
same role for variation listings.

Variation Options
_________________

The Variation Options page is where you set the variations for a varation
product. It will give you a choice of *Product Options* to use as the way in
which the product varies *e.g* Colour, Size. List every value each applicable
*Product Option*.

Unused Variations
_________________

The Unused Variation page gives you a list of every possible combination of
variations as set on the `Variation Options`_ page. If any combination is not
required for your product deselect the apropriate checkbox. Deselected
combinations will not appear as variations in your product.

Variation Info
______________

The Variation Info page allows you to set the details of each variation.
Unless changed each variation will copy the details set on the `Product Info`_
page. At the top of the page is the list of fields, you can use this to
select a field to edit. When you select a field it will appear for each of the
variations listed below. You can manually change the field for each variation
or update them in bulk. To bulk update variations, select them using the
checkboxes next to them or by toggeing them by variation option using the
buttons above. You can then type the required value into the top field next
to the copy button and click copy to replace the contents of the field for all
selected variations.

Fields:

* `Barcode`_
* `Purchase Price`_
* `Price`_
* `Retail Price`_
* `Stock Level`_
* `Location`_
* `Supplier`_
* `Supplier SKU`_
* `Weight`_
* `Dimensions`_
* `Package Type`_
* `Brand`_
* `Manufacturer`_
* `Gender`_


Variation Listing Options
_________________________

The Listing Options page allows you to use *Product Options* to add details
to your product listings. You select fields  and update variations in the same
way as the  `Variation Info`_ page. The `Listing Options`_ page performs the
same role for single products.

Finish
______
The **Finish** page will redirect you to the inventory page for your new product
and begin the process of creating it. Until all the variations complete the
range will show as **INCOMPLETE**. When all variations are complete the
incomplete message will disapear. If an error occurs during product creation
you will have the option to try again or edit the product.


Fields
======

Title
_____

The name of the **Product Range** to create.

* The title must *not* contain key words. This includes colours, sizes etc.
* This title is for internal reference and is not necessarily used for listings.
  It is, however, used on our website.
* It must make sense gramatically and not include dashes.
* It must use proper **title case**. (The first letter of every word should be
  capital except for connective words such as "and" or "the" unless they are the
  first word of the title.)
* **Required**

Department
__________
The department to which the product belongs.

* **Required**

Description
___________
Full description used in listings.

* This is **required** for any item listed online. You can leavit it blank and
  add it later if necessary.
* Must **not** start with the title of the product.
* Must **not** include information about **price** or **postage**.
* Do **not** use abrieviations such as "L" for length as this is not
  translatable for foreign listings.
* Sentences must end with full stops.
* Make correct use of capitalisation.
* The description can **contain** bullet points to hightlight key information
  but **MUST NOT** consist soley of bullet ponts.
* **Not Required**

Amazon Bullet Points
____________________
The bullet points that will appear at the top of the Amazon listing.

* These are far more prominent than the main description.
* Each bullet point should be about one sentence long.
* Can repeat key information from the main description.
* All rules for descriptions also apply to bullet ponts.
* **Not Required**

Amazon Search Terms
___________________
Key words and phrases that people might use to find the product.

* A list of keywords and key phrases used by Amazon to match a listing to
  customer's searches.
* Can include alternate words and spelling.
* Search terms must go here, **not** in the product title.
* **Not Required**

Barcode
_______
The barcode used when listing the product.

* Must be unique within our inventory.
* Use the manufacturer provided barcode where possible.
* Do not use the manufactuer's barcode if multiple variations use the same one.
* Leave blank to use a barcode from our stock.
* When listing variations do **not** mix our barcodes with manufacturer
  barcodes. If manufacturer barcodes are not available for all variations use
  our own.
* **Not Required**

Purchase Price
______________
The price paid to purchase the product.

* This should always reflect the currrent price at which we can restock the
  item.
* If the supplier's prices change update the purchase price.
* **Required**

Price
_____
The price and VAT rate the product sells with online in the UK.

* You cannot enter a price until you select a VAT rate.
* You can enter the price either with or without VAT using the apropriate
  field, the other will update accordingly.
* **Required**

Retail Price
____________

The price at which the product sells in shops.

* **Not Required**

Stock Level
___________
The initial stock level of the product.

* **Required**

Location
________
The picking location of the product.

* Set the Warehouse field according to the pick list on which the product
  should appear.
* The warehouse field will default to the department selected on the Basic Info
  page.
* You can set multiple bays as required but they must all belong to the same
  warehouse.
* If you leave the product field blank it will set to the default bay for the
  selected warehouse.
* Add new bays using the Create Bay page.
* **Warehouse field required.**


Supplier
________
The supplier which sells the product.

* Select the supplier from the list.
* Create new suppliers on the Create Supplier page.
* **Required**

Supplier SKU
____________
The supplier's SKU for the product.

* This is sometimes refered to as a **Product Code**.
* **Not Required**

Weight
______
The weight of the product in **grams**.

* Enter the correct weight to the nearest gram.
* Accuracy is important as our couriers charge based on this number.
* If the item requires extra packaging such as cardboard estimate how much
  weight this will add and add that to the weight.
* **Required**

Dimensions
_____________________________________
Dimensions of the product in Milimeters.

* Enter the largest dimension in Length.
* Enter the second largest dimenstion in Weight.
* Enter the smallest dimension in Height.
* Used to select the appropriate shipping service and will not appear in the
  listing.
* **Not Required.**

Package Type
____________
The type of package used to send the product.

* Used to select the appropriate shipping service for the product both in the UK
  and internationally.
* Based on size and weight of the item when packed.
* This will be greater for items requiring additional packaging such as
  cardboard.
* If in doubt contact the packing department.
* See `Package Types <{% url 'reference:package_types' %}>`_ for information
  about which package type to select.
* **Required**

Brand
_____
The brand of the product.

* If there is no available brand for the product a placeholder such as
  "Unbranded" is acceptable.
* **Required**

Manufacturer
____________
The manufacturer of the product.

* If the manufacturer is unknown use the name of the supplier.
* **Required**

Gender
______
The target gender of the product.

* Required for listing clothing items on Amazon. Leave blank for other products.
