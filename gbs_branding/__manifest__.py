# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

{
    'name': 'GBS Branding',
    'version': '1.0.0',
    'category': 'Logo',
    "sequence": 1,
    'summary': 'Branding',
    'complexity': "easy",
    "author": "Genweb2 Limited",
    "website": "http://www.genweb2.com",
    'depends': ['web'],
    'data': [
        'views/openeducat_template.xml',
        #'views/homepage_template.xml',
    ],
    'qweb': [
        'static/src/xml/base.xml'
    ],
    'js': [
        'static/src/js/chrome.js'
    ],
    'images': [
        'static/description/gbs_favicon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
