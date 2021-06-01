from odoo import models, fields, api, _


class PRFromWhereWizard(models.TransientModel):
    _inherit = 'pr.from.where.wizard'

    @api.multi
    def save_type(self):
        res = super(PRFromWhereWizard, self).save_type()

        active_id = self.env.context.get('active_id')
        purchase_requisition_pool = self.env['purchase.requisition'].search([('id', '=', active_id)])

        action_code = purchase_requisition_pool.get_action_code('validate')
        user_action_pool = self.env['users.action'].search([('code', '=', action_code)])
        if user_action_pool:
            purchase_requisition_pool.create_action_log(user_action_pool)

        return res
