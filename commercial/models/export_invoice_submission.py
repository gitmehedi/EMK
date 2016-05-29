from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ExportInvoiceSubmission(models.Model):
    """ 
    Export Invoice Submission creates for buyer
    """
    
    _name = 'export.invoice.submission'

    """ Buyer Work Order fields """
    name = fields.Char(string="Serial", size=30, readonly=True)
    eis_code = fields.Char(string='Code')
    
    submission_date = fields.Date(string="Submission Date", required=True, default=date.today().strftime('%Y-%m-%d'),
                                  readonly=True, states={'draft': [('readonly', False)]})
    acceptance_date = fields.Date(string="Acceptance Date", required=True,
                                  readonly=True, states={'draft': [('readonly', False)]})
    bank_ref_no = fields.Char(string="Bank Ref No", size=30, required=True,
                              readonly=True, states={'draft': [('readonly', False)]})
    submission_type = fields.Selection([('submission', 'Submission'), ('negotiation', 'Negotiation')],
                                       string="Submission Type", required=True, readonly=True, states={'draft': [('readonly', False)]})
    realization_date = fields.Date(string="Realization Date",  store=True, readonly=True, states={'draft': [('readonly', False)]})
    
    
    remarks = fields.Text(string='Remarks', readonly=True, states={'draft': [('readonly', False)]})

    """ Relational fields """
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, default=lambda self: self._set_default_currency('USD'),
                                  readonly=True, states={'draft': [('readonly', False)]})
    buyer_id = fields.Many2one('res.partner', string="Buyer", domain=[('customer', '=', 'True')],required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    lc_no_id = fields.Many2one('master.lc', string="LC No",required=True,
                               readonly=True, states={'draft': [('readonly', False)]})
    bank_id = fields.Many2one('res.bank', string="Bank", required=True,
                              readonly=True, states={'draft': [('readonly', False)]})
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms/Tenor",
                                      readonly=True, states={'draft': [('readonly', False)]})
    lc_type = fields.Selection([('deffered', "Deffered"), ('at_sight', "At Sight")], string="LC Type",
                               readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', "Draft"), ('submission', "Submission"),('accepted', "Accepted")], default='draft')

    """ One2many relational fields """
    invoice_submission_details_ids = fields.One2many('export.invoice.submission.details', 'export_invoice_submission_id',
                                                     readonly=True, states={'draft': [('readonly', False)]})

    """ All kinds of validation message """
    def _validate_data(self, vals):
        msg, filterChar = {}, {}

        filterChar['bank_ref_no'] = vals.get('bank_ref_no', False)

        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)

    def _set_default_currency(self, name):
        res = self.env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False


    """ All function which process data and operation """
    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['name'] = self.env['ir.sequence'].get('eis_code')

        return super(ExportInvoiceSubmission, self).create(vals)

    @api.multi
    def write(self, vals):
        self._validate_data(vals)

        return super(ExportInvoiceSubmission, self).write(vals)


    """ Onchange functionality """

    @api.onchange('buyer_id')
    def _onchange_buyer_id(self):
        res = {}
        self.lc_no_id = 0
        self.invoice_submission_details_ids = 0

        if self.buyer_id:
            lc_obj = self.env['master.lc'].search([('buyer_id','=',self.buyer_id.id)])

            res['domain'] = {
                'lc_no_id': [('id', 'in', lc_obj.ids)],
            }

        return res



    """ States functionality """

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_submission(self):
        self.state = 'submission'
        for obj in self.invoice_submission_details_ids:
            inv_obj = self.env['account.invoice'].search([('id', '=', obj.invoice_id.id)])
            inv_obj.write({'state': 'submission'})

    @api.multi
    def action_accepted(self):
        self.state = 'accepted'
        for obj in self.invoice_submission_details_ids:
            inv_obj = self.env['account.invoice'].search([('id', '=', obj.invoice_id.id)])
            inv_obj.write({'state': 'accepted'})













