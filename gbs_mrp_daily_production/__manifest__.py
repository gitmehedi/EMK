{
    'name': "GBS MRP DAILY PRODUCTION",
    'author': 'Genweb2',
    'version': '10.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'MRP Daily Production Process',
    'description': "MRP Daily Production Process",

    'depends': [
        'mrp',
        'base',
        'gbs_mrp_section',
        'product',
    ],
    'data': [
        #'security/ir.model.access.csv',
        'views/daily_production.xml',
    ],
    'installable': True,
    'application': False,
}