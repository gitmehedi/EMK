# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
    'name' : 'Custom Reports of CSL', 
    'version' : '0.1',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com.bd',
    'category' : 'Warehouse Management',
    'depends' : ['stock'],
    'description': """
    
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    
    
    
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    
    """,
    'data': ['security/ir.model.access.csv',
             'views/inherited_product_template_views.xml',
             'wizard/print_report_view.xml',
             'report/stock_inventory_report.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: