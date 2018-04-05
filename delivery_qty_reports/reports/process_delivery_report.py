from odoo import api, fields, models


class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        stock_picking_pool = self.env['stock.picking'].search([('min_date', '<', data['report_of_day'])])
        # sale_order_pool = self.env['sale.order'].search([('group_id','=',self.group)])

        do_list = []

        for stocks in stock_picking_pool:
            data = {}
            data['partner_id'] = stocks.partner_id.name
            data['do_date'] = stocks.min_date
            data['do_no'] = stocks.name
            # data['uom'] =
            # data['do_qty']
            # data['undelivered_qty']
            # data['issued_do_today']
            # data['delivered_qty']
            # data['un_delivered_qty']
            # data['product_category']
            do_list.append(data)

        docargs = { 'do_list': do_list }

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)
