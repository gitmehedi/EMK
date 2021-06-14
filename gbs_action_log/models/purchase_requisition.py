from odoo import models, fields, api, _

# key = Action Name
# value = Action Code
ACTION_CODE_DICT = {
    'confirm': 1,
    'validate': 2,
    'approve': 3,
    'done': 4
}


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.multi
    def action_in_progress(self):
        res = super(PurchaseRequisition, self).action_in_progress()

        action_code = self.get_action_code('confirm')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            self.create_action_log(user_action_pool)

    @api.one
    def action_done(self):
        res = super(PurchaseRequisition, self).action_done()

        action_code = self.get_action_code('done')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            self.create_action_log(user_action_pool)

    def create_action_log(self, user_action):
        vals = {
            'action_id': user_action.id,
            'performer_id': self.env.user.id,
            'perform_date': fields.Datetime.now(),
            'requisition_id': self.id
        }
        self.env['purchase.requisition.action.log'].create(vals)

    @api.multi
    def get_action_code(self, action_name):
        return ACTION_CODE_DICT.get(action_name, False)
