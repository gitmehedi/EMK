from odoo import api, fields, models
import time

from datetime import date,datetime



class ProcessMonthlyDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_monthly_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        do_list = []
        qty_mt_sum = []
        qty_kg_sum = []

        report_month = data['report_of_month']
        report_of_product_id = data['product_id']

        stock_move_pool = self.env['stock.move'].search([('product_id', '=', report_of_product_id)])
        product_pool = self.env['product.product'].search([('id','=',report_of_product_id)])

        #report_of_day = datetime.strptime(data['report_of_day'], "%Y-%m-%d %H:%M:%S").date()

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

            #@todo : need to change it and make it dynamic. Need to use 'reference' val insted of hardcoded 1000
            if product_uom.name == 'MT':
                datas['do_qty_mt'] = stocks.product_uom_qty
                datas['do_qty_kg'] = stocks.product_uom_qty * 1000

            datas['do_qty_bag'] = '-'
            datas['category'] = 'A'

            qty_mt_sum.append(datas['do_qty_mt'])
            qty_kg_sum.append( datas['do_qty_kg'])

            do_list.append(datas)

        docargs = \
            {
                'do_list': do_list,
                'qty_mt_sum': sum(qty_mt_sum),
                'qty_kg_sum': sum(qty_kg_sum),
                'product_name': product_pool.name,
                'report_month': report_month,

            }

        return self.env['report'].render('delivery_qty_reports.report_monthly_delivery_products', docargs)