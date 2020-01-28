from odoo import api, exceptions, fields, models
from odoo.tools.misc import formatLang


class MrrReport(models.AbstractModel):
    _name = 'report.stock_picking_mrr.report_mrr_doc'

    @api.multi
    def render_html(self, docids, data=None):
        report_utility_pool = self.env['report.utility']
        picking = self.env['stock.picking'].search(['|',('name', '=', data['origin']),('origin','=',data['origin'])],limit=1 ,order='id asc')
        new_picking = self.env['stock.picking'].search([('id', '=', data['self_picking_id'])])
        mrr_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(data['mrr_date']))
        data['address'] = report_utility_pool.getAddressByUnit(picking.operating_unit_id)
        pack_list = []
        total_amount = []
        customer =False
        challan =False
        challan_date = False
        po_no = []
        po_date = False

        # take decision that its from Shipment or direct
        if picking.shipment_id:
            if picking.shipment_id.lc_id.po_ids:
                po_ids = picking.shipment_id.lc_id.po_ids
                customer = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['customer']
                challan = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['challan']
                challan_date = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['challan_date']
                po_no = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['po_no']
                po_date = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['po_date']
                pack_list = self.get_rep_line(report_utility_pool,picking,new_picking,po_ids)['pack_list']
                total_amount = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['total_amount']

        elif picking.purchase_id:
            po_ids = [picking.purchase_id]
            customer = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['customer']
            challan = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['challan']
            challan_date = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['challan_date']
            po_no = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['po_no']
            po_date = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['po_date']
            pack_list = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['pack_list']
            total_amount = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['total_amount']

        else:
            po_ids = []
            customer = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['customer']
            challan = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['challan']
            challan_date = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['challan_date']
            po_no = False
            po_date = False
            pack_list = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['pack_list']
            total_amount = self.get_rep_line(report_utility_pool, picking, new_picking, po_ids)['total_amount']

        total = round(sum(total_amount),2)
        amt_to_word = self.env['res.currency'].amount_to_word(float(total))
        po_no_str = ''
        if po_no:
            po_no_str = ','.join(po_no)
        docargs = {
            'lists' : pack_list,
            'mrr_no' : data['mrr_no'],
            'mrr_date' : mrr_date,
            'customer' : customer,
            'challan' : challan,
            'challan_date' : challan_date,
            'po_no' : po_no_str,
            'po_date': po_date,
            'total_amount' : formatLang(self.env, total),
            'amt_to_word' : amt_to_word,
            'address': data['address']
        }
        return self.env['report'].render('stock_picking_mrr.report_mrr_doc', docargs)

    def get_rep_line(self,report_utility_pool,picking,new_picking,po_ids):
        pack_list = []
        total_amount = []
        po_no = []
        po_date = ''
        if po_ids:
            for po in po_ids:
                po_no.append(po.name)
                po_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(po.date_order))
                customer = po.partner_id.name
                challan = picking.challan_bill_no
                challan_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(picking.date_done))
                for move in new_picking.pack_operation_ids:
                    po_line_objs = po.order_line.filtered(lambda r: r.product_id.id == move.product_id.id)
                    if po_line_objs:
                        pack_obj = {}
                        # calculate discount amount
                        dis_amt = (po_line_objs[0].price_unit * po_line_objs[0].discount) / 100
                        pack_obj['product_id'] = move.product_id.name
                        pack_obj['pr_no'] = po.origin
                        pack_obj['mrr_quantity'] = move.qty_done
                        pack_obj['product_uom_id'] = move.product_uom_id.name
                        pack_obj['price_unit'] = formatLang(self.env, po_line_objs[0].price_unit)
                        pack_obj['sub_amount'] = formatLang(self.env, move.qty_done * (po_line_objs[0].price_unit - dis_amt))
                        pack_obj['discount'] = po_line_objs[0].discount
                        pack_obj['amount'] = move.qty_done * (po_line_objs[0].price_unit - dis_amt)
                        total_amount.append(pack_obj['amount'])
                        pack_list.append(pack_obj)
        else:
            customer = picking.partner_id.name
            challan = picking.challan_bill_no
            challan_date = report_utility_pool.getERPDateFormat(
                report_utility_pool.getDateTimeFromStr(picking.date_done))
            for move in new_picking.pack_operation_ids:
                pack_obj = {}
                pack_obj['product_id'] = move.product_id.name
                pack_obj['pr_no'] = new_picking.origin
                pack_obj['mrr_quantity'] = move.qty_done
                pack_obj['product_uom_id'] = move.product_uom_id.name
                pack_obj['price_unit'] = formatLang(self.env, move.product_id.standard_price)
                pack_obj['sub_amount'] = formatLang(self.env, move.qty_done * move.product_id.standard_price)
                pack_obj['discount'] = False
                pack_obj['amount'] = move.qty_done * move.product_id.standard_price
                total_amount.append(pack_obj['amount'])
                pack_list.append(pack_obj)

        return {
            'pack_list':pack_list,
            'po_no':po_no,
            'po_date':po_date,
            'customer':customer,
            'challan':challan,
            'challan_date':challan_date,
            'total_amount': total_amount
        }
