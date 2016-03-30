# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name' : 'Product Category Extension',
    'version' : '0.1.1',
    'author' : 'Binary Quest Limited',
    'sequence': 120,
    'category': 'Warehouse Management',
    'website' : 'http://www.binaryquest.com',
    'summary' : 'Product Category Extension',
    'description' : """
Product Category Extension
===================================================

* A code in the product category will be added!
* The code of the product category  must be unique!

""",
    'depends' : ['product'],
    'data' : ['security/security.xml',
              'product_category_view.xml'],
    'installable' : True,
    'application' : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

