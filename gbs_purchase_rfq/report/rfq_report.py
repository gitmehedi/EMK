from odoo import api, exceptions, fields, models

class GbsRFQReport(models.AbstractModel):
    _name = 'report.gbs_purchase_rfq.rfq_report'

    @api.multi
    def render_html(self, docids, data=None):

        if docids:
            rfq_obj_pool = self.env['purchase.rfq']
            rfq_obj = rfq_obj_pool.browse(docids[0])

            vals = []
            for obj in rfq_obj.purchase_rfq_lines:
                vals.append(({'product_id': obj.product_id.name,
                              'product_qty': obj.product_qty,
                              'product_uom_id': obj.product_uom_id.name,
                              }))
            data['vals'] = vals

        docargs = {
            'lists': data['vals'],
        }

        return self.env['report'].render('gbs_purchase_rfq.rfq_report', docargs)