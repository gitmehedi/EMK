from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorBillGeneration(models.Model):
    _name = 'vendor.bill.generation'
    _inherit = ['mail.thread']
    _description = 'Vendor Bill Generation'
    _order = 'name desc'

    name = fields.Char('Name', required=False, track_visibility='onchange', default='Draft VBG')
    narration = fields.Text('Narration')
    billing_period = fields.Selection([
        ('monthly', "Monthly"),
        ('yearly', "Yearly")], string="Billing Period", required=True,
        track_visibility='onchange', readonly=True, states={'draft': [('readonly', False)]})
    period_id = fields.Many2one('date.range', track_visibility='onchange', required=True,
                                readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.multi
    def action_confirm(self):
        for rec in self:
            name = self.env['ir.sequence'].sudo().next_by_code('vendor.bill.generation') or 'New'
            rec.write({
                'state': 'confirm',
                'name': name
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

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorBillGeneration, self).unlink()