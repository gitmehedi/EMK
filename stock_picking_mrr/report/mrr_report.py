from odoo import api, exceptions, fields, models

class MrrReport(models.AbstractModel):
    _name = 'report.stock_picking_mrr.report_mrr_doc'

    @api.multi
    def render_html(self, docids, data=None):
        report_utility_pool = self.env['report.utility']
        picking = self.env['stock.picking'].search(['|',('name', '=', data['origin']),('origin','=',data['origin'])],limit=1 ,order='id asc')
        new_picking = self.env['stock.picking'].search([('id', '=', data['self_picking_id'])])
        mrr_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(data['mrr_date']))
        pack_list = []
        total_amount = []
        customer =False
        challan =False
        challan_date = False
        po_no = False
        po_date = False
        pr_no = False

        if picking.shipment_id:
            if picking.shipment_id.lc_id.po_ids:
                for po in picking.shipment_id.lc_id.po_ids:
                    po_no = po.name
                    po_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(po.date_order))
                    customer = po.partner_id.name
                    pr_no = po.requisition_id.name
            if picking.shipment_id.gate_in_ids:
                for gate in picking.shipment_id.gate_in_ids:
                    challan = gate.challan_bill_no
                    challan_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(gate.date))

        elif picking.purchase_id:
            po_no = picking.purchase_id.name
            po_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(picking.purchase_id.date_order))
            customer = picking.purchase_id.partner_id.name
            pr_no = picking.purchase_id.sudo().requisition_id.name
            challan = picking.challan_bill_no
            challan_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateTimeFromStr(picking.date_done))

        product_list = []
        for product in picking.purchase_id.order_line:
            product_obj={}
            product_obj['product_id'] = product.product_id.id
            product_obj['product_name'] = product.product_id.name
            product_obj['price_unit'] = product.price_unit
            product_list.append(product_obj)


        if new_picking.move_lines:
            for move in new_picking.move_lines:
                pack_obj = {}
                pack_obj['product_id'] = move.product_id.name
                pack_obj['mrr_quantity'] = move.product_uom_qty
                pack_obj['product_uom_id'] = move.product_uom.name
                for pro_list in product_list:
                    if move.product_id.id == pro_list['product_id']:
                        price_unit =  pro_list['price_unit']
                        pack_obj['price_unit'] = price_unit
                        pack_obj['amount'] = move.product_uom_qty*price_unit
                        total_amount.append(pack_obj['amount'])
                        pack_list.append(pack_obj)
                    
        total = sum(total_amount)
        amt_to_word = self.env['res.currency'].amount_to_word(float(total))
        docargs = {
            'lists' : pack_list,
            'mrr_no' : data['mrr_no'],
            'mrr_date' : mrr_date,
            'customer' : customer,
            'challan' : challan,
            'challan_date' : challan_date,
            'po_no' : po_no,
            'pr_no' : pr_no,
            'po_date': po_date,
            'total_amount' : total,
            'amt_to_word' : amt_to_word
        }
        return self.env['report'].render('stock_picking_mrr.report_mrr_doc', docargs)
