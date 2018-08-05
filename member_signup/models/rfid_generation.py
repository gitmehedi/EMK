# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RFIDGeneration(models.Model):
    _name = 'rfid.generation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name = 'membership_id'
    _order = 'date desc'

    ref = fields.Text(string='Payment Ref', readonly=True, states={'draft': [('readonly', False)]})
    date = fields.Date(default=fields.Datetime.now(), string='Date', readonly=True,
                       states={'draft': [('readonly', False)]})
    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    domain=['&', ('is_applicant', '=', True), ('credit', '>', 0)],
                                    readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('generate', 'Generated')], default='draft', string='State')

    @api.multi
    def rfid_print(self):
        self.ensure_one()
        report = self.env['report'].get_action(self, 'member_signup.rfid_gen_tmpl')
        return report

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]
