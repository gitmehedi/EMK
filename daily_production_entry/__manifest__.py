{
    'name': 'MRP Daily Production',
    'author': 'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'MRP Daily Production',
    'version':'1.0',
    'depends': [
        'sale',
        'product_sales_pricelist'
    ],
    'data': [
        'views/mrp_daily_production_view.xml',
    ],
    
    'summary': 'MRP Daily Production Information',
    'description': 
    """This module is discribing all MRP daily production information""",
    'installable': True,
    'application': True,
}