from odoo import api, exceptions, fields, models

class GbsRFQReport(models.AbstractModel):
    _name = 'report.gbs_purchase_rfq.rfq_report'

    @api.multi
    def render_html(self, docids, data=None):

        docargs = {
            'lists': data['vals'],
        }

        return self.env['report'].render('gbs_purchase_rfq.rfq_report', docargs)