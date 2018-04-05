from odoo import api, fields, models
import time

from datetime import date,datetime

class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        stock_picking_pool = self.env['stock.picking'].search([('min_date', '<', data['report_of_day'])])
        do_list = []

        for stocks in stock_picking_pool:
            data = {}
            data['partner_id'] = stocks.partner_id.name
            data['do_date'] = stocks.min_date
            data['do_no'] = stocks.name
            data['do_qty'] = stocks.pack_operation_product_ids.product_qty
            data['un_delivered_qty'] = stocks.pack_operation_product_ids.product_qty - stocks.pack_operation_product_ids.qty_done
            data['delivered_qty'] = stocks.pack_operation_product_ids.qty_done
            data['product'] = stocks.pack_operation_product_ids.product_id.name

            ## Cross match with DO Date and today's date to get Issued D.O property
            if datetime.strptime(stocks.min_date, "%Y-%m-%d %H:%M:%S").date() == date.today():
                data['issued_do_today'] = stocks.pack_operation_product_ids.product_qty
            else:
                data['issued_do_today'] = ''

            #data['product_category']
            #
            # data['un_delivered_qty']


            sale_order_pool = self.env['sale.order'].search([('name', '=', stocks.origin)])
            if sale_order_pool:
                for s in sale_order_pool:
                    data['uom'] = s.order_line.product_uom.name
            else:
                data['uom'] = ''

            do_list.append(data)


        docargs = {'do_list': do_list}

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)