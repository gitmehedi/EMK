# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <contact@elico-corp.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Stock Location Reports',
    'version': '1.1',
    'category': 'Stock',
    'sequence': 19,
    'summary': 'Stock Location Reports',
    'description': """
Stock Location Reports
==================================================
Add Three new reports for warehouse management:
    * stock location reports
    * stock location overall reports
    * stock inventory reports
    """,
    'author': 'Odoo Bangladesh',
    'website': 'http://www.binaryquest.com',
    'images' : [],
    'depends': ['stock','product_stock_type','report_webkit'],
    'data': ['reports.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
