from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPaymentBatch(models.Model):
    _name = "account.payment.batch"
    _inherit = ['mail.thread']

    name = fields.Char(string='Batch Name', required=True, track_visibility='always')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'), ('reconciled', 'Reconciled')],
                             readonly=True, default='draft', copy=False, string="Status", track_visibility='onchange')
    journal_id = fields.Many2one('account.journal', string='Collection Journal', required=True,
                                 domain=[('type', 'in', ('bank', 'cash'))], track_visibility='onchange')
    is_auto_invoice_paid = fields.Boolean(string='Auto Invoice Paid', track_visibility='onchange')

    """ Relational field"""
    payment_ids = fields.One2many('account.payment', 'batch_id', string='Customer Collection')

    batch = fields.Boolean(store=False, compute='compute_batch')

    _sql_constraints = [('name_unique', 'unique(name)', 'The Batch name must be unique!')]

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
            elif not rec.payment_ids.ids:
                raise UserError(_("Trying to post a payment batch without any collection."))
            else:
                for ap in rec.payment_ids:
                    if ap.state != 'posted':
                        ap.post()

                rec.write({'state': 'posted'})

    @api.onchange('journal_id')
    def onchange_journal_id(self):
        self.payment_ids = []

    @api.onchange('is_auto_invoice_paid')
    def onchange_is_auto_invoice_paid(self):
        self.payment_ids = []

    @api.depends('journal_id')
    def compute_batch(self):
        self.batch = True

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


class InheritAccountPayment(models.Model):
    _inherit = "account.payment"

    """ Relational field"""
    batch_id = fields.Many2one('account.payment.batch', ondelete='cascade')
    sale_order_domain_ids = fields.Many2many('sale.order', compute="_compute_sale_order_domain_ids", readonly=True,
                                             store=False)

    @api.multi
    @api.depends('partner_id')
    def _compute_sale_order_domain_ids(self):
        for rec in self:
            ids = rec.get_sale_order_ids()
            rec.sale_order_domain_ids = self.env['sale.order'].search([('id', 'in', ids)])

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res = super(InheritAccountPayment, self).onchange_partner_id()
        if self.batch_id.batch:
            if not self.batch_id.journal_id:
                raise UserError(_("You must select a payment journal."))

            res['domain'] = {}

        return res
