{
    'name': 'Indent Management',
    'version': '10.0.1',
    'category': 'Warehouse Management',
    'depends': ['stock',
                'account',
                'purchase_requisition',
                'ir_sequence_operating_unit',
                'indent_type',
                'gbs_res_users'],
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'license': 'AGPL-3',
    'complexity': "normal",
    'description': """
Indent Management
===================
Usually big companies set-up and maintain internal requisition to be raised by Engineer, Plant Managers or Authorised Employees. Using Indent Management you can control the purchase and issue of material to employees within company warehouse.

- Purchase Indents
- Store purchase
- Capital Purchase
- Repairing Indents
- Project Costing
- Valuation
- etc.

Purchase Indents
++++++++++++++++++
When there is a need of specific materials or services, authorized employees or managers will create a Purchase Indent. He can specify required date, whether the indent is for store or capital, the urgency of materials etc. on indent.

While selecting the product, the system will automatically set the procure method based on the quantity on hand for the product. Once the indent is approved, an internal move has been generated. A purchase order will also be generated if the products are not in stock and to be purchased.


Repairing Indents
++++++++++++++++++
A store manager or will create a repairing indent when the product is needed to be sent for repairing. In case of repairing indent you will be able to select product to be repaired and service for repairing of the product.

A purchase order is generated for the service taken for the supplier who repairs the product, and an internal move has been created for the product to be moved for repairing.
    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'report/stock_indent.xml',
        'data/stock_indent_data.xml',
        'data/stock_indent_sequence.xml',
        'views/stock_location_view.xml',
        'views/stock_indent_view.xml',
        'views/stock_picking_views.xml',
        ],
    'installable': True,
    'application': False,
}
