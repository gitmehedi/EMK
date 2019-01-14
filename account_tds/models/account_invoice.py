from odoo import api, fields, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('invoice_line_ids.tds_amount')
    def _compute_total_tds(self):
        for invoice in self:
            invoice.total_tds_amount = sum(line.tds_amount for line in invoice.invoice_line_ids)

    is_tds_applicable = fields.Boolean(string='TDS Applicable',default=True,
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

    tds_amount = fields.Float('Tds value', compute='_compute_tds_value', readonly=True,store=True)
    account_tds_id = fields.Many2one(related='product_id.account_tds_id', string='TDS Rule',
                                     store=True)

    @api.multi
    @api.depends('quantity', 'price_unit')
    def _compute_tds_value(self):
        for line in self:
            if line.invoice_id.is_tds_applicable and line.product_id:
                pro_base_val = line.quantity * line.price_unit
                if line.account_tds_id.type_rate == 'flat':
                    # calculate previous vendor bill
                    line.tds_amount = pro_base_val * line.account_tds_id.flat_rate/100
                    remaining_pre_tds = self.previous_tds_value(line)
                    if remaining_pre_tds:
                        line.tds_amount = line.tds_amount + remaining_pre_tds
                else:
                    for tds_slab_rule_obj in line.account_tds_id.line_ids:
                        if pro_base_val>=tds_slab_rule_obj.range_from and pro_base_val<=tds_slab_rule_obj.range_to:
                            line.tds_amount = pro_base_val * tds_slab_rule_obj.rate / 100
                            self.previous_tds_value(line)
                            break
                        else:
                            line.tds_amount = 0.0


    def previous_tds_value(self,product_line):
        pre_invoice_line_objs = self.search([('product_id','=',product_line.product_id.id),
                                             ('invoice_id.partner_id','=',product_line.invoice_id.partner_id.id),
                                             ('account_tds_id','=',product_line.account_tds_id.id),
                                             ('invoice_id.is_tds_applicable','=',True),
                                             ('invoice_id.state','=','paid')])

        pre_total_tds = pre_total_qty = pre_total_price = count= 0.0
        for pre_invoice_line_obj in pre_invoice_line_objs:
            pre_total_tds += pre_invoice_line_obj.tds_amount
            pre_total_qty += pre_invoice_line_obj.quantity
            pre_total_price += pre_invoice_line_obj.price_unit
            count += 1
        # pre_total_qty = 900
        # pre_total_tds = 3040.65
        # pre_total_price = 135.14
        # count = 2
        # remain_tds_amount = 0

        pre_rate = (pre_total_tds * 100*count)/(pre_total_qty * pre_total_price)
        if product_line.account_tds_id.flat_rate > pre_rate:
            remain_tds_amount = ((pre_total_price * pre_total_qty * product_line.account_tds_id.flat_rate)/(100*count)) - pre_total_tds

        return remain_tds_amount




