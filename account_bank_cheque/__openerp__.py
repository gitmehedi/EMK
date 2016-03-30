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
    'name': 'Post Dated Cheque Management',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting',
    'data': [
             #'security/security.xml',
             #'security/ir.model.access.csv',
             'views/root_menu.xml',
             'views/account_postdated_cheque.xml',
             'views/account_postdated_bank.xml',
             'wizard/cheque_search_popup.xml',
             ],
    'depends': ['base',],
    'description': '''
''',
    'installable': True,
    'version': '0.1',
}
