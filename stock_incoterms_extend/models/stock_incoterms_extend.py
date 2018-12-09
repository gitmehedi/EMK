# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class Incoterms(models.Model):
    _inherit = "stock.incoterms"
    _description = "Incoterms"
    _rec_name ="code"