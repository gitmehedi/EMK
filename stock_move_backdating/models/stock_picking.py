# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    date_done = fields.Datetime('Date of Transfer', copy=False, readonly=False,
                                default=fields.Datetime.now, states={'done': [('readonly', True)]},
                                help="Completion Date of Transfer")

    @api.constrains('date_done')
    def _check_date_done(self):
        for stock_picking in self:
            if datetime.strptime(stock_picking.date_done, "%Y-%m-%d %H:%M:%S") > datetime.now():
                raise ValidationError('Transfer Date can not be greater then present date!!')

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()
        if res:
            picking = self.browse(self.ids)[0]
            for move in picking.move_lines:
                if self.date_done:
                    move.write({'date': self.date_done})

        return res
