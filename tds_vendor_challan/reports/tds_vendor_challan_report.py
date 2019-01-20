from odoo import api,models,fields
from odoo.tools.misc import formatLang


class PurchaseReport(models.AbstractModel):
    _name = "report.tds_vendor_challan.report_tds_vendor_challan"

    #
    # @api.multi
    # def render_html(self,docids,data=None):
    #
    #     docargs = {
    #         'data': data,
    #
    #     }
    #     return self.env['report'].render('purchase_reports.report_purchase_material_requisition', docargs)