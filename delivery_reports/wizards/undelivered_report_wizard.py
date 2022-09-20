from datetime import datetime
import pytz
from odoo import api, fields, models, _
import time

class UndeliveredReportWizard(models.TransientModel):
    _name = 'undelivered.report.wizard'

    # date_today = fields.Date(string='Date', readonly=True, default=datetime.datetime.today())
    date_today = fields.Date(string='Date', default=fields.Date.today())
    date_from = fields.Date(string='Date From', readonly=True, required=True,
                            default=time.strftime('%Y-%m-%d'))
    partner_id = fields.Many2one('res.partner', string='Customer', domain="([('customer','=','True')])")
    product_tmpl_id = fields.Many2one('product.template', string='Product', domain="([('sale_ok','=','True')])")
    product_id = fields.Many2one('product.product', string='Product Variant', domain="([('sale_ok','=','True')])")
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        domain=lambda self: [("id", "in", self.env.user.operating_unit_ids.ids)])

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            return {'domain': {'product_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]}}
        else:
            return {'domain': {'product_id': [('sale_ok', '=', 'True')]}}

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='delivery_reports.undelivered_report_xlsx')
