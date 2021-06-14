from odoo import models, fields, api, _

ACTION_CODE_DICT = {
    'confirm_order': 5
}


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def create_action_log(self, user_action):
        vals = {
            'action_id': user_action.id,
            'performer_id': self.env.user.id,
            'perform_date': fields.Datetime.now(),
            'order_id': self.id
        }
        self.env['purchase.order.action.log'].create(vals)

    @api.multi
    def get_action_code(self, action_name):
        return ACTION_CODE_DICT.get(action_name, False)
