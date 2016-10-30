# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Genweb2 Ltd
#    Copyright 2016 Genweb2 Ltd
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
#    You should have received a copy of the Genweb2 Ltd
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

#--------------- Configuration Setup----------------------
#    Create a Picking type (Type of Operation) where name will be "Stock Reservation"
#    go to setting menu and click warehouse menu. 
#    checked 
    #    - Manage multiple locations and warehouses
    #    - Manage advanced routes for your warehouse
    #    - Track lots or serial numbers
    #    - Expiry date on serial numbers
#    Then go to warehouse menu -> configuration menu->click warehouse->select warehouse
#    ->click Edit Btn
# go to Tab - Technical Information -> select - Stock Analytic Reservation Location
##############################################################################


{'name': 'Stock Reservation',
 'summary': 'Stock reservations on products',
 'version': '8.0.0.2.0',
 'author': 'Genweb2 Limited',
 'category': 'Warehouse',
 'license': 'AGPL-3',
 'complexity': 'normal',
 'images': [],
 'website': "http://www.genweb2.com",
 'depends': ['stock'
             ],
 'demo': [],
 'data': [
          'security/security.xml',
          'security/ir.model.access.csv',
          'view/inherited_warehouse_views.xml',
          'view/stock_reservation.xml',
          'view/stock_de_allocation.xml',
          'view/stock_re_allocation.xml',
          'wizard/product_reservation_status_wizard_views.xml',
          'report/product_reservation_status_report.xml',
          'wizard/epo_reservation_status_wizard_views.xml',
          'report/epo_reservation_status_report.xml'
          ],
 'auto_install': False,
 'installable': True,
 }
