from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPaymentBatch(models.Model):
    _name = "account.payment.batch"

    name = fields.Char(string='Batch Name', required=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status")
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))])

    """ Relational field"""
    payment_ids = fields.One2many('account.payment', 'batch_id', string='Customer Payments')

    is_batch_model = fields.Boolean(store=False, compute='_check_is_batch_model')

    @api.multi
    def unlink(self):
        """ delete function """
        for rec in self:
            if any(bool(ac.move_line_ids) for ac in rec.payment_ids):
                raise UserError(_("You can not delete a payment batch that is already posted"))
        return super(AccountPaymentBatch, self).unlink()

    @api.multi
    def post(self):
        """ confirm function """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment batch can be posted. "
                                  "Trying to post a payment batch in state %s.") % rec.state)
            else:
                for ap in rec.payment_ids:
                    if ap.state != 'posted':
                        ap.invoice_ids = ap.get_invoices()
                        ap.post()

                rec.write({'state': 'posted'})

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.payment_ids = []

    @api.depends('journal_id')
    def _check_is_batch_model(self):
        self.is_batch_model = True

    @api.multi
    def button_journal_entries(self):
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('payment_id', 'in', self.payment_ids.ids)],
        }


class InheritAccountPayment2(models.Model):
    _inherit = "account.payment"

    """ Relational field"""
    batch_id = fields.Many2one('account.payment.batch', ondelete='cascade')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(InheritAccountPayment2, self).onchange_partner_id()
        if self.batch_id.is_batch_model:
            if self.batch_id.journal_id.id:
                self.journal_id = self.batch_id.journal_id
            else:
                raise UserError(_("You must select a payment journal."))

        return res

    @api.multi
    def get_invoices(self):
        invoice_ids = self.env['account.invoice'].sudo().search([('partner_id', '=', self.partner_id.id),
                                                                 ('state', '=', 'open')])
        if self.sale_order_id.ids:
            invoice_ids = self.env['account.invoice'].sudo().search([('so_id', 'in', self.sale_order_id.ids),
                                                                    ('state', '=', 'open')])
        return invoice_ids
