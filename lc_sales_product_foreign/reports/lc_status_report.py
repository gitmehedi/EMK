from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
from datetime import datetime




class PurchaseSummaryReport(models.AbstractModel):
    _name = 'report.lc_sales_product_foreign.lc_status_foreign_template'


    sql_str_fst = """SELECT lc.name,
                            lc.issue_date,
                            rp.name,
                            pl.product_qty,
                            pi.name,
                            pi.invoice_date,
                            pl.product_received_qty,
                            lc.shipment_date,
                            lc.expiry_date,
                            lc.id,
                            pu.name,
                            lc.model_type
                    FROM letter_credit AS lc
                    LEFT JOIN lc_product_line AS pl ON lc.id = pl.lc_id
                    LEFT JOIN product_product AS pp ON pp.id = pl.product_id
                    LEFT JOIN product_uom AS pu ON pu.id = pl.product_uom
                    LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN res_partner AS rp ON rp.id = lc.second_party_applicant
                    LEFT JOIN proforma_invoice AS pi ON lc.id = pi.lc_id
                    WHERE lc.region_type = 'foreign' AND lc.type='export' AND (lc.state='confirmed' OR lc.state = 'progress')"""

    sql_str_snd = """SELECT lc.name,
                            lc.issue_date,
                            rp.name,
                            pl.product_qty,
                            pi.name,
                            pi.invoice_date,
                            pl.product_received_qty,
                            lc.shipment_date,
                            lc.expiry_date,
                            lc.id,
                            pu.name,
                            lc.model_type
                    FROM letter_credit AS lc
                    LEFT JOIN lc_product_line AS pl ON lc.id = pl.lc_id
                    LEFT JOIN product_product AS pp ON pp.id = pl.product_id
                    LEFT JOIN product_uom AS pu ON pu.id = pl.product_uom
                    LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                    LEFT JOIN res_partner AS rp ON rp.id = lc.second_party_applicant
                    LEFT JOIN purchase_shipment AS ps ON lc.id = ps.lc_id
                    LEFT JOIN proforma_invoice AS pi ON lc.id = pi.lc_id
                    WHERE lc.state='done' AND
                          (ps.bl_date BETWEEN cast(date_trunc('month', current_date) as date) AND cast(date_trunc('month', current_date) + interval '1 month' - interval '1 day' as date))
                    """

    @api.multi
    def render_html(self, docids, data=None):

        data = {
            'product_id': data['product_id'],
            'product_name': data['product_name'],
            'product_temp_id': data['product_temp_id'],
            'product_temp_name': data['product_temp_name'],
            'status' :  data['status'],
        }

        report_utility_pool = self.env['report.utility']
        lc_list = []

        if data['status'] == 'product':
            if data['product_temp_id']:
                self.sql_str_fst += "  AND pt.id = '%s'" % (data['product_temp_id'])
                self.sql_str_snd += "  AND pt.id = '%s'" % (data['product_temp_id'])

        elif data['status'] == 'variant':
            if data['product_id']:
                self.sql_str_fst += "  AND pp.id = '%s'" % (data['product_id'])
                self.sql_str_snd += "  AND pp.id = '%s'" % (data['product_id'])

        sql_str = self.sql_str_fst + " UNION ALL " + self.sql_str_snd

        self._cr.execute(sql_str)
        lc_pool = self._cr.fetchall()

        for lc in lc_pool:
            list_obj = {
                'lc_name': lc[0],
                'lc_date': lc[1],
                'first_party': lc[2],
                'lc_qty': lc[3],
                'pi_no': lc[4],
                'pi_date': lc[5],
                'delivery_qty': self.getDeliveryQty(lc[9]),
                'product_received_qty': lc[6],
                'lst_sp_date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(lc[7])),
                'lc_expiry_date': report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(lc[8])),
                'product_uom': lc[10],
                'model_type': lc[11],
                'pending_qty': lc[3]-self.getDeliveryQty(lc[9])
            }
            lc_list.append(list_obj)

        month_value = datetime.now().strftime('%B')
        year_value = datetime.now().year

        docargs = {
            'data': data,
            'lc_list': lc_list,
            'month': month_value,
            'year': year_value,
        }

        return self.env['report'].render('lc_sales_product_foreign.lc_status_foreign_template', docargs)


    def getDeliveryQty(self,lc_id):
        lc = self.env['letter.credit'].search([('id', '=', lc_id)])
        delivered_qty = 0
        for pi_id in lc.pi_ids_temp:
            so_ids = self.env['sale.order'].search([('pi_id', '=', pi_id.id)])
            for so_id in so_ids:
                quantity = so_id.order_line.filtered(lambda x: x.product_id.id == so_id.order_line.product_id.id).qty_delivered
                delivered_qty = delivered_qty + quantity

        return delivered_qty