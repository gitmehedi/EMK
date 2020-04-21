from odoo import api, fields, models, _


class RecieveOutstandingAdvance(models.Model):
    _name = 'receive.outstanding.advance'
    _inherit = ['mail.thread']
    _description = 'Outstanding Advance'
    _order = 'name desc'

    name = fields.Char('Name', required=False, track_visibility='onchange')
    agreement_id = fields.Many2one('agreement', string='Agreement', track_visibility='onchange')
    amount = fields.Float('Amount', track_visibility='onchange')
    debit_account_id = fields.Many2one('account.account', string='Debit Account', track_visibility='onchange')
    branch_id = fields.Many2one('operating.unit', string='Branch', track_visibility='onchange')
    sou_id = fields.Many2one('sub.operating.unit', string='Sub Operating Unit', track_visibility='onchange')
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.model
    def create(self, values):
        sequence = self.env['ir.sequence'].next_by_code('receive.outstanding.advance') or ''
        values['name'] = sequence
        return super(RecieveOutstandingAdvance, self).create(values)

    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.write({
                'state': 'confirm'
            })

    @api.multi
    def action_approve(self):
        for rec in self:
            rec.write({
                'state': 'approve'
            })

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'cancel'
            })