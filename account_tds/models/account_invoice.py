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

    @api.multi
    def action_invoice_open(self):
        res = super(AccountInvoice, self).action_invoice_open()
        if res:
#         do tds calculation
            if self.is_tds_applicable:
                date_range_objs = self.env['date.range'].search([('date_start','<=',self.date),('date_end','>=',self.date),('type_id.tds_year','=',True)],
                                                                order='id DESC', limit=1)
                if date_range_objs:
                    invoice_objs = self.search([('id','!=',self.id),('partner_id','=',self.partner_id.id),('date','>=',date_range_objs.date_start),('date','<=',date_range_objs.date_end)])
                    for line in self.invoice_line_ids:
                        if invoice_objs:
                            line._calculate_tds_value(invoice_objs)
                        else:
                            line._calculate_tds_value()
                else:
                    pass
        return res

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    tds_amount = fields.Float('Tds value',readonly=True,store=True)
    account_tds_id = fields.Many2one('tds.rule',related='product_id.account_tds_id', string='TDS Rule',
                                     store=True)


    @api.multi
    def _calculate_tds_value(self,invoice_objs=None):
        # for line in self:
        if self.invoice_id.is_tds_applicable and self.product_id:
            pro_base_val = self.quantity * self.price_unit
            if self.account_tds_id.type_rate == 'flat':
                # calculate previous vendor bill
                self.tds_amount = pro_base_val * self.account_tds_id.flat_rate/100
                if invoice_objs:
                    remaining_pre_tds = self.previous_tds_value(invoice_objs)
                    self.tds_amount = self.tds_amount + remaining_pre_tds
            else:
                for tds_slab_rule_obj in self.account_tds_id.line_ids:
                    if pro_base_val>=tds_slab_rule_obj.range_from and pro_base_val<=tds_slab_rule_obj.range_to:
                        self.tds_amount = pro_base_val * tds_slab_rule_obj.rate / 100
                        self.previous_tds_value()
                        break
                    else:
                        self.tds_amount = 0.0


    def previous_tds_value(self,invoice_objs):
        pre_invoice_line_list = []
        for invoice_obj in invoice_objs:
            for invoice_line_obj in invoice_obj.invoice_line_ids:
                if invoice_line_obj.product_id.id == self.product_id.id and invoice_line_obj.account_tds_id.id == self.account_tds_id.id:
                    pre_invoice_line_list.append(invoice_line_obj)

        remain_tds_amount = pre_total_tds = pre_total_base_amount= 0.0
        for pre_invoice_line_obj in pre_invoice_line_list:
            pre_total_tds += pre_invoice_line_obj.tds_amount
            pre_total_base_amount += (pre_invoice_line_obj.price_unit * pre_invoice_line_obj.quantity)

        pre_rate = (pre_total_tds * 100)/pre_total_base_amount
        current_rate = self.account_tds_id.flat_rate
        if current_rate > pre_rate:
            remain_tds_amount = ((pre_total_base_amount *current_rate)/100) - pre_total_tds

        return remain_tds_amount




