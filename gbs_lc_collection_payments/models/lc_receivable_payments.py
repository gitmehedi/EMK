from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LCReceivablePayment(models.Model):

    _name = 'lc.receivable.payment'
    _description = 'LC Receivable Payment'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "date desc"

    name = fields.Char(string='Reference', readonly=True, index=True,
                       track_visibility='onchange')
    lc_id = fields.Many2one('letter.credit', 'LC', ondelete='cascade',required=True,
                            readonly=True,states={'draft': [('readonly', False)]},
                            domain=[('type', '=', 'export')],
                            track_visibility = 'onchange')
    shipment_id = fields.Many2one('purchase.shipment','Shipment', ondelete='cascade',required=True,
                                  readonly=True, states={'draft': [('readonly', False)]},
                                  track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', string='Currency',readonly=True,store=True,
                                  track_visibility='onchange',compute='_compute_rate_amounts')
    invoice_amount = fields.Float(string='Invoice Amount',readonly=True,store=True,
                                  track_visibility='onchange',compute='_compute_rate_amounts')
    currency_rate = fields.Float(string='Currency Rate',readonly=True,store=True,
                                 track_visibility='onchange',compute='_compute_rate_amounts')
    amount_in_company_currency = fields.Float(string='Amount',readonly=True,store=True,
                                              track_visibility='onchange',compute='_compute_rate_amounts')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cost Centre', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]},
                                          track_visibility='onchange',required=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)
    date = fields.Datetime('Date', index=True, default=fields.Datetime.now,
                           readonly=True,states={'draft': [('readonly', False)]},
                           track_visibility = 'onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled')], string='Status', default='draft',
                             track_visibility='onchange')

    invoice_ids = fields.Many2many('account.invoice',
                                   'lc_collection_invoice_rel',
                                   'lc_collection_id',
                                   'invoice_id',
                                   'Invoices',readonly=True,required=True,
                                   states={'draft': [('readonly', False)]})

    """ Relational Fields """

    lc_receivable_collection_ids = fields.One2many('lc.receivable.collection', 'collection_parent_id',
                                                   string="Collections",readonly=True,
                                                   states={'draft': [('readonly', False)]})
    lc_receivable_charges_ids = fields.One2many('lc.receivable.charges', 'charges_parent_id',
                                                string="Charges",readonly=True,
                                                states={'draft': [('readonly', False)]})

    @api.onchange('lc_id')
    def onchange_lc_id(self):
        if self.lc_id:
            self.shipment_id = []
            self.invoice_ids = []
            self.currency_id = []
            self.invoice_amount = []
            self.amount_in_company_currency = []
            self.analytic_account_id = False
            invoice_ids = []
            shipment_ids = []
            shipment_objs = self.env['purchase.shipment'].search([('lc_id', '=', self.lc_id.id)])
            if shipment_objs:
                shipment_ids = shipment_objs.ids

            if self.lc_id.pi_ids_temp:
                so_objs = self.env['sale.order'].search([('pi_id', 'in',self.lc_id.pi_ids_temp.ids)])
                if so_objs:
                    for so_obj in so_objs:
                        for invoice_id in so_obj.invoice_ids:
                            invoice_ids.append(invoice_id.id)
            analytic_account_id = False
            if self.lc_id.analytic_account_id:
                analytic_account_id = self.lc_id.analytic_account_id.id
                self.analytic_account_id = analytic_account_id
            return {
                'domain': {'shipment_id': [('id', 'in', shipment_ids)],
                           'invoice_ids': [('id', 'in', invoice_ids),
                                           ('currency_id','=',self.lc_id.currency_id.id),
                                           ('state','=','open')],
                           'analytic_account_id': [('id', '=', analytic_account_id)]
                           }
            }

    @api.multi
    @api.depends('lc_id', 'date', 'invoice_ids')
    def _compute_rate_amounts(self):
        for record in self:
            if record.lc_id and record.invoice_ids:
                record.currency_id = record.lc_id.currency_id.id
                record.invoice_amount = sum(rec.residual for rec in record.invoice_ids)
                record.currency_rate = \
                    record.company_id.currency_id.rate / record.currency_id.with_context(date=record.date).rate
                record.amount_in_company_currency = record.invoice_amount * record.currency_rate

    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_approve(self):
        self.write({'state': 'approve'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not in draft state!'))
        return super(LCReceivablePayment, self).unlink()

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'confirm')]


class LCReceivableCollection(models.Model):
    _name = 'lc.receivable.collection'

    collection_parent_id = fields.Many2one('lc.receivable.payment', 'Collections', ondelete='cascade')
    account_journal_id = fields.Many2one('account.journal', string="Bank Account",required=True,
                                         domain="[('type', '=', 'bank')]")
    currency_id = fields.Many2one('res.currency', string='Currency',required=True)
    currency_rate = fields.Float(string='Currency Rate',required=True)
    amount_in_currency = fields.Float(string='Amount In Currency',required=True)
    amount_in_company_currency = fields.Float(string='Amount')

    @api.onchange('account_journal_id')
    def _onchange_account_journal_id(self):
        domain = {}
        if not self.collection_parent_id:
            return

        if not self.collection_parent_id.lc_id or not self.collection_parent_id.invoice_ids:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a LC and at lest one Invoice!'),
            }
            return {'warning': warning}

        self.currency_id = self.collection_parent_id.currency_id
        self.currency_rate = self.collection_parent_id.currency_rate
        self.amount_in_currency = self.collection_parent_id.invoice_amount
        self.amount_in_company_currency = self.collection_parent_id.amount_in_company_currency

        domain['currency_id'] = [('id', '=', self.collection_parent_id.currency_id.id)]
        return {'domain': domain}




class LCReceivableCharges(models.Model):
    _name = 'lc.receivable.charges'

    charges_parent_id = fields.Many2one('lc.receivable.payment', 'Charges', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Service')
    account_id = fields.Many2one('account.account', string="Account")
    currency_id = fields.Many2one('res.currency', string='Currency')
    currency_rate = fields.Float(string='Currency Rate')
    amount_in_currency = fields.Float(string='Amount In Currency')
    amount_in_company_currency = fields.Float(string='Amount')
