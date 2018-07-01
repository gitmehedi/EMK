from odoo import api, models


class PurchasePriceReport(models.AbstractModel):
    _name = 'report.purchase_average_price_report.purchase_price_report_temp'

    @api.multi
    def render_html(self, docids, data=None):
        get_data = self.get_report_data(data)
        report_utility_pool = self.env['report.utility']
        op_unit_id = data['operating_unit_id']
        op_unit_obj = self.env['operating.unit'].search([('id', '=', op_unit_id)])
        data['address'] = report_utility_pool.getAddressByUnit(op_unit_obj)
        docargs = {
            'doc_ids': self._ids,
            'docs': self,
            'record': data,
            'lines': get_data['product'],
            'address': data['address'],
        }
        return self.env['report'].render('purchase_average_price_report.purchase_price_report_temp', docargs)

    def get_report_data(self, data):
        date_from = data['date_from']
        date_start = date_from + ' 00:00:00'
        date_to = data['date_to']
        date_end = date_to + ' 23:59:59'
        location_stock = data['location_id']
        product_id = data['product_id']
        product_pool = self.env['product.product']
        product = []

        if product_id:
            product_param = "(" + str(data['product_id']) + ")"
        else:
            product_list = product_pool.search([])
            if len(product_list) == 1:
                product_param = "(" + str(product_list.id) + ")"
            else:
                product_param = str(tuple(product_list.ids))

        sql_avg ='''SELECT sm.product_id,
                           pt.name AS product_name,
                           pv.name AS variant_name,
                           pu.name AS uom_name,
                           Date_trunc('day', sm.date + interval'6h') AS move_date,
                           coalesce(sum(product_qty * price_unit) /sum(product_qty), 0) as avg_price
                    FROM   stock_move sm
                    LEFT JOIN product_product pp
                          ON sm.product_id = pp.id
                    LEFT JOIN product_template pt
                          ON pp.product_tmpl_id = pt.id
                    LEFT JOIN product_uom pu
                          ON pu.id = pt.uom_id
                    LEFT JOIN product_attribute_value_product_product_rel pr 
			              ON pr.product_product_id = pp.id
		            LEFT JOIN product_attribute_value pv 
			              ON pv.id = pr.product_attribute_value_id
                    WHERE  sm.date + interval'6h' BETWEEN '%s' AND '%s'
                          AND sm.state = 'done'
                          AND sm.location_id <> %s
                          AND sm.location_dest_id = %s
                          AND pp.id IN %s
                    Group by Date_trunc('day', sm.date + interval'6h'),sm.product_id,pt.name,pu.name,pv.name
                    Order by Date_trunc('day', sm.date + interval'6h')   
        '''% (date_start, date_end,location_stock,location_stock,product_param)

        self.env.cr.execute(sql_avg)
        for vals in self.env.cr.dictfetchall():
            if vals:
                product.append(vals)

        return {'product': product}