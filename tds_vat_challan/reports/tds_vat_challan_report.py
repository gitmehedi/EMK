from odoo import api,models,fields
from odoo.tools.misc import formatLang

class TDSVATChallanReport(models.AbstractModel):
    _name = "report.tds_vat_challan.report_tds_vat_challan"

    @api.multi
    def render_html(self, docids, data=None):

        docargs = {
            'doc': self,
        }
        return self.env['report'].render('tds_vat_challan.report_tds_vat_challan', docargs)