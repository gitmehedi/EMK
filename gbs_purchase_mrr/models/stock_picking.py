from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_approve(self):
        res = super(Picking, self).button_approve()
        self.ensure_one()
        # used stock move ids
        move_id_list = []
        po_obj = self.env['purchase.order'].search([('name', '=', self.origin)])
        if po_obj:
            move_id_list = self.update_pr_line_mrr(po_obj, move_id_list)
        else:
            po_obj_list = self.env['letter.credit'].search([('name', '=', self.origin), ('state', '!=', 'cancel')]).po_ids
            for po_obj in po_obj_list:
                move_id_list = self.update_pr_line_mrr(po_obj, move_id_list)
        return res

    @api.multi
    def update_pr_line_mrr(self, po_obj, move_id_list):
        po_line_ids_str = "(" + str(po_obj.order_line.id) + ")" if len(po_obj.order_line.ids) == 1 else str(tuple(po_obj.order_line.ids))
        sql_str = """SELECT pr_line_id FROM po_pr_line_rel WHERE po_line_id IN %s ORDER BY pr_line_id asc""" % (po_line_ids_str)
        self.env.cr.execute(sql_str)
        pr_line_ids_list = self._cr.fetchall()
        pr_line_obj_list = self.env['purchase.requisition.line'].search([('id', 'in', pr_line_ids_list)])

        for line in pr_line_obj_list:
            move_ids = self.move_lines.filtered(lambda m: m.product_id.id == line.product_id.id)
            move_ids = move_ids.sorted(key=lambda m: m.product_qty, reverse=True)

            for move in move_ids:
                if move.id not in move_id_list:
                    mrr_qty = line.mrr_qty + move.product_qty
                    if line.product_ordered_qty >= mrr_qty:
                        line.write({'mrr_qty': mrr_qty})
                        move_id_list.append(move.id)
                        break

        return move_id_list
