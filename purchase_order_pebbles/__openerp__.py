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
    'name': 'Purchase Order Pebbles',
    'author':  'Genweb2',
    'website': 'www.genweb2.com',
    'category': 'Purchase',
    'data': [
            'security/security.xml',
             'security/ir.model.access.csv',
            'views/root_menu.xml',
            'views/inherited_purchase_order_line_views.xml',
            'views/goods_receive_matrix_views.xml'
             ],
    'depends': ['base', 'product', 'point_of_sale','stock', 'purchase', 'web_widget_goods_recevie_matrix'],
    'description': '''
''',
    'installable': True,
    'application': True,
    'auto_install': False,
    'version': '0.1',
}
