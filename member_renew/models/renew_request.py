import base64

from odoo import models, fields, api, _
from odoo.addons.opa_utility.helper.utility import Utility
from odoo.exceptions import ValidationError, Warning


class RenewRequest(models.Model):
    _name = 'renew.request'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Membership Renew Request'
    _rec_name = 'membership_id'
    _order = 'id desc'

    def _default_renew_amount(self):
        product = self.env['product.product'].search([('membership_status', '=', True)], order='id desc', limit=1)
        return product.list_price

    def _default_payment(self):
        partner = self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
        return partner

    name = fields.Char(string='Name', readonly=True)
    membership_id = fields.Many2one('res.partner', string='Name', required=True, track_visibility="onchange",
                                    domain=[('state', '=', 'member')], readonly=True,
                                    states={'request': [('readonly', False)]})
    membership_state_date = fields.Date(string="Start Date", track_visibility="onchange")
    membership_end_date = fields.Date(string="End Date", track_visibility="onchange")
    request_date = fields.Date(string='Request Date', default=fields.Date.today(), required=True,
                               track_visibility="onchange", readonly=True, states={'request': [('readonly', False)]})
    payment_ids = fields.Many2many('account.payment', string='Payment')
    payment_amount = fields.Float(string='Payment Amount')
    renew_amount = fields.Float(string="Renew Amount", track_visibility="onchange", required=True,
                                readonly=True, states={'request': [('readonly', False)]})
    approve_date = fields.Date(string='Approve Date', default=fields.Date.today(), track_visibility="onchange",
                               readonly=True, states={'request': [('readonly', False)]})
    invoice_id = fields.Many2one('account.invoice', string='Invoice', track_visibility="onchange", readonly=True)
    membership_type_id = fields.Many2one('product.product', string='Membership Type', track_visibility="onchange",
                                         required=True, default=_default_renew_amount,
                                         domain=[('membership', '=', True), ('type', '=', 'service')])
    membership_duration = fields.Integer(string='Membership Year', track_visibility="onchange", required=True,
                                         default=1)
    state = fields.Selection([('request', 'Request'), ('invoice', 'Invoiced'), ('done', 'Done'), ('reject', 'Reject')],
                             default='request', string='State', track_visibility="onchange")

    @api.constrains('membership_id')
    def check_duplicate(self):
        rec = self.search([('membership_id', '=', self.membership_id.id), ('state', 'in', ['request', 'invoice'])])
        if len(rec) > 1:
            raise ValidationError(
                _('Currently a record exist for processing with member'.format(self.membership_id.name)))

    @api.onchange('membership_id')
    def onchange_membership(self):
        res = {}
        payments = self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
        pay_ids = [val.id for val in payments if not val.invoice_ids]
        res['domain'] = {
            'payment_ids': [('id', 'in', pay_ids)],
        }
        return res

    @api.onchange('membership_type_id', 'membership_id', 'membership_duration')
    def onchange_membership_type(self):
        if self.membership_id and self.membership_type_id:
            self.membership_state_date = Utility.next_date(self.membership_id.membership_stop, 1, 'days')
            self.membership_end_date = Utility.next_date(self.membership_id.membership_stop,
                                                         self.membership_duration)
            self.renew_amount = self.membership_duration * self.membership_type_id.list_price

    @api.onchange('payment_ids')
    def onchange_payment_ids(self):
        if self.payment_ids:
            self.payment_amount = sum([val.amount for val in self.payment_ids])

    @api.one
    def act_invoice(self):
        if 'request' in self.state:
            inv = self._create_invoice()
            sequence = self.env['ir.sequence'].next_by_code('renew.member.request.seq')
            mem_inv = self.env['membership.membership_line'].search([('account_invoice_line', '=', inv.id)])
            self.payment_ids.write({'invoice_ids': [(6, 0, [self.invoice_id.id])]})
            self.env['account.payment'].search([('partner_id', '=', self.membership_id.id)])
            mem_inv.write({'date': self.request_date,
                           'date_from': self.membership_state_date,
                           'date_to': self.membership_end_date
                           })
            self.write({'name': sequence,
                        'invoice_id': inv.id,
                        'state': 'invoice',
                        })

    @api.one
    def act_done(self):
        if 'invoice' in self.state:
            self.state = 'done'

    @api.one
    def act_reject(self):
        if 'request' in self.state:
            self.state = 'reject'

    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['request', 'invoice'])]

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('invoice', 'done', 'reject'):
                raise Warning(_('[Warning] Record cannot deleted.'))
        return super(RenewRequest, self).unlink()

    @api.model
    def _create_invoice(self):
        ins_inv = self.env['account.invoice']
        journal_id = self.env['account.journal'].search([('code', '=', 'INV')])
        account_id = self.env['account.account'].search([('internal_type', '=', 'receivable'),
                                                         ('deprecated', '=', False)])

        acc_invoice = {
            'partner_id': self.membership_id.id,
            'date_invoice': self.request_date,
            'user_id': self.env.user.id,
            'account_id': account_id.id,
            'state': 'draft',
            'invoice_line_ids': [
                (0, 0, {
                    'name': self.membership_type_id.name,
                    'product_id': self.membership_type_id.id,
                    'price_unit': self.renew_amount,
                    'account_id': journal_id.default_debit_account_id.id,
                })]
        }
        inv = ins_inv.create(acc_invoice)
        inv.action_invoice_open()

        if inv:
            self.state = 'invoice'
            pdf = self.env['report'].sudo().get_pdf([inv.id], 'account.report_invoice')
            attachment = self.env['ir.attachment'].create({
                'name': inv.number + '.pdf',
                'res_model': 'account.invoice',
                'res_id': inv.id,
                'datas_fname': inv.number + '.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf),
                'mimetype': 'application/x-pdf'
            })

            vals = {
                'template': 'member_signup.member_invoice_email_template',
                'email_to': self.membership_id.email,
                'attachment_ids': [(6, 0, attachment.ids)],
                'context': {'name': self.name},
            }
            self.membership_id.mailsend(vals)
            return inv
