

.. contents:: Table of Contents

******************************
Creating Productcs on STCAdmin
******************************

To begin creating a product navigate to http://stcadmin.stcstores.co.uk and go to the
`Inventory <{% url 'inventory:product_search' %}>`_ section and select
`New Product <{% url 'product_editor:basic_info' %}>`_.

The New Product Form
====================

The new product form is where you put information about your product. This is
the only step when creating single products, however variation products work
slightly differently and also require the `Variation Table <#variation_table>`_
to be filled in. For more information see `Variation Listings <#variation_listings>`_.

The new product form is colour coded:

* Fields with a **White background** are **optional** and can be left blank if they are not applicable or are to be filled in later.
* Fields witha **Grey background** are **required** for all products and must always be filled in.
* Fields with a **Blue background** are for **Product Options**. They work differently for `single products <#single_product_options>`_ and `variation products <#variation_product_options>`_.


Fields
======

The following is a list of fields that appear in the new product forms. This can be used as a checklist when creating products.

Title
______
The name of the **Product Range** to be created.

.. note:: All products are part of a **Product Range** even if they do not include variatons.

* The title should *not* contain key words. This includes colours, sizes etc.
* This title is for internal reference and will not necessarily be used for listings on eBay. It will, however, be used on our website.
* It must make sense gramatically and not include dashes.
* It must use proper **title case**. (The first letter of every word should be capital except for connective words such as "and" or "the" unless they are the first word of the title.)

Barcode
_______
The barcode that will be used when listing the item.

* Must be unique within our inventory.
* If left blank a new barcode will be applied from our stock.
* If the product has a barcode from the manufacturer this should be used.
* If the product has variations with the same barcode they should **not** be used.
* When listing variations do **not** mix our barcodes with manufacturer barcodes. If manufacturer barcodes are not available for all variations our own should be used.

Purchase Price
______________
The price for which this product was purchased.

* This should always reflect the currrent price at which we can restock the item.
* It should be updated if the supplier's prices change.

VAT Rate
________
The applicable rate of VAT for this product in the UK.

* Most products require 20% VAT.
* Books and children's clothing and shoes require 0% VAT.
* The selected VAT Rate will affect the **Price** field and so must be set first.

Price
_____
The base price of the product.

* The price depends on the selected **VAT Rate**. This must always be set first.
* Two fields are provided allowing you to enter the price either with or without VAT. Use the appropriate field and the other will update.
* This should **NOT** include **Shipping**.
* This is for internal reference and will **Not** be used for listings

Stock Level
___________
The initial stock level of the product.

Department
__________
The department to which the product belongs.

Location
________
The location where the product will be stocked.

* If your department does not use **Locations** this can be left blank.

Supplier
________
The supplier from which the item is purchased.

* Select the supplier from the list.
* If the supplier is new or does not appear in the list it must be added before you create your product. Contact Luke or Jake to add a supllier to the list.

Supplier SKU
____________
The supplier's SKU for the product.

* This is sometimes refered to as a **Product Code**.
* This can be left blank if none exists.

Weight
______
The weight of the product in **Grams**.

* Enter the correct weight to the nearest gram.
* Accuracy is important as we are charged postage based on this number.
* If the item is likely to require extra packaging such as cardboard estimate how much weight this will add and add that to the weight.

Dimensions (Height, Width and Length)
_____________________________________
Dimensions of the product in Milimeters.

* Can be left blank if unavilable (if you do not have the product to hand to measure for example) but should be added later when possible.
* Enter the largest dimension in Length.
* Enter the second largest dimenstion in Weight.
* Enter the smallest dimension in Height.
* This is used to select the appropriate shipping service and will not appear in the listing.

Package Type
____________
The shipping method that will be used in the UK.

* Used to select the appropriate shipping service for the product both in the UK and internationally.
* This must be selected correctly as we will be billed for postage based on this.
* Based on size and weight when the item is packed. Items requiering cardboard will be effected. If in doubt contact the packing department.
* See `Package Types <{% url 'reference:package_types' %}>`_ for information about which package type to select.

Brand
_____
The brand of the product.

* A brand must be supplied.
* If there is no available brand for the product a placeholder such as "Unbranded" can be used.

Manufacturer
____________
The manufacturer of the product.

* A manufacturer must be supplied.
* If the manufacturer is unknown use the name of the supplier.


Description
___________
Full description to be used in listings.

* This is **required** for any item that will be listed online. It can be left blank and added to a product later if necessary.
* Must **not** start with the title of the product. It will be added automatically on ebay.
* Must **not** include information about **price** or **postage**.
* Do **not** use abrieviations such as "L" for length as this cannot be translated for foreign listings.
* Sentences must end with full stops.
* Proper use of capitalisation is required.
* The description can **contain** bullet points to hightlight key information but **MUST NOT** consist only of bullet ponts.

Gender
______
Gender for which the product is intended.

* This is required only for clothing items being listed on Amazon.


Amazon Bullet Points
____________________
The bullet points that will appear at the top of the Amazon listing.

* These are far more prominent than the main description. This makes it crucial that these are included.
* Each bullet point should be about one sentence long.
* Can repeat key information from the main description.
* All rules for descriptions also apply to bullet ponts.

Amazon Search Terms
___________________
Key words and phrases that people might use to find the product.

* A list of keywords and key phrases used by Amazon to match a listing to customer's searches.
* Can include alternate words and spelling.
* Search terms must be put here, **not** in the product title.


Single Product Options
______________________

Product options work differently for single items and variation products. This
information is for single items.

* Fill in any fields you feel apply to the product.
* Any fields that do not seem applicable or relevent should be left blank.
* Colour should be filled in for all products as this is required by Amazon.

Listing Variations
==================
While a single form is required to create a single item, creating a product with
variations is a two step process. The first step is the
`new variation product form <#variation_product_form>`_, which is very similar
to the new single product variation form.
This is followed by the `Variation Table <#variation_table>`_.

New Variation Product Form
__________________________
The variation product form is very similar to the single product form.
The **Barcode** field does not appear here. You will be able to add
barcodes later. All the above information about fields still applies and
can still be used as a checklist. You will notice that when listing
variation products that checkboxes appear to the right of some fields.
If there are any fields for which the required information is not the same
for **every** variation the box next to it should be checked. If the
field is optional it can be left blank, however anything you do enter will
be provided as a default for all variations. If the information in this
field will be the same for most of your variations you can enter it here
to save typing later. If the field is not optional something must be
entered. This can be the correct information for one or some of your
variations or a placeholder. For **Price**, **Purchase Price** and
**Weight** zero is a viable placeholder but another value must be
entered for all variations on the next page.

When the form is complete you will be presented with a table containing
each field you have selected for each existant variation. These fields
should be filled in in exactly the same way they otherwise would be.

The **Barcode** field will always appear here. As usual the manufactuer
barcode can be used if available, otherwise it can be left blank to use
new barcodes from our stock.

Variation Product Options
_________________________
At the bottom of the new variation product form you will see the same list
of **Product Options** as on the new single product form. Instead of a
text box you will see the options **Unused**, **Single**,
**Variable** and **Variation**.

If the field is not applicable to the product leave **Unused** selected.

**Variation** should be selected for the options that most closely
relates the the way in which the variation product varies. For instance
shoes might use **Colour** and **Size**. This will be the name next to
the drop down box(es) in listings. All existant values for each selected
option must be listed in the boxes provided. This will be used to create
the variation table on the next page. The **TAB** key can be used after
typing a variation to enter the next box.

Relevent product options can be used in the same way they are used for
single items, to add information to the listing, if they are not variation
options.

If the information is the same for every variation select **Single**.
The typed value will be applied to every variation.

If the information is **not** the same for every variation
select **Variable**. This will add this field to the table on the next page.
As with other fields a default value can be added here. There are few products
for which this is applicable. See below for an example of when it might be.

To clarify the above here are some examples:

* For a red T-Shirt that comes in a range of sizes you would select **Variation** for the **Size** option and list the sizes. Then select **Single** for the **Colour** option and type "Red". This would allow the customer to select their size and see that all the sizes come in one colour.
* For a product that comes in a range of sizes and colours you would select **Vatiation** for both **Size** and **Colour** and list the appropriate options in the applicable fields.
* For a named door plaque for which each name has a particular coloured background you would select **Variation** for **Name** and list the names, then select **Variable** for **Colour**. This would allow you to put the appropriate colour next to each name in the variation table on the next page.


The Variation Table
___________________
When the new variation product form is complete you will see the **variation table**.
This will list every possible variation for your product by combining all
the values from **Product Option** fields marked as **Variation**.
For each variation you will have a **Barcode** field as well as any
other field for which you checked the variable check box and any **Product Option**
that was marked as **Variable**.

You will also have a **Delete** checkbox.
This should be checked for any variation that does not exist or that we will
not be stocking. If there are any variations that we do not stock but are
likely to in the future do not delete them. It is far easier to create them
now and leave them out of stock than to add them later.

All the fields in the **Variation Table** should be filled out in the
same way they would in the new single product form or the new variation
product form.

Incomplete Products
___________________
When the **Variation Table** has been submitted your new Product Range
will be created and you will be taken to it's page in the inventory.
However it will likey not yet be complete as variations are created in
the background. This will happen even for single products. If you refresh
the page you will see variations appearing. When all the variations have appeared
and the page no longer says **INCOMPLETE** your product will have been
successfully created. It is possible an error, in this case the product will
remain **INCOMPLETE**. Please allow some time for it to complete before
acting on this. Products with more variations will take longer to create
and Cloud Commerce does not always operate at it's full capacity. If you are
sure that an error has occured the product must be deleted and recreated.
