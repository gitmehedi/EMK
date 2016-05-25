from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator
from datetime import date


class ExportInvoice(models.Model):
    """
    Inherit Account Invoice master model and names as Export Invoice
    """
    _inherit = 'account.invoice'


    """ Export invoice fields """
    ei_name = fields.Char(string="Serial", size=30, readonly=True)
    ei_code = fields.Char(string='Code')

    invoice_against = fields.Selection([('lc', 'LC'), ('tt', 'TT')], string="Invoice Against", required="True")
    export_invoice_no = fields.Char(string="Export Invoice No", size=30, required="True")
    ei_date = fields.Date(string="Export Invoice Date", default=date.today().strftime('%Y-%m-%d'))
    acceptace_date = fields.Date(string="Acceptance Date")
    inco_term_place = fields.Char(string="Inco Term Place", size=30)

    destination = fields.Char(string="Destination", size=30)
    mother_vessel = fields.Char(string="Mother Vessel", size=30)
    feader_vessel = fields.Char(string="Feader Vessel", size=30)
    shipping_mark = fields.Char(string="Shipping Mark", size=30)
    no_of_container = fields.Integer(string="No of Container")
    etd = fields.Char(string="ETD", size=30)
    bill_of_living_no = fields.Char(string="BL No", size=30)
    invoice_value = fields.Char(string="Invoice Value", size=30)
    discount = fields.Char(string="Discount %", size=30)
    discount_amount = fields.Char(string="Discount Amount", size=30)
    net_invoice_value = fields.Char(string="Net Invoice Value", size=30)

    conversion_rate = fields.Integer(string="Conversion Rate")
    invoice_value_bdt = fields.Integer(string="Invoice Value (BDT)")
    buying_house_com = fields.Integer(string="Buying House Com")


    remarks = fields.Text(string='Remarks')

    """ Relational fields """
    lc_id = fields.Many2one('master.lc', string='Export LC/ TT No')
    tt_id = fields.Many2one('tt.payment', string='Export LC/ TT No')
    consignee = fields.Many2one('res.bank', string='Consignee')
    notify_party = fields.Many2one('res.partner', string='Notify Party')
    port_of_loading = fields.Many2one('port', string='Port of Loading')
    port_of_discharge = fields.Many2one('port', string='Port of Discharge')
    currency = fields.Many2one('res.currency', string="Currency")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Terms/Tenor")
    inco_term_id = fields.Many2one('stock.incoterms', ei_string="Inco Term")
    shipment_mode = fields.Selection([("sea", "Sea"), ("air", "Air"), ("road", "By Road")], string='Ship Mode')

    """ One2many relationships """
    shipment_mode = fields.Selection([("sea", "Sea"), ("air", "Air"), ("road", "By Road")], string='Ship Mode')
    state = fields.Selection(selection=[('draft', "Draft"), ('submission', "Submission"),('acceptance', "Acceptance"),('realization', "Realization")])

    """ All kinds of validation message """
    @api.multi
    def _validate_data(self, value):
        msg , filterInt, filterNum, filterChar = {}, {}, {}, {}

        filterChar['Export LC/TT No'] = value.get('export_invoice_no', False)
        filterInt['Discount'] = value.get('discount', False)
        filterNum['No of Container'] = value.get('no_of_container', False)
        filterNum['Invoice Value'] = value.get('invoice_value', False)
        filterNum['Discount Amount'] = value.get('discount_amount', False)
        filterNum['Net Invoice Value'] = value.get('net_invoice_value', False)
        filterNum['Conversion Rate'] = value.get('conversion_rate', False)
        filterNum['Invoice Value (BDT)'] = value.get('invoice_value_bdt', False)
        filterNum['Buying House Com'] = value.get('buying_house_com', False)


        msg.update(validator._validate_percentage(filterInt))
        msg.update(validator._validate_number(filterNum))
        msg.update(validator._validate_character(filterChar, True))
        validator.validation_msg(msg)

        return True


    """ All function which process data and operation """


    @api.model
    def create(self, vals):
        self._validate_data(vals)
        vals['ei_name'] = self.env['ir.sequence'].get('ei_code')

        return super(ExportInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        self._validate_data(vals)

        return super(ExportInvoice, self).write(vals)

    """ Onchange functionality """

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = {}
        self.lc_no_id = 0
        self.invoice_submission_details_ids = 0

        if self.partner_id and self.invoice_against=='lc':
            lc_obj = self.env['master.lc'].search([('buyer_id', '=', self.partner_id.id)])

            print "-------------------- lc_obj----------------", lc_obj

            res['domain'] = {
                'lc_id': [('id', 'in', lc_obj.ids)],
            }

        return res



    @api.multi
    @api.depends('ei_name')
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s' % (record.ei_name)))
        return result

    @api.multi
    def action_draft(self):
        self.ei_state = 'draft'

    @api.multi
    def action_submission(self):
        self.ei_state = 'submission'

