from odoo import models, fields, api, _

# key = Action Name
# value = Action Code
ACTION_CODE_DICT = {
    'pi_confirm': 9,
    'so_approval': 10,
    'accounts_approval': 11,
    'cxo_approval': 12,
    'submit_to_approval': 13,
    'da_confirm': 14,
    'da_approved': 15,
    'ds_confirm': 16,
    'dc_validate': 17
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_to_submit(self):
        res = super(SaleOrder, self).action_to_submit()
        action = ActionLogCommon()
        action_code = action.get_action_code('submit_to_approval')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res

    @api.multi
    def action_submit(self):
        res = super(SaleOrder, self).action_submit()
        action = ActionLogCommon()
        action_code = action.get_action_code('so_approval')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res

    @api.multi
    def action_validate(self):
        res = super(SaleOrder, self).action_validate()
        action = ActionLogCommon()
        action_code = action.get_action_code('accounts_approval')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        action = ActionLogCommon()
        action_code = action.get_action_code('cxo_approval')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res



class ProformaInvoice(models.Model):
    _inherit = 'proforma.invoice'

    @api.multi
    def action_confirm(self):
        res = super(ProformaInvoice, self).action_confirm()
        action = ActionLogCommon()
        action_code = action.get_action_code('pi_confirm')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res



class DeliveryAuthorization(models.Model):
    _inherit = 'delivery.authorization'

    def action_validate(self):
        res = super(DeliveryAuthorization, self).action_validate()
        action = ActionLogCommon()
        action_code = action.get_action_code('da_confirm')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res

    def action_close(self):
        res = super(DeliveryAuthorization, self).action_close()
        action = ActionLogCommon()
        action_code = action.get_action_code('da_approved')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            action.create_action_log(self, user_action_pool)
        return res

class DeliverySchedules(models.Model):
    _inherit = 'delivery.schedules'

    @api.multi
    def action_confirm(self):
        res = super(DeliverySchedules, self).action_confirm()
        action = ActionLogCommon()
        action_code = action.get_action_code('ds_confirm')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            for line in self.line_ids:
                self = line.sale_order_id
                action.create_action_log(self, user_action_pool)
        return res

class StockDateOfTransfer(models.TransientModel):
    _inherit = 'stock.date.transfer'

    @api.multi
    def save(self):
        res = super(StockDateOfTransfer, self).save()
        action = ActionLogCommon()
        action_code = action.get_action_code('ds_confirm')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            self = self.pick_id.sale_id
            action.create_action_log(self, user_action_pool)
        return res



class ActionLogCommon:
    def create_action_log(self, action, user_action):
        self = action
        vals = {
            'action_id': user_action.id,
            'performer_id': self.env.user.id,
            'perform_date': fields.Datetime.now(),
            'order_id': self.id
        }
        self.env['sale.order.action.log'].create(vals)

    @api.multi
    def get_action_code(self, action_name):
        return ACTION_CODE_DICT.get(action_name, False)