from odoo import api, fields, models
import time

from datetime import date, datetime


class ProcessDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_delivery_products'


    sql_get_product_ids = """SELECT DISTINCT(sale_l.product_id) 
               FROM sale_order_line sale_l 
               JOIN sale_order sale_o ON sale_l.order_id = sale_o.id
               WHERE sale_o.operating_unit_id = %s"""

    sql_get_DOs = """SELECT 
                          DISTINCT(deli_o.id), deli_o.name, customer.name, 
                          deli_o.requested_date, sale_l.product_uom_qty, 
                          uom.name, sale_l.qty_delivered, customer.id AS customer_id
                     FROM 
                          sale_order_line sale_l
                          JOIN sale_order sale_o ON sale_l.order_id = sale_o.id
                          JOIN delivery_order deli_o ON deli_o.sale_order_id = sale_o.id
                          LEFT JOIN res_partner customer ON customer.id = sale_o.partner_id
                          LEFT JOIN product_uom uom ON uom.id = sale_l.product_uom
                     WHERE 
                          sale_l.qty_delivered < sale_l.product_uom_qty AND 
                          sale_l.product_id = %s
                     UNION                     
                     SELECT 
                          DISTINCT(deli_o.id), deli_o.name, customer.name, 
                          deli_o.requested_date, sale_l.product_uom_qty, 
                          uom.name, sale_l.qty_delivered, customer.id AS customer_id
                     FROM 
                         stock_pack_operation stock_p_l
                         JOIN stock_picking stock_p ON stock_p.id = stock_p_l.picking_id
                         JOIN delivery_order deli_o ON deli_o.id = stock_p.delivery_order_id
                         JOIN sale_order sale_o ON deli_o.sale_order_id = sale_o.id
                         LEFT JOIN sale_order_line sale_l ON sale_l.order_id = sale_o.id
                         LEFT JOIN product_uom uom ON uom.id = sale_l.product_uom
                         LEFT JOIN res_partner customer ON customer.id = sale_o.partner_id
                     WHERE 
                         DATE(stock_p_l.write_date + interval '6h') = DATE(%s) AND 
                         stock_p_l.product_id =%s ORDER BY customer_id"""


    sql_get_delivered_qty = """SELECT 
                                SUM(stock_p_l.qty_done)
                            FROM 
                                stock_pack_operation stock_p_l
                                JOIN stock_picking stock_p ON stock_p.id = stock_p_l.picking_id
                            WHERE 
	                            stock_p.delivery_order_id = %s AND 
	                            stock_p.state = 'done' AND
	                            DATE(stock_p_l.write_date + interval '6h') = DATE(%s)
	                            AND product_id = %s"""


    sql_get_issued_do = """SELECT 
                                do_line.quantity
                          FROM 
                              delivery_order_line do_line
                              JOIN delivery_order delivery_o ON do_line.parent_id = delivery_o.id
                          WHERE
	                          delivery_o.id = %s AND
	                          delivery_o.requested_date = %s AND
	                          do_line.product_id = %s"""


    @api.model
    def render_html(self, docids, data=None):
        date_given = data['report_of_day']

        operating_unit_id = data['operating_unit_id']

        datas = {}

        # Get Product By Login User Operating Unit
        self._cr.execute(self.sql_get_product_ids,(operating_unit_id,)) # Never remove the comma after the parameter
        products = self._cr.fetchall()

        for prod_id in products:

            self.prepareListForProduct(datas,prod_id)

            ##Get DO List By Product ID and Given Date
            self._cr.execute(self.sql_get_DOs, (prod_id,date_given, prod_id,)) # Never remove the comma after the parameter, it gives error
            delivery_orders = self._cr.fetchall()

            ##Get Delivered Qty By delivery_order_id, date and product_id, delivery_order_id[0] means DO ID
            for delivery_order in delivery_orders:

                val = {}
                val['partner_id'] = delivery_order[2]
                val['do_date'] = delivery_order[3]
                val['do_no'] = delivery_order[1]
                val['do_qty'] = delivery_order[4]
                val['uom'] = delivery_order[5]
                val['product'] = datas[prod_id]['name']

                un_delivered_qty = delivery_order[4] - delivery_order[6]
                val['un_delivered_qty'] = un_delivered_qty

                # Get Today Issued DO
                self._cr.execute(self.sql_get_issued_do, (delivery_order[0], date_given, prod_id,))  # Never remove the comma after the parameter, it gives error
                result = self._cr.fetchall()
                if len(result) == 0:
                    issued_do_today = 0
                else:
                    issued_do_today = result[0][0]
                val['issued_do_today'] = issued_do_today

                # Get Today Delivered QTY
                self._cr.execute(self.sql_get_delivered_qty, (delivery_order[0], date_given, prod_id,))  # Never remove the comma after the parameter, it gives error
                result1 = self._cr.fetchall()
                if len(result1) > 0 and result1[0][0] is not None:
                    delivered_qty = result1[0][0]
                else:
                    delivered_qty = 0
                val['delivered_qty'] = delivered_qty



                datas[prod_id]['total']['do_qty'] = datas[prod_id]['total']['do_qty'] + delivery_order[4]
                datas[prod_id]['total']['issued_do'] = datas[prod_id]['total']['issued_do'] + issued_do_today
                datas[prod_id]['total']['un_delivered_qty'] = datas[prod_id]['total']['un_delivered_qty'] + un_delivered_qty

                datas[prod_id]['total']['delivered_qty'] = datas[prod_id]['total']['delivered_qty'] + delivered_qty

                datas[prod_id]['details'].append(val)

            if len(datas[prod_id]['details']) == 0:
                datas.pop(prod_id)

        docargs = {
            'do_list': datas,
            'report_of_day': date_given,
        }

        return self.env['report'].render('delivery_qty_reports.report_daily_delivery_products', docargs)



    def prepareListForProduct(self,data,product_id):

        product = self.env['product.product'].search([('id', '=', product_id)])

        attribute = ""
        if len(product.attribute_value_ids) > 0:
            attribute = " (" + product.attribute_value_ids.name + ")"

        data[product_id] = {'name': product.product_tmpl_id.name + attribute,
                                   'details': [],
                                   'total': {'do_qty': 0,
                                             'issued_do':0,
                                             'un_delivered_qty': 0,
                                             'delivered_qty': 0,
                                             }
                                   }