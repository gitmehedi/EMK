# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Smile (<http://www.smile.fr>).
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
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "OPA Date Type Search Between Start and End Datetime",
    "version": "0.1",
    "depends": ['base'],
    "author": "git.mehedi",
    "description": """
Date Type Search Between Start and End Datetime
=======================================

    """,
    "summary": "",
    "website": "https://www.angrybyte.wordpress.com",
    "category": 'Tools',
    "sequence": 20,
    "data": [
        'views/webclient_templates.xml',
    ],
    "qweb": [
        'static/src/xml/base.xml',
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
