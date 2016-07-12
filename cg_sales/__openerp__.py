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
    'name' : 'Sales', 
    'version' : '0.1.5',
    'author': 'Odoo Bangladesh',
    'website': 'www.odoo.com',
    'category' : 'Sales',
    'depends' : ['base', 'account',
                 'stock',
                 'sale',
                 'sale_promotions_extend',
                 'extend_partner_ledger'],
    'description': """
    
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    
    Discount features that will cover
    1) Invoice Discount
    2) Special Discount
    
    = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
    
    """,
    'data': ['security/security.xml',
             'security/ir.model.access.csv',
             'views/base_menu.xml',
             'views/product.xml',
             'views/sale_area_view.xml',
             'views/res_partner_view.xml',
             'views/partner_inherit_view.xml',
             'wizard/customer_creditlimit_assign_by_partners.xml',
             'views/limit_view.xml',
             'views/res_users_view.xml',
             'views/sale_order_view.xml',
             'views/indent_inherit_view.xml',
             'report/report_invoice.xml',
             'report/report_partnerledger.xml',
             'views/account_inherit_view.xml',
             'views/purchase_order_inherit_view.xml',
             ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: