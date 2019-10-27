# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountPeriodClose(models.TransientModel):
    _name = "account.period.close"
    _description = "period close"

    sure = fields.Boolean('Check this box', required=True)

    @api.multi
    def data_save(self, context=None):
        mode = 'done'
        for rec in self:
            if rec.sure:
                for id in context['active_ids']:
                    range = self.env['date.range'].search([('id', '=', id)])
                    move_ids = self.env['account.move'].search(
                        [('state', '=', 'draft'), ('date', '>=', range['date_start']),
                         ('date', '<=', range['date_end'])])
                if move_ids:
                    raise Warning(_('In order to close a period, you must first approve all journal entries within this period.'))

                self.env['date.range'].write({'state': 'close'})

        return {'type': 'ir.actions.act_window_close'}

        # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
