from odoo import api, fields, models, _


class PurchaseRequisitionTypeWizard(models.TransientModel):
    _name = 'purchase.order.type.wizard'

    region_type = fields.Selection([('local', 'Local'), ('foreign', 'Foreign')],
                                   string="LC Region Type",required=True,
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
        if order.company_id.po_double_validation == 'one_step'\
                or (order.company_id.po_double_validation == 'two_step'\
                    and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                or order.user_has_groups('purchase.group_purchase_manager'):
            order.button_approve()
        else:
            order.write({'region_type': self.region_type,'purchase_by': self.purchase_by,'state': 'to approve'})
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def cancel_window(self):
        form_id = self.env.context.get('active_id')
        order = self.env['purchase.order'].search([('id', '=', form_id)])
        order._add_supplier_to_product()
        # Deal with double validation process
        if order.company_id.po_double_validation == 'one_step' \
                or (order.company_id.po_double_validation == 'two_step' \
                            and order.amount_total < self.env.user.company_id.currency_id.compute(
                        order.company_id.po_double_validation_amount, order.currency_id)) \
                or order.user_has_groups('purchase.group_purchase_manager'):
            order.button_approve()
        else:
            order.write({'state': 'to approve'})
        return {'type': 'ir.actions.act_window_close'}










