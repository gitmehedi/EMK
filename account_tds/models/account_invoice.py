from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('invoice_line_ids.tds_amount')
    def _compute_total_tds(self):
        for invoice in self:
            invoice.total_tds_amount = sum(line.tds_amount for line in invoice.invoice_line_ids)

    is_applicable = fields.Boolean(string='TDS Applicable',default=True,
        readonly=True,states={'draft': [('readonly', False)]},
        help="""TDS applicable/not applicable for this bill.
               If its not applicable then need to take decision 
               that is it for permanent or temporary.""")
    inapplicable_type = fields.Selection([
        ('temporary_inapplicable', 'Temporary'),
        ('permanent_inapplicable', 'Permanent')], string='Select Type',
        readonly=True, states={'draft': [('readonly', False)]},
        help="""If TDS not apply for this bill or supplier already give the TDS for this bill then it will permanently inapplicable.
        If there any chance to add TDS in this bill then its temporary inapplicable""")

    total_tds_amount = fields.Float('Total TDS', compute='_compute_total_tds',
        store=True, readonly=True, track_visibility='always')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tds_amount = fields.Float('Tds value', compute='_compute_tds_value', readonly=True)

    @api.multi
    @api.depends('quantity', 'price_unit')
    def _compute_tds_value(self):
        for line in self:
            if line.invoice_id.is_applicable and line.product_id:
                pro_base_val = line.quantity * line.price_unit
                if line.product_id.account_tds_id.type_rate == 'flat':
                    line.tds_amount = pro_base_val * line.product_id.account_tds_id.flat_rate/100
                else:
                    for tds_slab_rule_obj in line.product_id.account_tds_id.line_ids:
                        if pro_base_val>=tds_slab_rule_obj.range_from and pro_base_val<=tds_slab_rule_obj.range_to:
                            line.tds_amount = pro_base_val * tds_slab_rule_obj.rate / 100
                        else:
                            line.tds_amount = 0.0






