from odoo import models, fields, api, _

ACTION_CODE_DICT = {
    'validate': 6,
    'approve': 7,
    'ac_approve': 8
}


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        res = super(StockPicking, self).do_transfer()

        # user action log
        if res:
            action_code = self.get_action_code('validate')
            user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
            if user_action_pool:
                self.create_action_log(user_action_pool)

        return res

    @api.multi
    def button_ac_approve(self):
        res = super(StockPicking, self).button_ac_approve()

        # user action log
        action_code = self.get_action_code('ac_approve')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            self.create_action_log(user_action_pool)

    @api.multi
    def button_approve(self):
        res = super(StockPicking, self).button_approve()

        # user action log
        action_code = self.get_action_code('approve')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            self.create_action_log(user_action_pool)

    def create_action_log(self, user_action):
        vals = {
            'action_id': user_action.id,
            'performer_id': self.env.user.id,
            'perform_date': fields.Datetime.now(),
            'picking_id': self.id
        }
        self.env['stock.picking.action.log'].create(vals)

    @api.multi
    def get_action_code(self, action_name):
        return ACTION_CODE_DICT.get(action_name, False)
