# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2017-Today Hiren Patel 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Image In Sales Order, Purchase Orders And Invoice Report',
    'version': '0.1',
    'category': 'sales',
    'summary': 'This module used to show image in sales order , purchase order and invoice report for product.',
    'description': """
        In this module you can show image in sales order , purchase order and invoice report for product.
""",
    'author': 'Hiren Patel',
    'depends': ['base','sale','purchase','account'],
    'data': [
             'views/inherit_sale_report.xml',
             'views/inherit_invoice_report.xml',
            'views/inherit_purchase_report.xml',
            'views/inherit_purchase_rfq_report.xml'
    ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
