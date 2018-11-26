from odoo import api, fields, models,_
from odoo.exceptions import ValidationError,UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    rfq_id = fields.Many2one('purchase.rfq', string='RFQ Reference',store=True,states={'done': [('readonly', True)],'purchase': [('readonly', True)],'cancel': [('readonly', True)]})

    @api.onchange('rfq_id')
    def _onchange_rfq_id(self):
        if not self.rfq_id:
            return

        rfq = self.rfq_id
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'),
             ('warehouse_id.operating_unit_id', '=', rfq.operating_unit_id.id)], order='id ASC', limit=1)
        if not picking_type:
            raise UserError(_('Please create picking type or contact with your system administrator.'))

        due_products = self.rfq_id.purchase_rfq_lines.filtered(lambda x: x.product_qty - x.po_receive_qty > 0)
        if not due_products:
            raise UserError('No due so no quotation required!!!')
        else:
            self.origin = rfq.name
            self.partner_ref = rfq.name  # to control vendor bill based on agreement reference
            self.date_order = rfq.rfq_date or fields.Datetime.now()
            self.picking_type_id = picking_type.id
            self.operating_unit_id = rfq.operating_unit_id

            # Create PO lines if necessary
            order_lines = []
            for line in due_products:
                # Create PO line
                order_lines.append((0, 0, {
                    'name': line.product_id.display_name,
                    'product_id': line.product_id.id,
                    'product_uom': line.product_id.uom_po_id.id,
                    'product_qty': line.product_qty - line.po_receive_qty,
                    'price_unit': line.price_unit,
                    'taxes_id': '',
                    'date_planned': rfq.rfq_date or fields.Date.today(),
                    # 'procurement_ids': [
                    #     (6, 0, [requisition.procurement_id.id])] if requisition.procurement_id else False,
                    # 'account_analytic_id': line.account_analytic_id.id,
                }))
            self.order_line = order_lines
            # if requisition.region_type:
            #     self.region_type = requisition.region_type
            # if requisition.purchase_by:
            #     self.purchase_by = requisition.purchase_by
            # if requisition.state == 'done':
            #     self.check_po_action_button = True

    @api.multi
    def action_update(self):
        res = super(PurchaseOrder, self).action_update()
        self.ensure_one()
        if self.rfq_id:
            for line in self.order_line:
                rfq_line_id = self.rfq_id.purchase_rfq_lines.filtered(lambda x: x.product_id.id == line.product_id.id)
                if rfq_line_id:
                    rfq_line_id[0].write({'po_receive_qty': rfq_line_id[0].po_receive_qty + line.product_qty})
                    # if len(pr_line_id) > 1....open wizard and choose from which pr how many product will given for PO
                    # else
                    query = """SELECT pr_line_id FROM pr_rfq_line_rel WHERE rfq_line_id = %s ORDER BY pr_line_id asc"""
                    self._cr.execute(query, [tuple([rfq_line_id[0].id])])
                    datas = self._cr.fetchall()
                    total_po_qty = line.product_qty
                    for data in datas:
                        pr_line_obj = self.env['purchase.requisition.line'].search([('id', '=', data)])
                        if total_po_qty > pr_line_obj.product_ordered_qty:
                            pr_line_obj.write({'receive_qty': pr_line_obj.receive_qty + pr_line_obj.product_ordered_qty})
                        else:
                            pr_line_obj.write({'receive_qty': pr_line_obj.receive_qty + total_po_qty})
                        total_po_qty = total_po_qty - pr_line_obj.product_ordered_qty
                        self._cr.execute('INSERT INTO po_pr_line_rel (pr_line_id,po_line_id) VALUES (%s, %s)',
                                     tuple([data, line.id]))
        return res
