from odoo import api, exceptions, fields, models
from odoo.addons.custom_report.data.utility import ReportUtility




class MrrReport(models.AbstractModel):
    _name = 'report.stock_picking_mrr.report_mrr_doc'

    @api.multi
    def render_html(self, docids, data=None):
        report_utility_pool = self.env['report.utility']
        origin_picking_objs = self.env['stock.picking'].search([('name', '=', data['origin'])])
        mrr_date = report_utility_pool.getERPDateFormat(report_utility_pool.getDateFromStr(data['mrr_date']))
        pack_list = []
        total_amount = []
        for picking in origin_picking_objs:
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

            if picking.pack_operation_product_ids:
                for pack in picking.pack_operation_product_ids:
                    pack_obj = {}
                    pack_obj['product_id'] = pack.product_id.name
                    pack_obj['pr_no'] = pr_no
                    pack_obj['mrr_quantity'] = pack.qty_done
                    pack_obj['product_uom_id'] = pack.product_uom_id.name
                    pack_obj['price_unit'] = pack.linked_move_operation_ids.move_id.price_unit
                    pack_obj['amount'] = pack.qty_done*pack.linked_move_operation_ids.move_id.price_unit
                    total_amount.append(pack_obj['amount'])
                    pack_list.append(pack_obj)

        #amt_to_word_amount = self.env['res.currency'].amount_to_word(total_amount)
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
            'po_date': po_date,
            'total_amount' : total,
            'amt_to_word' : amt_to_word

        }
        return self.env['report'].render('stock_picking_mrr.report_mrr_doc', docargs)
