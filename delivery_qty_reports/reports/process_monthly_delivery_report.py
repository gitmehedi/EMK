from odoo import api, fields, models
import time

from datetime import date,datetime



class ProcessMonthlyDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_monthly_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        product_name_with_variant = None

        do_list = []
        qty_mt_sum = []
        qty_kg_sum = []

        report_date_to = data['report_to']
        report_date_from = data['report_from']
        report_of_product_id = data['product_id']

        stock_move_pool = self.env['stock.move'].search([('date','<',report_date_to),('date','>',report_date_from),('product_id', '=', report_of_product_id)])

        for stocks in stock_move_pool:

            product_uom = stocks.product_uom

            DO_date = datetime.strptime(stocks.date, "%Y-%m-%d %H:%M:%S").date()
            do_create_date = datetime.strptime(stocks.create_date, "%Y-%m-%d %H:%M:%S").date()

            datas = {}
            datas['create_date'] = do_create_date
            datas['partner_id'] = stocks.partner_id.name
            datas['do_no'] = stocks.picking_id.name  # @todo: Need to talk with Matiar bhai
            datas['do_date'] = DO_date
            datas['challan_id'] = stocks.picking_id.name

            #@todo : need to change it and make it dynamic
            if product_uom.name == 'MT':
                datas['do_qty_mt'] = stocks.product_uom_qty
                datas['do_qty_kg'] = stocks.product_uom_qty * 1000

            datas['do_qty_bag'] = '-'
            datas['category'] = 'A'

            qty_mt_sum.append(datas['do_qty_mt'])
            qty_kg_sum.append( datas['do_qty_kg'])

            do_list.append(datas)

            product_name_with_variant = stocks.name

        only_report_date_to = datetime.strptime(report_date_to, "%Y-%m-%d %H:%M:%S").date()
        only_report_date_from = datetime.strptime(report_date_from, "%Y-%m-%d %H:%M:%S").date()

        docargs = \
            {
                'do_list': do_list,
                'qty_mt_sum': sum(qty_mt_sum),
                'qty_kg_sum': sum(qty_kg_sum),
                'product_name': product_name_with_variant,
                'report_date_to': only_report_date_to,
                'report_date_from': only_report_date_from

            }

        return self.env['report'].render('delivery_qty_reports.report_monthly_delivery_products', docargs)