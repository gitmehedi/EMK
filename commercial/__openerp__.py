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
    'name': 'Commercial',
    'summary': """Lakshma Commercial Module""",
    'version': '0.1',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'description': '''Commercial Module:
     Commercial department works for resolving the issues where Buyers and Sellers are from different countries
     and they needs to be ensured about the product and payment. Commercial (Export & Import) department handles all the internationally
     accepted procedures to make sure successful international sales and purchase.''',
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'wizard/master_lc_wizard_views.xml',
             'wizard/sales_contract_conversion_wizard_views.xml',
             'views/root_menu.xml',
             'views/inherited_account_payment_term_views.xml',
             'views/inherited_bank_views.xml',
             'views/commercial_term_views.xml',
             'views/notify_party_views.xml',
             'views/port_views.xml',
             'views/delivery_to_views.xml',
             'views/export_invoice_views.xml',
             'views/import_invoice_views.xml',
             'views/sales_contract_views.xml',
             'views/export_invoice_views.xml',
             'views/export_invoice_receive_views.xml',
             'views/export_invoice_realization_views.xml',
             'views/tt_receive_views.xml',
             'views/tt_payment_views.xml',
             'views/import_payment_views.xml',
             'views/master_lc_views.xml',
             'views/proforma_invoice_views.xml',
             'views/bb_import_lc_views.xml',
             'views/lc_amendment_views.xml',
             'views/lc_amendment_new_views.xml',

             ],
    'depends': ['account','stock'],
    'installable': True,
    'application': True,
}
