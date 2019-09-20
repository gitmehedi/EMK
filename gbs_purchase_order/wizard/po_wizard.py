from odoo import api, fields, models, _
from datetime import datetime


class PurchaseRequisitionTypeWizard(models.TransientModel):
    _name = 'purchase.order.type.wizard'

    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')],
                                   string="Region Type",required=True,
                                   default=lambda self: self.env.context.get('region_type'))

    purchase_by = fields.Selection([('cash', 'Cash'), ('credit', 'Credit'), ('lc', 'LC'), ('tt', 'TT')],
                                   string="Purchase By",required=True,
                                   default=lambda self: self.env.context.get('purchase_by'))

    @api.multi
    def save_type(self):
        form_id = self.env.context.get('active_id')
        order = self.env['purchase.order'].search([('id', '=', form_id)])
        order._add_supplier_to_product()
        # Deal with double validation process
        requested_date = datetime.strptime(order.date_order, "%Y-%m-%d %H:%M:%S").date()
        new_seq = self.env['ir.sequence'].next_by_code_new('purchase.order', requested_date,order.operating_unit_id)
        if new_seq:
            order.write({'name': new_seq})
        # insert and update receive quantity (function)
        order.action_update()
        if self.purchase_by not in ['lc']:
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.write({'region_type': self.region_type, 'purchase_by': self.purchase_by})
                order.button_approve()
            else:
                order.write({'region_type': self.region_type, 'purchase_by': self.purchase_by, 'state': 'to approve'})
        else:
            if order.company_id.po_double_validation == 'one_step':
                order.write({'region_type': self.region_type, 'purchase_by': self.purchase_by, 'state': 'done'})
            else:
                order.write({'region_type': self.region_type, 'purchase_by': self.purchase_by, 'state': 'purchase'})
        for po in order:
            # if po.requisition_id.type_id.exclusive == 'exclusive':
            others_po = po.requisition_id.mapped('purchase_ids').filtered(lambda r: r.id != po.id)
            for other_po in others_po:
                other_po.disable_new_revision_button = True
            # others_po.button_cancel()
            po.write({'invoice_status':'to invoice'})
            for element in po.order_line:
                if element.product_id == po.requisition_id.procurement_id.product_id:
                    element.move_ids.write({
                        'procurement_id': po.requisition_id.procurement_id.id,
                        'move_dest_id': po.requisition_id.procurement_id.move_dest_id.id,
                    })
            po.check_po_action_button = False
        return {'type': 'ir.actions.act_window_close'}










