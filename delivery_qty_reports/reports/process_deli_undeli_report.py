from odoo import api, fields, models
import datetime
from datetime import timedelta


class ProcessDeliveryUnDeliveryReport(models.AbstractModel):
    _name = 'report.delivery_qty_reports.report_daily_deli_undeli'


    sql_get_product_ids = """SELECT DISTINCT(sale_l.product_id) 
               FROM sale_order_line sale_l 
               JOIN sale_order sale_o ON sale_l.order_id = sale_o.id
               WHERE sale_o.operating_unit_id = %s"""

    sql_get_DOs = """SELECT
                        deli_o.id, customer.name AS customer_name,
                        deli_o.requested_date AS do_date,
                        deli_o.name,
                        deli_o_l.quantity AS do_qty,
                        uom.name,
                        stock_p_l.product_qty + stock_p_l.undelivered_qty AS "Begening Un_Deli QTY",
                        stock_p_l.product_qty AS "Delivered Qty",
                        stock_p.vat_challan_id,
                        stock_p_l.undelivered_qty AS "Un_Deli Qty",
                        pack.packaging_mode,
                        'today' AS status,
                        customer.id
                    FROM
                        stock_move stock_p_l
                        LEFT JOIN stock_picking stock_p ON stock_p.id = stock_p_l.picking_id
                        LEFT JOIN delivery_order deli_o ON deli_o.id = stock_p.delivery_order_id
                        LEFT JOIN delivery_order_line deli_o_l ON deli_o_l.parent_id = deli_o.id
                        LEFT JOIN product_uom uom ON uom.id = deli_o_l.uom_id
                        LEFT JOIN sale_order sale_o ON sale_o.id = deli_o.sale_order_id
                        LEFT JOIN res_partner customer ON customer.id = sale_o.partner_id
                        LEFT JOIN product_packaging_mode pack ON pack.id = stock_p.pack_type
                    WHERE
                        DATE(stock_p.date_done + interval '6h') = DATE(%s) AND
                        stock_p_l.product_id = %s
                    UNION
                    SELECT
                        DISTINCT(deli_o.id), customer.name AS customer_name,
                        deli_o.requested_date AS do_date,
                        deli_o.name,
                        deli_o_l.quantity AS do_qty,
                        uom.name,
                        0 AS "Begening Un_Deli QTY",
                        0 AS "Delivered Qty",
                        '-' AS "vat challan",
                        0 AS "Un_Deli Qty",
                        pack.packaging_mode,
                        'pending' AS status,
                        customer.id
                    FROM
                        sale_order_line sale_o_l
                        LEFT JOIN sale_order sale_o ON sale_o.id = sale_o_l.order_id
                        LEFT JOIN delivery_order deli_o ON deli_o.sale_order_id = sale_o.id
                        LEFT JOIN delivery_order_line deli_o_l ON deli_o_l.parent_id = deli_o.id
                        LEFT JOIN stock_picking stock_p ON stock_p.delivery_order_id = deli_o.id
                        LEFT JOIN product_uom uom ON uom.id = deli_o_l.uom_id
                        LEFT JOIN res_partner customer ON customer.id = sale_o.partner_id
                        LEFT JOIN product_packaging_mode pack ON pack.id = stock_p.pack_type
                    WHERE
                        (deli_o_l.date_done IS NULL OR DATE(deli_o_l.date_done + interval '6h') > DATE(%s)) AND
                        sale_o_l.product_id = %s AND 
                        DATE(deli_o.requested_date + interval '6h') <= DATE(%s) AND
                        deli_o.id NOT IN (SELECT stock_p.delivery_order_id
                                          FROM stock_move stock_p_l
                                          LEFT JOIN stock_picking stock_p ON stock_p.id = stock_p_l.picking_id
                                          WHERE DATE(stock_p.date_done + interval '6h') = DATE(%s) AND stock_p_l.product_id = %s)
                    ORDER BY customer_name ASC, do_date DESC"""


    sql_get_issued_do = """SELECT 
                                do_line.quantity
                          FROM 
                              delivery_order_line do_line
                              JOIN delivery_order delivery_o ON do_line.parent_id = delivery_o.id
                          WHERE
	                          delivery_o.id = %s AND
	                          delivery_o.requested_date = %s AND
	                          do_line.product_id = %s"""

    sql_get_delivered_qty = """SELECT SUM(stock_p_l.product_qty) 
                                FROM 
                                    stock_move stock_p_l
                                LEFT JOIN 
                                    stock_picking stock_p ON stock_p.id = stock_p_l.picking_id
                                WHERE 
                                    stock_p_l.delivery_order_id = %s AND 
                                    stock_p_l.product_id = %s AND 
                                    DATE(stock_p.date_done + interval '6h') < DATE(%s)"""

    @api.model
    def render_html(self, docids, data=None):
        date_given = data['report_of_day']

        operating_unit_id = data['operating_unit_id']
        operating_unit_name = data['operating_unit_name']
        given_date = self.getDateFromStr(date_given)

        datas = {}

        # Get Product By Login User Operating Unit
        self._cr.execute(self.sql_get_product_ids,(operating_unit_id,)) # Never remove the comma after the parameter
        products = self._cr.fetchall()

        for prod_id in products:

            self.prepareListForProduct(datas,prod_id)

            ##Get DO List By Product ID and Given Date
            self._cr.execute(self.sql_get_DOs, (date_given,prod_id,date_given,prod_id,date_given,date_given,prod_id)) # Never remove the comma after the parameter, it gives error
            delivery_orders = self._cr.fetchall()

            ##Get Delivered Qty By delivery_order_id, date and product_id, delivery_order_id[0] means DO ID
            for delivery_order in delivery_orders:

                val = {}
                do_date = self.getDateFromStr(delivery_order[2])

                if delivery_order[11] == 'pending':
                    previous_deli_qty = self.get_deli_qty(delivery_order[0],date_given,prod_id)

                    val['begen_un_deli_qty'] = delivery_order[4] - previous_deli_qty
                    val['issued_do_today'] = 0
                    val['delivered_qty'] = 0
                    val['un_delivered_qty'] = delivery_order[4] - previous_deli_qty

                else:
                    val['begen_un_deli_qty'] = delivery_order[6]
                    val['delivered_qty'] = delivery_order[7]
                    val['un_delivered_qty'] = delivery_order[9]
                    val['issued_do_today'] = 0

                if (do_date == given_date) and (val['delivered_qty'] + val['un_delivered_qty'] == delivery_order[4]):
                    val['issued_do_today'] = self.get_issue_do_qty(delivery_order[0], date_given, prod_id)

                # If given date is DO issue date, then 'Begening of Undelivery Qty' of First delivery is set by 0.
                # How To Check First Delivery Of DO: Condition delivered_qty + un_delivered_qty = do_qty
                if val['issued_do_today'] > 0 and (val['delivered_qty'] + val['un_delivered_qty'] == delivery_order[4]):
                    val['begen_un_deli_qty'] = 0


                val['partner_id'] = delivery_order[1]
                val['do_date'] = delivery_order[2]
                val['do_no'] = delivery_order[3]
                val['do_qty'] = delivery_order[4]
                val['uom'] = delivery_order[5]
                val['vat_challan'] = delivery_order[8]
                val['packing_mode'] = delivery_order[10]
                val['product'] = datas[prod_id]['name']

                datas[prod_id]['total']['do_qty'] = datas[prod_id]['total']['do_qty'] + delivery_order[4]
                datas[prod_id]['total']['begen_un_deli_qty'] = datas[prod_id]['total']['begen_un_deli_qty'] + val['begen_un_deli_qty']
                datas[prod_id]['total']['issued_do'] = datas[prod_id]['total']['issued_do'] + val['issued_do_today']
                datas[prod_id]['total']['delivered_qty'] = datas[prod_id]['total']['delivered_qty'] + val['delivered_qty']
                datas[prod_id]['total']['un_delivered_qty'] = datas[prod_id]['total']['un_delivered_qty'] + val['un_delivered_qty']


                datas[prod_id]['details'].append(val)

            if len(datas[prod_id]['details']) == 0:
                datas.pop(prod_id)

        docargs = {
            'do_list': datas,
            'report_of_day': date_given,
            'operating_unit_name':operating_unit_name
        }

        return self.env['report'].render('delivery_qty_reports.report_daily_deli_undeli', docargs)



    def prepareListForProduct(self,data,product_id):

        product = self.env['product.product'].search([('id', '=', product_id)])

        attribute = ""
        if len(product.attribute_value_ids) > 0:
            attribute = " ("
            for attr in product.attribute_value_ids:
                attribute += attr.name + ","

            attribute = attribute[:-1]
            attribute += ")"
        name = product.product_tmpl_id.name if product.product_tmpl_id.name else ''
        data[product_id] = {'name': name + attribute,
                                   'details': [],
                                   'total': {'do_qty': 0,
                                             'begen_un_deli_qty': 0,
                                             'issued_do':0,
                                             'delivered_qty': 0,
                                             'un_delivered_qty': 0,
                                             }
                                   }


    def get_deli_qty(self,do_id,date_given,prod_id):


        self._cr.execute(self.sql_get_delivered_qty,(do_id, prod_id,date_given))  # Never remove the comma after the parameter, it gives error
        result = self._cr.fetchall()
        if len(result) == 0:
            begen_un_deli_qty = 0
        elif result[0][0] == None:
            begen_un_deli_qty = 0
        else:
            begen_un_deli_qty = result[0][0]

        return begen_un_deli_qty

    def get_issue_do_qty(self,do_id,date_given,prod_id):

        # Get Today Issued DO
        self._cr.execute(self.sql_get_issued_do, (do_id, date_given, prod_id,))  # Never remove the comma after the parameter, it gives error
        result = self._cr.fetchall()
        if len(result) == 0:
            issued_do = 0
        elif result[0][0] == None:
            issued_do = 0
        else:
            issued_do = result[0][0]

        return issued_do

    def getDateFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d")
        else:
            return None