from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError


class MyLeaveConfirmWizard(models.TransientModel):
    _name = 'my.leave.confirm.wizard'

    encashment_leave = fields.Integer(string="Encashment", required=True)
    carried_leave = fields.Integer(string="Carried Over", required=True)

    @api.multi
    def action_confirm_save(self):

        form_id = self.env.context.get('active_id')
        obj_pool = self.env['hr.leave.forward.encash.line']
        line_obj = obj_pool.search([('id', '=', form_id)])

        if line_obj.balance_leave < self.encashment_leave + self.carried_leave:
            raise UserError(_("Invalid Entry."))

        line_obj.write({'encashment_leave':self.encashment_leave,
                        'carried_leave': self.carried_leave,
                        'state': 'confirmed'})

        return {'type': 'ir.actions.act_window_close'}










