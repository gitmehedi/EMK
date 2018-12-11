from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # write function of reset to quotation
    def action_reset_quotation(self):
        # condition is there any related picking?
        if self.picking_ids:
            # condition 1 is related picking is in done state?
            if 'done' in [i.state for i in self.picking_ids]:
                raise UserError(_('Sorry!Unable to reverse this PO because already anticipatory stock updated.'))
            else:
                self.picking_ids.sudo().pack_operation_product_ids.unlink()
                picking_objs = self.env['stock.picking'].search([('origin', '=', self.name)])
                picking_objs.sudo().unlink()
                self.reserve_pr_line()
        elif self.env['letter.credit'].search([('po_ids', '=', self.id)]):
            # condition 2 is it has any LC?
            raise UserError(_('Sorry!Unable to reverse this PO because already its added to the LC.'))
        else:
            # without any LC and picking reserve process
            self.reserve_pr_line()


    def reserve_pr_line(self):
        if len(self.order_line.ids) == 1:
            po_line_ids = "(" + str(self.order_line.id) + ")"
        else:
            po_line_ids = str(tuple(self.order_line.ids))
        query_pr_line_ids = """SELECT pr_line_id FROM po_pr_line_rel WHERE po_line_id IN %s ORDER BY pr_line_id asc""" % (
            po_line_ids)
        self.env.cr.execute(query_pr_line_ids)
        data_pr_line_ids = self._cr.fetchall()
        pr_line_objs = self.env['purchase.requisition.line'].search([('id', 'in', data_pr_line_ids)],order='id ASC')
        if self.rfq_id:
            if len(pr_line_objs.ids) == 1:
                pr_line_ids = "(" + str(pr_line_objs.id) + ")"
            else:
                pr_line_ids = str(tuple(pr_line_objs.ids))

            query_rfq_line_ids = """SELECT rfq_line_id FROM pr_rfq_line_rel WHERE pr_line_id IN %s ORDER BY rfq_line_id asc""" % (
                pr_line_ids)
            self.env.cr.execute(query_rfq_line_ids)
            data_rfq_line_ids = self._cr.fetchall()
            rfq_line_objs = self.env['purchase.rfq.line'].search([('id', 'in', data_rfq_line_ids)],order='id ASC')
            self.reserve_pr_line_due_qty(self.order_line, pr_line_objs,rfq_line_objs)
        else:
            self.reserve_pr_line_due_qty(self.order_line,pr_line_objs)

        # delete pr_po_line_rel
        query_pr_line_ids = """DELETE FROM po_pr_line_rel WHERE po_line_id IN %s""" % (
            po_line_ids)
        self.env.cr.execute(query_pr_line_ids)
        # changes on main form
        self.write({'state':'draft'})
        self.check_po_action_button = True


    def reserve_pr_line_due_qty(self,order_line_obs,pr_line_objs,rfq_line_objs = None):
        for order_line_id in order_line_obs:
            # if rfq then update rfq line
            if rfq_line_objs:
                rfq_line_obj = rfq_line_objs.filtered(lambda r: r.product_id.id == order_line_id.product_id.id)
                if rfq_line_obj:
                    rfq_line_obj[0].write({'po_receive_qty': rfq_line_obj.po_receive_qty - order_line_id.product_qty})
            # update pr line
            pr_line_filter_objs = pr_line_objs.filtered(lambda r: r.product_id.id == order_line_id.product_id.id)
            if pr_line_filter_objs:
                po_line_qty = order_line_id.product_qty
                for pr_line_filter_obj in pr_line_filter_objs:
                    if po_line_qty > pr_line_filter_obj.product_ordered_qty:
                        pr_line_filter_obj.write(
                            {'receive_qty': pr_line_filter_obj.receive_qty - pr_line_filter_obj.product_ordered_qty})
                    else:
                        pr_line_filter_obj.write({'receive_qty': pr_line_filter_obj.receive_qty - po_line_qty})
                    po_line_qty = po_line_qty - pr_line_filter_obj.product_ordered_qty
