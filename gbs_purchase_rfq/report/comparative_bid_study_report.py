from odoo import api, fields, models, _


class ComparativeBidReport(models.AbstractModel):
    _name = 'report.gbs_purchase_rfq.com_bid_report_temp'

    @api.multi
    def render_html(self, docids, data=None):
        report_utility_pool = self.env['report.utility']
        rfq_obj_pool = self.env['purchase.rfq']
        rfq_obj = rfq_obj_pool.browse(docids[0])
        data['address'] = report_utility_pool.getAddressByUnit(rfq_obj.operating_unit_id)

        header = {}
        header['pr_no'] = 'PR No'
        header['item'] = 'Item'
        header['req_qty'] = 'Required Qty'
        header['unit'] = 'Unit'
        header['last_price'] = 'Last Price'
        header_data = self.env['purchase.order'].search([('rfq_id','=',rfq_obj.id )], order='id ASC')
        header['dynamic']={}
        for val in header_data:
            header['dynamic'][str(val.name)] = { 'Supplier' : val.partner_id.name , 'Total': 0}

        lists = self.get_report_data(rfq_obj, header_data)

        docargs = {
            'report_objs': lists,
            'header': header,
            'address': data['address'],
        }
        return self.env['report'].render('gbs_purchase_rfq.com_bid_report_temp', docargs)

    def get_report_data(self, rfq_obj,header_data):
        sql = """
                SELECT pp.id AS product_id,pr.name AS pr_name ,pt.name AS product_name ,
                       prl.product_ordered_qty AS required_qty ,pu.name AS product_unit ,
                       prl.last_price_unit AS last_price
                FROM purchase_rfq rfq
                LEFT JOIN purchase_rfq_line rfql ON rfq.id = rfql.rfq_id
                LEFT JOIN pr_rfq_line_rel pr_rel ON rfql.id = pr_rel.rfq_line_id
                LEFT JOIN purchase_requisition_line prl ON pr_rel.pr_line_id = prl.id
                LEFT JOIN purchase_requisition pr ON prl.requisition_id = pr.id
                LEFT JOIN product_product pp ON rfql.product_id = pp.id
                LEFT JOIN product_template pt ON pp.product_tmpl_id = pt.id
                LEFT JOIN product_uom pu ON pu.id = pt.uom_id
                WHERE rfq.id = %s
                ORDER BY pr.id;
        """% (rfq_obj.id)

        self.env.cr.execute(sql)
        products = { val[0]: {
            'pr_name': val[1],
            'product_name': val[2],
            'product_ordered_qty': val[3],
            'product_unit': val[4],
            'last_price': val[5],
            'quotation': {v.id: {
                'price': 0,
                'total': 0
            } for v in header_data}} for val in self._cr.fetchall()}

        if len(header_data.ids) == 1:
            po_ids = "("+ str(header_data.ids[0])+")"
        else:
            po_ids = tuple(header_data.ids)

        if len(products.keys())==1:
            product_ids = "(" + str(products.keys()[0]) + ")"
        else:
            product_ids = tuple(products.keys())

        sql_q = """
            SELECT pol.product_id,po.id,rp.name AS Supplier,pol.price_unit
            FROM purchase_order po
            JOIN purchase_order_line pol ON po.id = pol.order_id
            LEFT JOIN res_partner rp ON po.partner_id = rp.id
            WHERE
            po.id IN %s AND
            pol.product_id IN %s;
        """% (po_ids,product_ids)
        self._cr.execute(sql_q)
        for record in self._cr.fetchall():
            rec = products[record[0]]['quotation']
            for i in rec:
                if i == record[1]:
                    products[record[0]]['quotation'][i]['price'] = record[3]
                    products[record[0]]['quotation'][i]['total'] = record[3] * products[record[0]]['product_ordered_qty']

        return products