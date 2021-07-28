# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Create Issue from Project Task',
    'version': '10.0.0.1',
    'author': 'BrowseInfo',
    'category':'Project',
    'price': '15',
    'currency': "EUR",
    'website': 'www.browseinfo.in',
    'description':""" This module allow to create issue directly from task and it will show how many issues in a particular task.Create Issue from Task, Add Issue from Task, Create Issue from Project Task, Add Issue from Project Task """,
    'summary': 'This apps helps to create multiple issue from the project task',
    'license':'OPL-1',
    'depends':['base','project','rating_project_issue'],
    'data':[
        'views/project_issues.xml',
        'wizard/project_issue_wizard.xml',
        ],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
