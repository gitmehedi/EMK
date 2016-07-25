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
    'name': 'Journal Template',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Accounting & Finance',
    'data': [
             'views/acc_journal_template_view.xml',
             'wizard/acc_journal_wizard_views.xml',
             'views/inherited_account_move_views.xml',

             ],
    'depends': ['account'],
    'description': '''
	''',
    'installable': True,
    'version': '0.1',
}
