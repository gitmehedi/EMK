# -*- coding: utf-8 -*-
##############################################################################
#
#    Ingenieria ADHOC - ADHOC SA
#    https://launchpad.net/~ingenieria-adhoc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{   
    'name': 'Stock Extend',
    'author':  'Stock Extend New',
    'website': 'www.genweb2.com',
    'category': 'Warehouse',
    'data': [
             'security/security.xml',
             #'security/ir.model.access.csv',
            'wizard/product_return_line_wizard_views.xml',
            'views/inherited_product_return_views.xml',
            'views/stock_goods_price_views.xml',
            'views/stock_transfer_menu_view.xml',
            'views/inherited_stock_picking_type_views.xml',
            'views/stock_issue_view.xml',
            'views/stock_return_view.xml',
            'views/stock_transfer_view.xml',
            'wizard/stock_report_wizard_view.xml',
            'report/absence_report_pdf.xml',
            'report/absence_report_view.xml',
            'views/inherited_stock_inventory_line_views.xml',
            'views/stock_receive_view.xml',
            'views/inherited_stock_picking_views.xml'
#             'wizard/confirmation_wizard_views.xml'
             ],
    'depends': ['stock','purchase'],
    'description': '''
''',
    'installable': True,
    'version': '0.1',
}
