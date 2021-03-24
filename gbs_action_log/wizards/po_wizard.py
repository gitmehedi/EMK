from odoo import api, fields, models, _


class PurchaseOrderTypeWizard(models.TransientModel):
    _inherit = 'purchase.order.type.wizard'

    @api.multi
    def save_type(self):
        res = super(PurchaseOrderTypeWizard, self).save_type()

        active_id = self.env.context.get('active_id')
        order_pool = self.env['purchase.order'].search([('id', '=', active_id)])

        action_code = order_pool.get_action_code('confirm_order')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            order_pool.create_action_log(user_action_pool)

        return res
