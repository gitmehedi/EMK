# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class RFIDGeneration(models.Model):
    _name = 'rfid.generation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'RFID Generation'
    _rec_name = 'membership_id'
    _order = 'date desc'

    ref = fields.Text(string='Reference', readonly=True, track_visibility="onchange",
                      states={'draft': [('readonly', False)]})
    date = fields.Date(default=fields.Datetime.now(), string='Date', readonly=True, track_visibility="onchange",
                       states={'draft': [('readonly', False)]})
    membership_id = fields.Many2one('res.partner', string='Applicant/Member', required=True,
                                    track_visibility="onchange",
                                    domain=['&', ('is_applicant', '=', True), ('credit', '>', 0)],
                                    readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'),
                              ('issue', 'Issued'),
                              ('generate', 'Generated'),
                              ('handover', 'Hand Over')],
                             track_visibility="onchange", default='draft', string='State')

    @api.multi
    def rfid_print(self):
        if self.state == 'issue':
            self.ensure_one()
            report = self.env['report'].get_action(self, 'member_signup.rfid_gen_tmpl')
            return report

    @api.multi
    def act_issue(self):
        if self.state == 'draft':
            self.state = 'issue'

    @api.multi
    def act_generate(self):
        if self.state == 'issue':
            self.state = 'generate'

    @api.multi
    def act_handover(self):
        if self.state == 'generate':
            self.state = 'handover'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]
