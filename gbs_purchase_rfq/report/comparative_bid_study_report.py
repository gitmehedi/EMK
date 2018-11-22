from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


class ComparativeBidReport(models.AbstractModel):
    _name = 'report.gbs_purchase_rfq.com_bid_report_temp'


    @api.multi
    def render_html(self, docids, data=None):
        report_utility_pool = self.env['report.utility']
        rfq_obj_pool = self.env['purchase.rfq']
        rfq_obj = rfq_obj_pool.browse(docids[0])
        data['address'] = report_utility_pool.getAddressByUnit(rfq_obj.operating_unit_id)

        rfq_data = {}
        rfq_data['name'] = rfq_obj.name
        rfq_data['rfq_date'] = rfq_obj.rfq_date

        pq_list = self.env['purchase.order'].search([('rfq_id', '=', rfq_obj.id)], order='id ASC')
        if not pq_list:
            raise UserError('No Quotation created for this RFQ.\n'
                            ' PLease create quotation to see the comparative study!!!')

        header = {}
        header['pr_no'] = 'PR No'
        header['item'] = 'Item'
        header['req_qty'] = 'Required Qty'
        header['unit'] = 'Unit'
        header['last_price'] = 'Last Price'
        header['approved_price'] = 'Approved Price'
        header['total'] = 'Total'
        header['remarks'] = 'Remarks'

        header['dynamic']={}
        for val in pq_list:
            header['dynamic'][str(val.name)] = { 'supplier' : val.partner_id.name , 'total': 0}




        #


        lists = self.get_report_data(rfq_obj, pq_list)

        docargs = {
            'report_objs': lists['products'],
            'grand_totals': lists['total'],
            'header': header,
            'address': data['address'],
            'data': rfq_data,
        }
        return self.env['report'].render('gbs_purchase_rfq.com_bid_report_temp', docargs)

    def get_report_data(self, rfq_obj,pq_list):

        grand_total = {v.id:{
            'title': 'TOTAL',
            'total_price': 0,
        }for v in pq_list}

        product_row_list=[]

        for val in self.get_purchase_data(rfq_obj):
            product_row_list.append({
                'product_id': val[0],
                'pr_name': val[1],
                'product_name': val[2],
                'product_ordered_qty': val[3],
                'product_unit': val[4],
                'last_price': val[5],
                'approved_price': 0,
                'approved_total': 0,
                'remarks': '',
                # 'quotation': quotation
                })

        pq_temp_list = self.get_temp_pq(pq_list)

        for product_row in product_row_list:
            for pq in pq_temp_list:
                if pq.product_line.get(product_row['product_id']):
                    product_row['unit_price'] = pq.product_line.get(product_row['product_id'])

        # for val in products:
        #     for val_quotation_dic in val['quotation'].keys():
        #         pq_line_obj = pq_line_list.filtered(lambda r: r.product_id.id == val['product_id'] and r.order_id.id== val_quotation_dic)
        #         if pq_line_obj:
        #             val['quotation'][val_quotation_dic]['price'] = pq_line_obj.price_unit
        #             val['quotation'][val_quotation_dic]['total'] = pq_line_obj.price_unit * val['product_ordered_qty']
        #             if pq_line_obj.order_id.state in ['purchase','done']:
        #                 val['approved_price'] = pq_line_obj.price_unit
        #                 val['approved_total'] = pq_line_obj.price_unit * val['product_ordered_qty']

                # grand_total[pq_line_obj.order_id.id]['total_price'] = grand_total[pq_line_obj.order_id.id]['total_price'] + (pq_line_obj.price_unit * val['product_ordered_qty'])

        return {'products':product_row_list,'total':grand_total}


    def get_purchase_data(self,rfq_obj):

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
        """%(rfq_obj.id)

        self.env.cr.execute(sql)

        return self._cr.fetchall()

    def get_temp_pq(self, pq_list):

        quotations = []
        for pq in pq_list:
            product_line = {}
            for pq_line in pq.order_line:
                product_line[pq_line.product_id.id] = pq_line.price_unit
            quotations.append(TempPQ(pq.id,pq.name,product_line))
        return quotations


class TempPQ(object):

    def __init__(self, pq_id=None, name=None, product_line=None):
        self.pq_id = pq_id
        self.name = name
        if product_line is None:
            self.product_line = {}
        else:
            self.product_line = product_line


