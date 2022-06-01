# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018-BroadTech IT Solutions (<http://www.broadtech-innovations.com/>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

{
    'name': 'Timesheet Analysis Report',
    'version': '0.1',
    'category': 'Generic Modules/Human Resources',
    'summary': '"Timesheet Analysis Report"',
    'description': """
      Timesheet Analysis Report
    """,
    'author': 'BroadTech IT Solutions Pvt Ltd',
    'website': 'http://www.broadtech-innovations.com/',
    'depends': ['hr_timesheet','hr','project'],
    'license':'LGPL-3',
    'data': [
        'wizard/bt_timesheet_analyis_report.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': True,
    'qweb': [
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
