Analytic Structure
==================

What is it ?
------------

The module provides a way of defining dynamic relationships between objects.
We use the following concepts:

- Dimensions, represented by ``analytic.dimension``
- Structure, represented by ``analytic.structure``
- Codes, represented by ``analytic.code``

These objects can be seen in ``Technical >> Analytics`` under ``Settings``.

Dimensions act as labels for data points that can be used to perform analyses.
Structures define mappings between models and dimensions, they can be configured through the *Settings* menu.
Codes are the objects that are bound to instances of dimension models, they allow us to define dynamic relationships.

Example: Your company has several product lines and you would like to analyse expenses related to these product lines in your accounting system.
You would then define a *product line* dimension and some structures that bind the *product line* dimension to ``product.product``, ``invoice.line``, ``account.move.line`` models.

How does it work ?
------------------

Analytic Structure provides the ``MetaAnalytic`` metaclass (see MetaAnalytic_) that injects new behaviors into Odoo models.
Dimension models and models that define analytic fields must use ``MetaAnalytic`` and define various class attributes.

A dimension model is declared with the ``_dimension`` attribute (see AnalyticDimensions_).
The metaclass automatically creates ``analytic.dimension`` records for each dimension model.
Once a model is declared as a dimension, every new instance will automatically create a new ``analytic.code`` record that points to the relevant ``analytic.dimension`` record.

A model that is declared with the ``_analytic`` attribute (see AnalyticFields_) can reference dimension objects.
The ``MetaAnalytic`` will automatically create a number of M2O fields that point to analytic codes.
The number of fields that will be added depends on the configuration (See ConfigureAnalyticFields_).
They are named with a predefined prefix and a number or slot eg. ``a1_id``, ``a2_id``, ``a3_id``, ...

These analytic fields will be displayed in views with the names of the dimensions they point to thanks to view manipulation magic.

Schematic::

 | AnalyticModel     Code        DimensionModel     Dimension
 | -----             ----        --------------     ---------
 | an_id ----------> id,name <-- analytic_code_id
 |
 |                   n_id    ---------------------> id,name

The relationship between a model and a dimension is configured by *analytic structures*.
Structure define how models point to dimensions and what analytic field to use.

Example: You have a dimension ``D`` you wish to bind to model ``A``.
You would create an ``analytic.structure`` record for ``A`` that references ``D`` through the ``Analysis 1`` slot.
This would allow you to use the ``a1_id`` field (assuming the default prefix is used) to reference ``D`` records.

Integrity of analytic codes
---------------------------

You cannot delete analytic codes that are referenced by objects.
The goal of this constraint is to ensure the integrity of your analyses.

.. _ConfigureAnalyticFields:

Configure your OpenERP server for analytic fields
-------------------------------------------------

In your OpenERP server's configuration file, you can set several optional
parameters related to the analytic module.::

 [analytic]
 key = value ...


Those options must be grouped under the [analytic] category. If the category
doesn't exist, add it to your configuration file.

key (default value): description

analytic_size (5): define the maximum number of analytic dimensions
that can be associated with a model.

translate (False): enable or disable the translation of field values on
analytic dimensions (name) and codes (name and description).

.. _MetaAnalytic:

Add the MetaAnalytic metaclass to a model
-----------------------------------------

At the beginning of the source file, import the MetaAnalytic metaclass:

from openerp.addons.analytic_structure.MetaAnalytic import MetaAnalytic


Inside your Model class, define MetaAnalytic to be used as metaclass:

.. code:: python

 __metaclass__ = MetaAnalytic

.. _AnalyticFields:

Add analytic fields to a model
------------------------------

First of all, make sure you are using the MetaAnalytic metaclass.
Then, add the _analytic attribute to your class, using the following syntax.


Use the analytic fields associated with the model:

.. code:: python

 _analytic = True


Use analytic fields associated with another model:

.. code:: python

 _analytic = 'account_move_line'


Use several analytic field structures, associated with different prefixes:

.. code:: python

 _analytic = {
     'a': 'account_asset_asset',
     't': 'account_move_line',
 }

Add analytic fields to a view
-----------------------------

Analytic fields can be added to the view individually, like any other field:

.. code:: xml

 <field name="a1_id" />

'a' is the prefix associated with the structure. By default, it is 'a'.
'1' is the dimension's ordering as defined by the analytic structure.


You can also use a field named 'analytic_dimensions' to insert every analytic field within a given structure
(defined by its prefix) that wasn't explicitly placed in the view. This field is automatically generated when
you call the Metaclass

.. code:: xml

 <field name="analytic_dimensions" required="1" prefix="t" />

The prefix can be omitted for a structure that uses the default prefix 'a'.
Any other attribute will be propagated to the analytic fields.


Warning: analytic fields should generally not be used inside nested sub-views.
If possible, create a separate record and use the context to specify the view:

.. code:: xml

 <field name="order_line" colspan="4" nolabel="1" context="{
     'form_view_ref' : 'module.view_id',
     'tree_view_ref' : 'module.view_id'
 }"/>


Advanced: Para-analytic fields
------------------------------

Para-analytic fields are a more advanced feature of analytic_structure.
They differ from ordinary analytics fields in two ways:

- They are entirely configurable, meaning that you decide their type and parameters
- They don't have predefined behaviors

Para-analytic fields are defined in with the ``_para_analytic`` attribute.
For each entry in ``_para_analytic`` the ``MetaAnalytic`` metaclass will create a number fields.
The number of fields depend on ``analytic_size`` in the configuration file (see ConfigureAnalyticFields_).

Each entry is key-value pair of a dict where the key is a (prefix, suffix) tuple and the value a dict containing the following:

``model`` the name of the referenced dimension model (doesn't do anything special)

``type`` a field class, the field type to use

``default`` default value for the fields

``args`` list of arguments to inject in ``type`` constructor

``kwargs`` dict of keyword arguments to inject in ``type`` constructor.

Here is declaration that will create fields with the names ``a1_b``, ``a2_b``, ``a3_b``, ...

.. code:: python

 from openerp import fields

 # ...

 # Inside a class
 _para_analytic = {
    ('a', 'b'): {
        'model': 'account_move_line',
        'type': fields.Boolean,
        'default': True,
        'args': ("field is optional"),
        'kwargs': dict(required=True),
    }
 }

Validation hook for analytic fields
-----------------------------------

Models that define the ``_analytic`` attribute can override the ``_validate_analytic_fields`` to perform validation on analytic fields.
The method is called every time the model's ``create`` and ``write`` methods are called.

Odoo 8.0 Method signature:

.. code::python

 def validate_analytic_fields(self, analytic):

where ``analytic`` is a dict containing in the same information given in the ``_analytic`` class attribute, in the expanded form.

The method signals failure by raising an exception, just like methods decorated with ``api.constrains()``.

.. _AnalyticDimensions:

Bind an analytic dimension to a model
-------------------------------------

First of all, make sure you are using the MetaAnalytic metaclass.
Then, add the _dimension attribute to your class, using the following syntax.


Bind the model to an analytic dimension named after the model, using default values:

.. code:: python

 _dimension = True


Bind the model to an analytic dimension with a specified name, using default values:

.. code:: python

 _dimension = 'Funding Source'


Bind the model to an analytic dimension, using either custom or default values:

.. code:: python

 _dimension = {
     'name': 'School',
     'column': 'analytic_code_id',
     'ref_id': 'school_analytic_dimension',
     'ref_module': 'my_module',
     'sync_parent': False,
     'rel_description': True,
     'rel_active': (u"Active", 'active_code'),
     'use_inherits': False,
     'use_code_name_methods': False,
 }


key (default value): description

``name`` (= ``_description`` or ``_name``): The name of the analytic dimension.
This name is only used when creating the dimension in the database.

column (analytic_id): The field that links each record to an analytic code.

``ref_id`` (= ``_name`` + ``analytic_dimension_id``): The external ID that will
be used by the analytic dimension. By setting this value, you can allow two
models to use the same dimension, or a model to use an already existing one.

``ref_module`` (empty string): The name of the module associated with the dimension
record. Change this value in order to use a dimension defined in a data file.

``sync_parent`` (``False``): Controls the synchronization of the codes' parent-child
hierarchy with that of the model. When using an inherited, renamed parent field,
you must give the parent field name rather than simply ``True``.

``use_inherits`` (special): Determines whether the analytic codes should be bound
to the records by inheritance, or through a simple many2one field.
Inheritance allows for better synchronization, but can only be used if there
are no duplicate fields between the two objects.
The default value is ``True`` if the model has no 'name' and 'code_parent_id' field
as well as no inheritance of any kind, and ``False`` otherwise. If the object has
inheritances that do not cause conflicts, you can set it to ``True``.

``rel_active`` (``False``): Create a related field in the model, targeting the
analytic code field 'active' and with an appropriate store parameter.
This is useful when the model doesn't inherit analytic_code and/or when it
already has a field named 'active'.
Can take a pair of string values: (field label, field name).
If given a string, the default field name 'active' will be used.
If given ``True``, the default field label 'Active' will also be used.

``rel_description`` (``False``): Same as rel_active for the code field 'description'.
If given a string, the default field name 'description' will be used.
If given ``True``, the default field label 'Description' will also be used.

``use_code_name_methods`` (``False``): Set to ``True`` in order to override the methods
name_get and name_search, using those of analytic code.
This allows the analytic code's description to be displayed (and searched)
along with the entry's name in many2one fields targeting the model.



Active / View type / Disabled in my company
-------------------------------------------

Differences between the various "active" fields:

- Active: Determines whether an analytic code is in the referential.
- View type: Determines whether an analytic code is not selectable (but still
in the referential).
- Disabled per company: Determines whether an analytic code is disabled for the
current company.

