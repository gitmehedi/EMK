from odoo import api, exceptions, fields, models


class PurchasrRequisition(models.AbstractModel):
    _name = 'report.gbs_purchase_requisition.report_purchase_requisition'

    @api.multi
    def render_html(self, docids, data=None):
        pur_req = self.env['purchase.requisition.line'].search([])
        product = self.env['product.template'].search([])
        price = product.standart_price * pur_req.price_unit

        docargs = {
            'price_unit': price
        }

        return self.env['report'].render('gbs_purchase_requisition.report_purchase_requisition', docargs)
