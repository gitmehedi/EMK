from odoo import models, fields, api


class InheritStockPicking(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_individual_payslip'


    @api.model
    def render_html(self, docids, data=None):
        stock_picking_pool = self.env['stock.picking']
        docs = stock_picking_pool.browse(docids[0])

        stock_picking_data = stock_picking_pool.search([('partner_id','=',docs.partner_id.id)])

        sum_qty_delivered = 0
        for stocks in stock_picking_data:
            sum_qty_delivered = sum_qty_delivered + stocks.sale_id.order_line.qty_delivered

        print '----', sum_qty_delivered

        data = {}

        data['partner_id'] = docs.partner_id.name
        data['do_date'] = docs.create_date
        data['do_number'] = docs.name
        data['do_qty'] = docs.group_id.procurement_ids.sale_line_id.product_uom_qty
        #data['un_delivered_qty']
        #data['issued_do'] = ### DO issued on today's date
        data['delivered_qty'] = sum_qty_delivered
        #data['un_delivered_qty']
        #data['category']

        docargs = {
            'doc_model': 'stock.picking',
            'data': data,
        }

        return self.env['report'].render('delivery_qty_reports.report_individual_payslip', docargs)
