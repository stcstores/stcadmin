
.. contents:: Table of Contents

*************
The Inventory
*************

The inventory allows you to create, find and edit products within the Cloud
Commerce inventory. It can be accessed by opening http://stcadmin.stcstores.co.uk
and navigating to `Inventory <{% url 'inventory:product_search' %}>`_.


Creating Products
=================
See `Product Creation <{% url 'reference:product_creation' %}>`_.


Finding Products
================
To find an existing product navigate to
`Product Search <{% url 'inventory:product_search' %}>`_. This page allows you
to search for products in two ways, **Basic Search** and **Advanced Search**.
The type of search is selected using the radio buttons in the **Search Type**
field. You will notice that the search form changes when moving between them.

Basic Search
____________
The **Basic Search** is faster and easier to use than the **Advanced Search**
and should always be used unless a feature of the **Advanced Search** is
specificaly required. To perform a **Basic Search** click on the appropriate
radio button in the **Search Type** field (it is selected by default). This
will return a list of all products for which the search text is present in
any of the following locations:

* Range Title
* Product SKU
* Supplier
* Supplier SKU
* Colour
* Size
* Design
* Brand
* Manufacturer
* Any other **Product Option**

.. note::
    The search will match the SKU of a **Product** (variation) but **not** the
    SKU of the **Product Range**.

The time taken to complete a search depends on the number of results. if you are
more specific with your search text fewer products will match your search and
so the search will complete more quickely.

Hide End of Line
----------------

The **Hide End of Line** field is present in both the **Basic Search** and
**Advanced Search**. This adds or removes products from the search results
based on the `End of Line`_ setting of the **Product Range**. It has three
options:

* **Exclude** (default): *Remove* ranges marked **End of Line** from search results.
* **Include**: *Include* ranges marked **End of Line** in the search results.
* **Exclusive**: *Only include* ranges marked **End of Line** in the search results.

Advanced Search
_______________

The **Advanced Search** works in a similar way to the **Basic Search**, with
the search text going the the **Search Text** field, with some extra options.

Hide Out of Stock
-----------------
Out of stock products can be removed from the search result by checking the
**Hide out of stock** checkbox.

Product Option
--------------
This field allows you to limit the search results to products which have a
particular **Product Option** with a particular value. To do this select
a **Product Option** from the drop down box. This will cause a second drop
down box to appear with a list of all the existant values for the selected
**Product Option**, select an option from this list. It can be usefull to
leave the **Search Text** field blank and use the **Product Option** field
to get a complete list of **all** the products for which the **Product Option**
matches a given value. For instance you could select the **Supplier** product
option and choose a supplier to get a list of all products from that supplier.

Search Results
______________
After performing either a **Basic Search** or an **Advanced Search** you will
be presented with a list of **Product Ranges** for which any **Product**
matches the search criteria. This is presented as a table containing the
Range's SKU and title, some shortcuts to update the range and an option to
show the Range's Products.

The title is a link to the `Range Page`_ for this **Product Range**.

The purpose of each shortcut can be found by hovering over it's button, and
are as follows:

* **V** (**Variations**): The `Variations Page`_.
* **D** (**Descriptions**): The `Description Page`_.
* **L** (**Locations**): The `Location Page`_.
* **I** (**Images**): The `Images Page`_.
* **P** (**Price Calculator**): The `Price Calculator`_.
* **C** (**Show on Cloud Commerce**): Opens the **Product Range** page on Cloud Commerce for this product.

Showing products for a range can be toggled by clicking on [[show]] in the last
column of the table. This will then be replaced with a list of the ranges products.
This will include the products SKU, full title and stock level. The stock
level can be updated from here by changing the displayed stock level and clicking
on "Update Stock Level". The products can be hidden again by clicking [[hide]]
Displaying products for all ranges can be toggled using the "Show/hide all"
button in the table header.


Range Page
==========
The **Range Page** shows details of a given **Product Range**. From here you
can update any attribute of the **Range** and view all of it's **Products**
(variations).

From here you can access `Variations <#variations-page>`_,
`Descriptions <#description-page>`_, `Locations <#location-page>`_,
`Image <#image-page>`_, `Price Calculator`_ and `Barcode Labels`_ for the range as well as
the `Product Page`_ for all of it's **Products**. You can click on the title
of a **Product** to go to it's **Product Page**.

It includes a table of **Products**, displaying the SKU and title for each
as well as allowing you to update the stock level by entering a new figure
and clicking "Update Stock Level".

End of Line
___________
From the **Range Page** you can mark a Range as **End of Line**. This should be
done for any Range for which every **Product** is out of stock an unlikely
to be re-stocked. Ranges marked **End of Line** will be hidden from most
searches.

To mark a Range as **End of Line**, check the **End of Line** checkbox and
click "Update".

.. note::
    Old Ranges and Products should **never** be deleted, they should be marked
    as **END of Line** instead. Products can only be deleted if they where
    created erroneously and have not been listed on **any** channel.


Product Page
============
The **Product Page** shows details of a given **Product** (variation). This page
allows you to update various attribute of the **Product**.

From here you can
update:

* `VAT Rate <{% url 'reference:product_creation' %}#vat-rate>`_.
* `Price <{% url 'reference:product_creation' %}#price>`_.
* `Location <{% url 'reference:product_creation' %}#location>`_.
* `Weight <{% url 'reference:product_creation' %}#weight>`_.
* `Dimensions (Height, Width and Length) <{% url 'reference:product_creation' %}#dimensions-height-width-and-length>`_.
* `Package Type <{% url 'reference:package_types' %}>`_.
* `Supplier SKU <{% url 'reference:product_creation' %}#supplier-sku>`_.
* `Product Options <{% url 'reference:product_creation' %}#single_product_options>`_.

For more information on these, consult the
`Fields <{% url 'reference:product_creation'}#fields>`_ section of the
`Product Creation Documentation <{% url 'reference:product_creation' %}>`_


Variations Page
===============
The **Variation Page** allows you to update various attributes of every
**Product** in a the given **Product Range**.

From here you can update:

* `VAT Rate <{% url 'reference:product_creation' %}#vat-rate>`_.
* `Price <{% url 'reference:product_creation' %}#price>`_.
* `Weight <{% url 'reference:product_creation' %}#weight>`_.

Any **Product Option** for which every **Product** does not share the same value
will also appear here and can be updated.

.. note::
    The loading time for this page depends on the number of **Products** in the
    **Range**. **Ranges** with a lot of variations may take some time to load.


Description Page
=================
From the **Description Page** you can update the
`Description <{% url 'reference:product_creation' %}#description>`_,
`Amazon Bullet Points <{% url 'reference:product_creation' %}#amazon-bullet-points>`_,
and `Amazon Search Terms <{% url 'reference:product_creation' %}#amazon-search-terms>`_.


Location Page
==============
The **Location Page** allows you to change the **Location** of each **Product**
in a **Range**. The **Warehouse** (department) in which the location is
located must be set in the **Warehouse** column. The **Bays** (box number, etc)
within the **Warehouse** can be listed for each **Product** in the **Bays**
column. If the product does not have a specific **Bay**, the **Bay** name
should match the **Warehouse**. The main picking location should always be
listed first.

.. note::
    A product can be in multiple **Bays** but only one **Warehouse**.

.. note::
    The loading time for this page depends on the number of **Products** in the
    **Range**. **Ranges** with a lot of variations may take some time to load.

Images Page
===========
The **Images Page** allows you to view, upload and re-order **Product Images**
in **Cloud Commerce** and to them in STCAdmin.

.. note::
    The loading time for this page depends on the number of **Products** in the
    **Range**. **Ranges** with a lot of variations may take some time to load.

Cloud Commerce Images
_____________________
**Cloud Commerce Images** are the **Product Images** saved in Cloud Commerce.
They will be added to listings for the product. You will see a table containing
each variation for the selected **Product Range**. To add an image to a
particular variation select the checkbox in it's row in the table, then click
the **Browse** button next to *Cloud Commerce Images* above. This will create an
open file dialog box allowing you to select one or more images. To add an image
to multiple variations, select multiple checkboxes in the image table. All
variations wit a particular *Size*, *Colour* or *Design* **Product Option Value**
can be selected using the buttons that will appear above the table if they
are applicable to the current **Product Range**.

When a variation has a **Product Image** associated with it it will appear to
the right of it in the table. Beneath the image will be it's **Image ID**, this
doubles as a link to the original image file. By clicking on this you can view
the image full size and download it by right clicking on it and selecting "**Save
Image As...**". Underneath this are buttons to re-order the image left or right
and a red cross button to delete it.

STC Admin Images
________________
**STC Admin Images** are not uploaded to Cloud Commerce and will **not** be added
to listings. This can be usefull if images need to be stored without adding to
listings or for eBay main images that contain multiple variations and therefore
do not apply to any particular variation. They can be added by clicking the
**Browse** button next to *STC Admin Images*. When a **Product Range** has
STC Admin images they will appear under the **Product Image Table**. They can
be viewed and saved by clicking on them and deleted by clicking the red cross
button under them.

Price Calculator
================
The **Price Calculator** takes product information and calculates the profit
from a sale in a given country at a given price. To calculate the profit for
an existing **Product** go to it's `Range Page`_ and click on the
"*Price Calculator*" button. You can then select the country and input the sale
price to see the sale profit. Alternatively you can select "*Price Calculator*"
from the inventory navigation bar. This will give you a price calculator for
which you can enter any product details. This can be usefull for products that
are not yet in the inventory.

Barcode Labels
==============
The **Barcode Labels** page allows you to product barcode labels for **Products**.
To do this you must select the number of labels required for each **Product** in
the **Range**. The quantity will default to the current stock level of the
*Product*. If no labels are required for a particular **Product** set the
quantity to zero. By selecting **Products** with the checkboxes the same quantity
can be applied to multiple **Products** by putting the required quantity in the
box above the list of **Products** and clicking "*Update Selected*". To produce
the barcodes click "*Product Barcodes*". This will generate a *.pdf* file of
barcode labels which can then be printed.


Common Tasks
============

Updating Stock Levels
_____________________
Ths easiest method to update a product's stock level is to use the
`Product Search`_ to find the necessary **Product Range**. From the search
results click the [[Show]] button next the the **Product Range** to show it's
variations. Next to the **Product**'s title and SKU the current **Stock Level**
will be displayed. By changing this number and clicking the "*Update Stock Level*"
button next to it the **Stock Level** can be altered. When this is done a tick
will appear next to the button. If an error occurs for any reason a cross will
appear instead.

Changing a Product's Location
_____________________________
To update the **Location** of a **Product** use the `Product Search`_ to find
the necessary **Product Range**, then access the `Location Page`_ by clicking
on the "*L*" button or clicking on the **Product's** title to access the
`Range Page`_ and clicking on the "*Locations*" button. From here you can select
a **Warehouse** and list the appropriate **Bays** for each **Product**. When
the necessary changes are complete, click the "*Update Locations*" button. If
only one **Product** needs updating this can be done from the `Product Page`_.
This page will load much faster than the `Location Page`_.
