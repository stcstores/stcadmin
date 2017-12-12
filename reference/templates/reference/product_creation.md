{% load markup_tags %}
{% filter apply_markup:"restructuredtext" %}

# Creating Productcs on STCAdmin#
To begin creating a product navigate to http://stcadmin.stcstores.co.uk and go to the [Inventory](http://stcadmin.stcstores.co.uk/inventory) section and select [New Product](http://stcadmin.stcstores.co.uk/inventory/new_product).

If your product has variations select
[Variation Product](http://stcadmin.stcstores.co.uk/inventory/new_variation_product/) otherwise choose [Single Product](http://stcadmin.stcstores.co.uk/inventory/new_single_product/).

## The New Product Form
The new product form is where you put information about your product. This is the only step when creating single products, however variation products work slightly differently and also require the [Variation Table](#variation_table) to be filled in. For more information set [Variation Listings](#variation_listings).

The new product form is colour coded:
* Fields with a **White background** are **optional** and can be left blank if they are not applicable or are to be filled in later.
* Fields witha **Grey background** are **required** for all products and must always be filled in.
* Fields with a **Blue background** are for **Product Options**. They work differently for [single products](#single_product_options) and [variation products](#variation_product_options).

## Fields
The following is a list of fields that appear in the new product forms. This can be used as a checklist when creating products.

### Title
The name of the **Product Range** to be created.
**Note:** All products are part of a **Product Range** even if they do not include variatons.
* The title should *not* contain key words. This includes colours, sizes etc.
* This title is for internal reference and will not necessarily be used for listings on eBay or Amazon. It will, however, be used on our website.
* It must make sense gramatically and not include dashes.
* It must use proper **title case**. (The first letter of every word should be capital except for connective words such as "and" or "the" unless they are the first word of the title.)

{% endfilter %}
