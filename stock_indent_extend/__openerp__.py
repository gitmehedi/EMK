# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2014 Elico Corp. All Rights Reserved.
#    Augustin Cisterne-Kaas <augustin.cisterne-kaas@elico-corp.com>
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
    'name': 'Stock Indent Extend',
    'version': '0.4',
    'category': 'stock',
    'depends': ['stock_indent','purchase_requisition'],
    'author': 'Odoo Bangladesh',
    'license': 'AGPL-3',
    'website': 'https://www.binaryquest.com',
    'description': """
        
    """,
    'images': [],
    'data': [
        'security/ir.model.access.csv',
        'indent_data.xml',
        'indent_view.xml'],
    'installable': True,
    'application': False,
}
