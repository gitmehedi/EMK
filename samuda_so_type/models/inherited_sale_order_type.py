from odoo import fields, models,api
from odoo.exceptions import UserError, ValidationError

class InheritedSaleOrderType(models.Model):
    _inherit = 'sale.order.type'
    _order = 'name'

    #operating_unit = fields.Many2one('operating.unit', string="Operating Unit", required=True,track_visibility='onchange')
    sale_order_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
        ('tt_sales', 'TT'),
        ('contract_sales', 'Sales Contract'),
    ], string='Sale Order Type', required=True,track_visibility='onchange')

    region_type = fields.Selection([
        ('local', 'Local'),
        ('foreign', 'Foreign'),
    ], string="Region Type", required=True, track_visibility='onchange',
        help="Local: Local LC.\n"
             "Foreign: Foreign LC.")

    currency_id = fields.Many2one('res.currency', string="Currency", required=True,track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['sale.order.type'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('Sale Order Type for this Name already exists')



#################################################
# Add Sales Order Type to Sales Analysis Report
################################################

# class InheritSaleReport(models.Model):
#     _inherit = 'sale.report'
#
#     type_id = fields.Many2one('sale.order.type', string='Sale Order Type',readonly=True)
#
#
#     def _select(self):
#         select_str = """
#             WITH currency_rate as (%s)
#              SELECT min(l.id) as id,
#                     l.product_id as product_id,
#                     t.uom_id as product_uom,
#                     sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
#                     sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
#                     sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
#                     sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
#                     sum(l.price_total / COALESCE(cr.rate, 1.0)) as price_total,
#                     sum(l.price_subtotal / COALESCE(cr.rate, 1.0)) as price_subtotal,
#                     count(*) as nbr,
#                     s.name as name,
#                     s.date_order as date,
#                     s.type_id AS type_id,
#                     s.state as state,
#                     s.partner_id as partner_id,
#                     s.user_id as user_id,
#                     s.company_id as company_id,
#                     extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
#                     t.categ_id as categ_id,
#                     s.pricelist_id as pricelist_id,
#                     s.project_id as analytic_account_id,
#                     s.team_id as team_id,
#                     p.product_tmpl_id,
#                     partner.country_id as country_id,
#                     partner.commercial_partner_id as commercial_partner_id,
#                     sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
#                     sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
#         """ % self.env['res.currency']._select_companies_rates()
#         return select_str
#
#
#     def _group_by(self):
#         group_by_str = """
#             GROUP BY l.product_id,
#                     l.order_id,
#                     t.uom_id,
#                     t.categ_id,
#                     s.name,
#                     s.date_order,
#                     s.partner_id,
#                     s.user_id,
#                     s.state,
#                     s.company_id,
#                     s.pricelist_id,
#                     s.project_id,
#                     s.team_id,
#                     s.type_id,
#                     p.product_tmpl_id,
#                     partner.country_id,
#                     partner.commercial_partner_id
#         """
#         return group_by_str



###################################################
# Add Sales Order Type on Invoice Analysis Report
###################################################

#
# class InheritedAccountInvoiceReport(models.Model):
#     _inherit = 'account.invoice.report'
#
#
#     #product_template = fields.Many2one('product.template', string='Product Template', readonly=True)
#     sale_type_id = fields.Many2one('sale.order.type', string='Sale Order Type', readonly=True)
#
#
#     def _select(self):
#         select_str = """
#                SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
#                    sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
#                    sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
#                    sub.weight, sub.volume, sub.sale_type_id,
#                    sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
#                    sub.product_qty, sub.price_total as price_total, sub.price_average as price_average,
#                    COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id
#            """
#         return select_str
#
#     def _sub_select(self):
#         select_str = """
#                    SELECT ail.id AS id,
#                        ai.date_invoice AS date,
#                        ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
#                        u2.name AS uom_name,
#                        ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
#                        1 AS nbr, ai.sale_type_id AS sale_type_id,
#                        ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
#                        ai.partner_bank_id,
#                        SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
#                        SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
#                        SUM(ABS(ail.price_subtotal_signed)) / CASE
#                                WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
#                                   THEN SUM(ail.quantity / u.factor * u2.factor)
#                                   ELSE 1::numeric
#                                END AS price_average,
#                        ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
#                        count(*) * invoice_type.sign AS residual,
#                        ai.commercial_partner_id as commercial_partner_id,
#                        partner.country_id,
#                        SUM(pr.weight * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS weight,
#                        SUM(pr.volume * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS volume
#            """
#         return select_str
#
#
#     def _group_by(self):
#         group_by_str = """
#                    GROUP BY ail.id, ail.product_id, ail.account_analytic_id, ai.date_invoice, ai.id,
#                        ai.sale_type_id, ai.partner_id, ai.payment_term_id, u2.name, u2.id, ai.currency_id, ai.journal_id,
#                        ai.fiscal_position_id, ai.user_id, ai.company_id, ai.type, invoice_type.sign, ai.state, pt.categ_id,
#                        ai.date_due, ai.account_id, ail.account_id, ai.partner_bank_id, ai.residual_company_signed,
#                        ai.amount_total_company_signed, ai.commercial_partner_id, partner.country_id
#            """
#         return group_by_str
#
#
#
#
#
#
#
#
