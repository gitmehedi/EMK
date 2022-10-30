from odoo import fields, http, _
from odoo.http import request
import datetime
import json
from bson import json_util
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseQuotationsController(http.Controller):

    def modify_po_line(self, listOfObjects, rfq_id, remarks_maker, remarks_checker, remarks_approver):
        rfq_obj = request.env['purchase.rfq'].suspend_security().browse(rfq_id)
        rfq_obj.write(
            {'user_remarks': remarks_maker, 'manager_remarks': remarks_checker,
             'procurement_head_remarks': remarks_approver})
        if listOfObjects:
            po_orders = request.env['purchase.order'].search([('rfq_id', '=', rfq_id), ('created_by_cs', '=', False)],
                                                             order='id ASC')
            for order in po_orders:
                for line in order.order_line:
                    line.suspend_security().write({'is_cs_processed': False})

        for obj in listOfObjects:
            if obj['po_line']:
                po_line_obj = request.env['purchase.order.line'].browse(int(obj['po_line']))
                po_line_obj.suspend_security().write({'is_cs_processed': True})

    def prepare_order_data(self, listOfObjects, orders_tobe_created):
        for obj in listOfObjects:
            po_lines = []
            if orders_tobe_created:
                if not any(d['vendor_id'] == obj['selected_vendor'] for d in orders_tobe_created):
                    po_lines.append({'po_line': obj['po_line'], 'pro_id': obj['pro_id'], 'pro_unit': obj['pro_unit'],
                                     'req_qty': obj['req_qty'],
                                     'selected_rate': obj['selected_rate'], 'selected_total': obj['selected_total']})
                    my_dict = {'vendor_id': obj['selected_vendor'], 'po_lines': po_lines}
                    orders_tobe_created.append(my_dict)
                else:
                    for m in orders_tobe_created:
                        if m['vendor_id'] == obj['selected_vendor']:
                            tmp_list = m['po_lines']
                            tmp_list.append(
                                {'po_line': obj['po_line'], 'pro_id': obj['pro_id'], 'pro_unit': obj['pro_unit'],
                                 'req_qty': obj['req_qty'],
                                 'selected_rate': obj['selected_rate'], 'selected_total': obj['selected_total']})

                            m.update({'po_lines': tmp_list})
            else:
                po_lines.append({'po_line': obj['po_line'], 'pro_id': obj['pro_id'], 'pro_unit': obj['pro_unit'],
                                 'req_qty': obj['req_qty'],
                                 'selected_rate': obj['selected_rate'], 'selected_total': obj['selected_total']})

                my_dict = {'vendor_id': obj['selected_vendor'], 'po_lines': po_lines}
                orders_tobe_created.append(my_dict)

        return orders_tobe_created

    @http.route(['/purchase/save_cs'], type='json', auth="user")
    def save_cs(self, type=None, listOfObjects=None, rfq_id=None, remarks_maker=None, remarks_checker=None,
                remarks_approver=None, **post):
        self.modify_po_line(listOfObjects, rfq_id, remarks_maker, remarks_checker, remarks_approver)
        return {
            'return_val': 'true'
        }

    @http.route(['/purchase/send_to_manager'], type='json', auth="user")
    def send_to_manager(self, type=None, listOfObjects=None, rfq_id=None, remarks_maker=None, remarks_checker=None,
                        remarks_approver=None, **post):
        self.modify_po_line(listOfObjects, rfq_id, remarks_maker, remarks_checker, remarks_approver)

        rfq_obj = request.env['purchase.rfq'].suspend_security().browse(rfq_id)
        cs_obj = request.env['purchase.rfq.cs'].suspend_security().search([('rfq_id', '=', rfq_id)], limit=1,
                                                                          order='id ASC')
        rfq_obj.suspend_security().write({'state': 'sent_for_confirmation'})
        cs_obj.suspend_security().write({'state': 'sent_for_confirmation'})

        return {
            'return_val': 'true'
        }

    @http.route(['/purchase/confirm_cs'], type='json', auth="user")
    def confirm_cs(self, type=None, listOfObjects=None, rfq_id=None, remarks_maker=None, remarks_checker=None,
                   remarks_approver=None, **post):
        self.modify_po_line(listOfObjects, rfq_id, remarks_maker, remarks_checker, remarks_approver)

        rfq_obj = request.env['purchase.rfq'].suspend_security().browse(rfq_id)
        cs_obj = request.env['purchase.rfq.cs'].suspend_security().search([('rfq_id', '=', rfq_id)], limit=1,
                                                                          order='id ASC')
        rfq_obj.suspend_security().write({'state': 'confirmed'})
        cs_obj.suspend_security().write({'state': 'confirmed'})

        return {
            'return_val': 'true'
        }

    @http.route(['/purchase/approve_cs'], type='json', auth="user")
    def approve_cs(self, type=None, listOfObjects=None, rfq_id=None, remarks_maker=None, remarks_checker=None,
                   remarks_approver=None, **post):
        rfq_obj = request.env['purchase.rfq'].suspend_security().browse(rfq_id)
        purchase_menu = request.env['ir.model.data'].sudo().get_object('purchase', 'menu_purchase_form_action')
        purchase_action = request.env['ir.model.data'].sudo().get_object('purchase', 'purchase_form_action')

        self.modify_po_line(listOfObjects, rfq_id, remarks_maker, remarks_checker, remarks_approver)

        orders_tobe_created = []
        orders_tobe_created = self.prepare_order_data(listOfObjects, orders_tobe_created)

        create_purchase_orders = []
        for order in orders_tobe_created:
            seq_name = request.env['ir.sequence'].next_by_code_new('purchase.order', datetime.today(),
                                                                   rfq_obj.operating_unit_id) or '/'

            type_obj = request.env['stock.picking.type']
            company_id = request.env.context.get('company_id') or request.env.user.company_id.id
            types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id.company_id', '=', rfq_obj.company_id.id),
                                     ('operating_unit_id', '=', rfq_obj.operating_unit_id.id)])
            if not types:
                types = type_obj.search([('code', '=', 'incoming'), ('warehouse_id', '=', False)])

            order_obj = {
                'name': seq_name,
                'partner_id': order['vendor_id'],
                'operating_unit_id': rfq_obj.operating_unit_id.id,
                'company_id': company_id,
                'picking_type_id': types[0].id,
                'rfq_id': rfq_id,
                'date_order': datetime.now(),
                'created_by_cs': True,
                'state': 'done'
            }
            created_po_obj = request.env['purchase.order'].suspend_security().create(order_obj)
            for line in order['po_lines']:
                submitted_po_line = request.env['purchase.order.line'].suspend_security().browse(int(line['po_line']))

                uom_id = request.env['product.uom'].suspend_security().search([('name', '=', line['pro_unit'])])
                pro_qty = line['req_qty'].replace(',', '')
                price_unit = line['selected_rate'].replace(',', '')
                order_line = {
                    'product_id': int(line['pro_id']),
                    'name': 'product Name',
                    'date_planned': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'product_qty': pro_qty,
                    'price_unit': price_unit,
                    'product_uom': uom_id.id,
                    'currency_id': submitted_po_line.order_id.currency_id.id,
                    'order_id': created_po_obj.id,
                }
                created_po_line = request.env['purchase.order.line'].suspend_security().create(order_line)
                submitted_po_line.order_id.suspend_security().write({'state': 'cancel'})

                # search po_line id in row then on the purchase order column put created_po id
                url = request.httprequest.host_url + "web#id=" + str(
                    created_po_obj.id) + "&view_type=form" + "&model=purchase.order&menu_id=" + str(
                    purchase_menu.id) + "&action=" + str(purchase_action.id)
                url_link = "<a href=" + url + ">" + created_po_obj.name + "</a>"
                submitted_po_line.suspend_security().write({'created_po': url_link})

        cs_obj = request.env['purchase.rfq.cs'].suspend_security().search([('rfq_id', '=', rfq_id)], limit=1,
                                                                          order='id ASC')
        rfq_obj.suspend_security().write({'state': 'approved'})
        cs_obj.suspend_security().write({'state': 'approved'})

        return {
            'return_val': 'true',
            'purchase_orders': create_purchase_orders

        }

    @http.route(['/purchase/get_quotations'], type='json', auth="user")
    def get_quotations(self, type=None, rfq_id=None, **post):

        data_list = []
        rfq_obj = request.env['purchase.rfq'].browse(rfq_id)
        pq_list = request.env['purchase.order'].search([('rfq_id', '=', rfq_id), ('created_by_cs', '=', False)],
                                                       order='id ASC')
        if not pq_list:
            raise UserError('No Quotation created for this RFQ.\n'
                            ' Please create quotation to see the comparative study!!!')
        header = self.get_dynamic_header(pq_list)
        lists = self.get_all_row_data(rfq_obj, pq_list)
        data_list.append(header)
        user_remarks = rfq_obj.user_remarks
        manager_remarks = rfq_obj.manager_remarks
        procurement_head_remarks = rfq_obj.procurement_head_remarks
        return {'header': header, 'row_objs': lists['products'], 'user_remarks': user_remarks,
                'manager_remarks': manager_remarks, 'procurement_head_remarks': procurement_head_remarks};

    def get_dynamic_header(self, pq_list):
        header = {}
        header['pr_no'] = 'PR No'
        header['item'] = 'Item'
        header['req_qty'] = 'Required Qty'
        header['unit'] = 'Unit'
        header['last_price'] = 'Last Price'
        header['approved_price'] = 'Selected Rate'
        header['total'] = 'Total'
        header['po'] = 'Purchase Order'

        header['dynamic'] = []
        for val in pq_list:
            header['dynamic'].append({'name': val.name, 'supplier': val.partner_id.name, 'total': 0})

        return header

    def get_all_row_data(self, rfq_obj, pq_list):

        grand_total = []
        for v in pq_list:
            grand_total.append({'pq_id': v.id, 'title': 'TOTAL', 'total_price': 0})

        product_row_list = []
        flag = 0
        for val in self.get_purchase_data(rfq_obj):
            quotations = []
            for obj in product_row_list:
                if obj['product_id'] == val[0]:
                    obj.update({'pr_name': obj['pr_name'] + ',' + val[1],
                                'product_ordered_qty': obj['product_ordered_qty'] + val[3]})
                    flag = 1

            if flag == 0:
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
            flag = 0
        pq_temp_list = self.get_temp_pq(pq_list)
        for product_row in product_row_list:
            for pq in pq_temp_list:
                if pq.product_line.get(product_row['product_id']):
                    price_pq = formatLang(request.env, pq.product_line.get(product_row['product_id']))
                    total_pq = formatLang(request.env, pq.product_line.get(product_row['product_id']) * product_row[
                        'product_ordered_qty'])
                    po_line_id = pq.po_line.get(product_row['product_id'])
                    vendor = pq.vendors.get(product_row['product_id'])
                    cq_processed = pq.cs_processed.get(product_row['product_id'])
                    created_po = pq.created_po.get(product_row['product_id'])
                    product_row['quotations'].append(
                        {'price': price_pq, 'total': total_pq, 'po_line_id': po_line_id, 'vendor_id': vendor,
                         'cq_processed': cq_processed, 'created_po': created_po})

                else:
                    product_row['quotations'].append(
                        {'price': None, 'total': None, 'po_line_id': None, 'vendor_id': None, 'cq_processed': None,
                         'created_po': None})
        return {'products': product_row_list}

    def get_purchase_data(self, rfq_obj):
        sql = """
                SELECT pp.id AS product_id,pr.name AS pr_name ,pt.name AS product_name ,
                       COALESCE(prl.product_ordered_qty,0.0) AS required_qty ,pu.name AS product_unit ,
                       COALESCE(prl.last_price_unit,0.0) AS last_price
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
            po_line = {}
            vendors = {}
            cs_processed = {}
            created_po = {}
            for pq_line in pq.order_line:
                product_line[pq_line.product_id.id] = pq_line.price_unit
                po_line[pq_line.product_id.id] = pq_line.id
                vendors[pq_line.product_id.id] = pq_line.order_id.partner_id.id
                cs_processed[pq_line.product_id.id] = pq_line.is_cs_processed
                created_po[pq_line.product_id.id] = pq_line.created_po

            quotations.append(
                TempPQ(pq.id, pq.name, pq.state, product_line, po_line, vendors, cs_processed, created_po))
        return quotations


class TempPQ(object):

    def __init__(self, pq_id=None, name=None, state=None, product_line=None, po_line=None, vendors=None,
                 cs_processed=None, created_po=None):
        self.pq_id = pq_id
        self.name = name
        self.state = state
        if product_line is None:
            self.product_line = {}
        else:
            self.product_line = product_line
        if po_line is None:
            self.po_line = {}
        else:
            self.po_line = po_line

        if vendors is None:
            self.vendors = {}
        else:
            self.vendors = vendors

        if cs_processed is None:
            self.cs_processed = {}
        else:
            self.cs_processed = cs_processed

        if created_po is None:
            self.created_po = {}
        else:
            self.created_po = created_po
