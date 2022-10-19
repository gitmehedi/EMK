from odoo import fields, http, _
from odoo.http import request
import datetime
import json
from bson import json_util
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang


class PurchaseQuotationsController(http.Controller):

    @http.route(['/purchase/get_quotations'], type='json', auth="user")
    def get_quotations(self, type=None, rfq_id=None, **post):

        data_list = []
        rfq_obj = request.env['purchase.rfq'].browse(rfq_id)
        pq_list = request.env['purchase.order'].search([('rfq_id', '=', rfq_id)], order='id ASC')
        if not pq_list:
            raise UserError('No Quotation created for this RFQ.\n'
                            ' Please create quotation to see the comparative study!!!')
        header = self.get_dynamic_header(pq_list)
        lists = self.get_all_row_data(rfq_obj, pq_list)
        data_list.append(header)
        return {'header': header,'row_objs': lists['products']};

    def get_dynamic_header(self, pq_list):
        header = {}
        header['pr_no'] = 'PR No'
        header['item'] = 'Item'
        header['req_qty'] = 'Required Qty'
        header['unit'] = 'Unit'
        header['last_price'] = 'Last Price'
        header['approved_price'] = 'Approved Price'
        header['total'] = 'Total'
        header['remarks'] = 'Remarks'

        header['dynamic'] = []
        for val in pq_list:
            header['dynamic'].append({'name': val.name, 'supplier': val.partner_id.name, 'total': 0})

        return header

    def get_all_row_data(self, rfq_obj, pq_list):

        grand_total = []
        for v in pq_list:
            grand_total.append({'pq_id': v.id, 'title': 'TOTAL', 'total_price': 0})

        product_row_list = []
        for val in self.get_purchase_data(rfq_obj):
            quotations = []

            product_row_list.append({
                'product_id': val[0],
                'pr_name': val[1],
                'product_name': val[2],
                'product_ordered_qty': val[3],
                'product_unit': val[4],
                'last_price': val[5],
                'approved_price': None,
                'approved_total': None,
                'remarks': '',
                'quotations': quotations
            })

        pq_temp_list = self.get_temp_pq(pq_list)
        for product_row in product_row_list:
            for pq in pq_temp_list:
                if pq.product_line.get(product_row['product_id']):
                    price_pq = formatLang(request.env, pq.product_line.get(product_row['product_id']))
                    total_pq = formatLang(request.env, pq.product_line.get(product_row['product_id']) * product_row[
                        'product_ordered_qty'])
                    product_row['quotations'].append({'price': price_pq, 'total': total_pq})

                    if pq.state in ['purchase', 'done']:
                        product_row['approved_price'] = formatLang(request.env,
                                                                   pq.product_line.get(product_row['product_id']))
                        product_row['approved_total'] = formatLang(request.env,
                                                                   pq.product_line.get(product_row['product_id']) *
                                                                   product_row['product_ordered_qty'])

                    for i in grand_total:
                        if pq.pq_id == i['pq_id']:
                            if i['total_price']:
                                i['total_price'] = float(i['total_price'].replace(',', '')) + float(
                                    total_pq.replace(',', ''))
                            else:
                                i['total_price'] = i['total_price'] + float(total_pq.replace(',', ''))

                            i['total_price'] = formatLang(request.env, i['total_price'])
                else:
                    product_row['quotations'].append({'price': None, 'total': None})

        return {'products': product_row_list, 'total': grand_total}

    def get_purchase_data(self, rfq_obj):
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
                ORDER BY pr.id ASC;
        """ % (rfq_obj.id)
        request.env.cr.execute(sql)

        return request.env.cr.fetchall()

    def get_temp_pq(self, pq_list):
        quotations = []
        for pq in pq_list:
            product_line = {}
            for pq_line in pq.order_line:
                product_line[pq_line.product_id.id] = pq_line.price_unit
            quotations.append(TempPQ(pq.id, pq.name, pq.state, product_line))
        return quotations


class TempPQ(object):

    def __init__(self, pq_id=None, name=None, state=None, product_line=None):
        self.pq_id = pq_id
        self.name = name
        self.state = state
        if product_line is None:
            self.product_line = {}
        else:
            self.product_line = product_line
