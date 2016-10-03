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
    'name': 'Merchandising',
    'author':  'Genweb2 Limited',
    'website': 'www.genweb2.com',
    'category': 'Garments & Apparels',
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'views/root_menu.xml',
             'views/assets.xml',
             'views/res_season_views.xml',
             'views/res_region_views.xml',
             'views/product_size_views.xml',
             'views/product_size_line_views.xml',
             'views/product_size_group_views.xml',
             'wizard/product_style_amendment_wizard_views.xml',
             'wizard/bill_of_matetials_wizard_views.xml',
             'views/product_style_views.xml',
             'views/inherited_res_buyer_views.xml',
             'views/account_fiscal_year_views.xml',
             'views/product_unit_of_measurement.xml',
             'views/merchandising_dept_views.xml',
             'views/inherited_res_courier_views.xml',
             'wizard/sample_development_request_wizard_views.xml',
             'wizard/sample_development_receive_wizard_views.xml',
             'wizard/sample_development_submission_wizard_views.xml',
             'views/sample_development_request_views.xml',
             'views/sample_development_receive_views.xml',
             'views/sample_development_submission_views.xml',
             'views/sample_requisition_views.xml',
             'views/product_style_sequence.xml',
             'wizard/material_consumption_wizard_views.xml',
             'views/material_consumption_view.xml',
             'views/bom_consumption_view.xml',
             'wizard/quotation_submission_wizard_views.xml',
             'views/product_costing_views.xml',
             'views/quotation_submission_views.xml',
             'views/quotation_request_views.xml',
             'workflow/quotation_request_workflow.xml',
             'workflow/sample_requisition_workflow.xml',
             'views/inherited_product_template_views.xml',
             'views/inherited_res_country_views.xml',
             'views/delivery_term_views.xml',
             'views/buyer_work_order_views.xml',
             'views/shipping_destination.xml',
#             'views/inherited_pos_template.xml',
             'views/inherited_res_users_views.xml',
             'views/inherited_product_attribute.xml',
             ],
    'depends': ['account', 'web_tree_image', 'sale'],
    'description': '''
''',
    'installable': True,
    'version': '0.1',
}
