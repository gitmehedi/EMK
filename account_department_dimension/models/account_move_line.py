# -*- coding: utf-8 -*-
# Copyright 2015-2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    department_id = fields.Many2one('hr.department', index=True, string='Department')
