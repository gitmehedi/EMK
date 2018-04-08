# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Stock(models.Model):
    _inherit = 'stock.location'

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_required_operating_unit(self):
        pass

    @api.multi
    def write(self, values):

        res = super(Stock, self).write(values)
        return res