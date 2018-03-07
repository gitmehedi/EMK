# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class HrExperience(models.Model):
    _inherit = 'hr.experience'
    _inherit = 'hr.curriculum'

    passing_yr = fields.Char('Passing Year')
