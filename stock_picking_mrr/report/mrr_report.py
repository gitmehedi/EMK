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

                    
        total = sum(total_amount)
        amt_to_word = self.env['res.currency'].amount_to_word(float(total))
        docargs = {
            'lists' : pack_list,
            'mrr_no' : data['mrr_no'],
            'mrr_date' : mrr_date,
            'customer' : customer,
            'challan' : challan,
            'challan_date' : challan_date,
            'po_no' : ','.join(po_no),
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
        for po in po_ids:
            po_no.append(po.name)
            po_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(po.date_order))
            customer = po.partner_id.name
            challan = picking.challan_bill_no
            challan_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(picking.date_done))
            for move in new_picking.move_lines:
                po_line_objs = po.order_line.filtered(lambda r: r.product_id.id == move.product_id.id)
                if po_line_objs:
                    pack_obj = {}
                    pack_obj['product_id'] = move.product_id.name
                    pack_obj['pr_no'] = po.origin
                    pack_obj['mrr_quantity'] = move.product_uom_qty
                    pack_obj['product_uom_id'] = move.product_uom.name
                    pack_obj['price_unit'] = formatLang(self.env, po_line_objs[0].price_unit)
                    pack_obj['sub_amount'] = formatLang(self.env, move.product_uom_qty * po_line_objs[0].price_unit)
                    pack_obj['amount'] = move.product_uom_qty * po_line_objs[0].price_unit
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