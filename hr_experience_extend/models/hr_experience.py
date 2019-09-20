# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields

class HrAcademic(models.Model):
    _inherit = 'hr.academic'

    passing_yr = fields.Char('Passing Year')
