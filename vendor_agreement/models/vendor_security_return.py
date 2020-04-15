from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class VendorSecurityReturn(models.Model):
    _name = 'vendor.security.return'
    _inherit = ['mail.thread']
    _description = 'Vendor Security Return'
    _order = 'name desc'

    name = fields.Char(required=False, track_visibility='onchange', string='Name', default='Draft VSR')
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange',
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    vsd_ids = fields.Many2many('vendor.security.deposit', 'vendor_security_deposit_return_rel',
                               'return_id', 'deposit_id', string='Security Deposits',
                               domain=[('state', '=', 'draft')],
                               readonly=True, states={'draft': [('readonly', False)]})
    optional_vsd_ids = fields.Many2many('vendor.security.deposit',
                                        'vendor_security_deposit_return_optional_rel',
                                        'return_id', 'deposit_id',
                                        string='Security Deposits',readonly=True,
                                        states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange',
                          states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('vendor.security.return.line', 'return_id',
                               string='Security Return Lines')
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.onchange('vsd_ids')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.vsd_ids:
                for vsd in rec.vsd_ids:
                    remaining_vsd_amount = vsd.amount - vsd.adjusted_amount
                    amount = amount + remaining_vsd_amount
                rec.amount = amount

    @api.onchange('vsd_ids')
    def _onchange_vsd_ids(self):
        self.optional_vsd_ids = self.vsd_ids

    @api.multi
    def action_confirm(self):
        for rec in self:
            if not rec.vsd_ids:
                raise ValidationError("No Vendor Security Deposit is selected")
            if not rec.amount>0:
                raise ValidationError("Amount must be greater than Zero")
            name = self.env['ir.sequence'].sudo().next_by_code('vendor.security.return') or 'New'
            rec.write({
                'state': 'confirm',
                'name': name
            })

    @api.multi
    def action_approve(self):
        security_return_line_obj = self.env['vendor.security.return.line']
        for rec in self:
            remaining_balance = rec.amount
            if rec.vsd_ids:
                for vsd in rec.vsd_ids:
                    security_deposit_obj = self.env['vendor.security.deposit'].sudo().search([('id', '=', vsd.id)])
                    remaining_vsd_balance = vsd.amount - vsd.adjusted_amount
                    line_vals = {
                        'vsd_id': vsd.id,
                        'return_id': rec.id,
                        'date': fields.datetime.now()
                    }
                    if remaining_balance >= remaining_vsd_balance:
                        line_vals['amount'] = remaining_vsd_balance
                        remaining_balance = remaining_balance - remaining_vsd_balance
                        security_return_line_obj.create(line_vals)
                        new_vsd_adjusted_amount = vsd.amount
                        security_deposit_obj.write({
                            'adjusted_amount': new_vsd_adjusted_amount,
                            'state': 'done'
                        })

                    elif remaining_vsd_balance > remaining_balance > 0:
                        line_vals['amount'] = remaining_balance
                        security_return_line_obj.create(line_vals)
                        new_vsd_adjusted_amount = vsd.adjusted_amount + remaining_balance
                        security_deposit_obj.write({
                            'adjusted_amount': new_vsd_adjusted_amount
                        })
                        break

            rec.write({
                'state': 'approve'
            })

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorSecurityReturn, self).unlink()




