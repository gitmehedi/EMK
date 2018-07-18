from odoo import api, fields, models
import time

from datetime import date, datetime


class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'

    @api.model
    def render_html(self, docids, data=None):

        report_of_day = data['report_of_day']

        date_start = report_of_day + ' 00:00:00'
        date_end = report_of_day + ' 23:59:59'

        stock_picking = self.env['stock.picking'].search(
            [('min_date', '>', date_start), ('max_date', '<', date_end)])

        data = {}
        for val in stock_picking:
            data[val.product_id.id] = {'name': val.product_id.name + " (" + val.product_id.attribute_value_ids.name + ")",
                                       'details': [],
                                       'total': {'do_qty': 0,
                                                 'un_delivered_qty': 0,
                                                 'delivered_qty': 0,
                                                 'delivefsdafred_qty': 0,
                                                 'deliverefsdd_qty': 0
                                                 }
                                       }

        for record in stock_picking:
            for rec in record.pack_operation_product_ids:
                val = {}
                val['partner_id'] = record.partner_id.name
                val['do_date'] = datetime.strptime(record.min_date, "%Y-%m-%d %H:%M:%S").date()
                val['do_no'] = record.delivery_order_id.name
                val['do_qty'] = rec.product_qty
                val['un_delivered_qty'] = rec.product_qty - rec.qty_done
                val['delivered_qty'] = rec.qty_done
                val['product'] = rec.product_id.name + " (" + rec.product_id.attribute_value_ids.name + ")"
                val['uom'] = 'MT'
                #val['issued_do_today'] = rec.product_id.name + " (" + rec.product_id.attribute_value_ids.name + ")"

                if datetime.strptime(record.min_date, "%Y-%m-%d %H:%M:%S").date() == date.today():
                    val['issued_do_today'] = rec.product_qty
                else:
                    val['issued_do_today'] = ''

                data[rec.product_id.id]['total']['do_qty'] = data[rec.product_id.id]['total'][
                                                                 'do_qty'] + rec.product_qty
                data[rec.product_id.id]['total']['un_delivered_qty'] = data[rec.product_id.id]['total'][
                                                                 'un_delivered_qty'] + (rec.product_qty - rec.qty_done)

                data[rec.product_id.id]['total']['delivered_qty'] = data[rec.product_id.id]['total'][
                                                                 'delivered_qty'] + rec.qty_done
                # if rec.product_qty:
                #     data[rec.product_id.id]['total']['issued_do_today'] = data[rec.product_id.id]['total'][
                #                                                         'issued_do_today'] + rec.product_qty

                data[rec.product_id.id]['details'].append(val)



        docargs = {
            'do_list': data,
            'report_of_day': report_of_day,
        }

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)
