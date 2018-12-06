from odoo import models, fields, api

class Picking(models.Model):
    _inherit = "stock.picking"


    def button_approve(self):
        res = super(Picking, self).button_approve()
        self.ensure_one()
        po_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po_obj:
            self.update_pr_line_mrr(po_obj)
        else:
            lc_po_objs = self.search([('name', '=', self.origin)]).shipment_id.lc_id.po_ids
            for lc_po_obj in lc_po_objs:
                self.update_pr_line_mrr(lc_po_obj)
        return res

    def update_pr_line_mrr(self,po_obj):
        if len(po_obj.order_line.ids) == 1:
            po_line_ids = "(" + str(po_obj.order_line.id) + ")"
        else:
            po_line_ids = str(tuple(po_obj.order_line.ids))
        query = """SELECT pr_line_id FROM po_pr_line_rel WHERE po_line_id IN %s ORDER BY pr_line_id asc""" % (
        po_line_ids)
        self.env.cr.execute(query)
        datas = self._cr.fetchall()
        for move in self.move_lines:
            pr_line_objs = self.env['purchase.requisition.line'].search(
                [('id', 'in', datas), ('product_id', '=', move.product_id.id)])
            if pr_line_objs:
                mrr_qty = move.product_qty
                for pr_line_obj in pr_line_objs:
                    if mrr_qty > pr_line_obj.product_ordered_qty:
                        pr_line_obj.write({'mrr_qty': pr_line_obj.mrr_qty + pr_line_obj.product_ordered_qty})
                    else:
                        pr_line_obj.write({'mrr_qty': pr_line_obj.mrr_qty + mrr_qty})
                    mrr_qty = mrr_qty - pr_line_obj.product_ordered_qty
                    # pr_line_obj[0].write({'mrr_qty': pr_line_obj.mrr_qty + move.product_qty})