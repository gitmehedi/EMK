from odoo import api, models, SUPERUSER_ID


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def create(self, vals):
        res = super(HrHolidays, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def _notify_approvers(self):
        """Input: res.user"""
        # self.ensure_one()
        for holiday in self:
            approvers = holiday.employee_id._get_employee_manager()
            if not approvers:
                return True
            for approver in approvers:
                holiday.sudo(SUPERUSER_ID).add_follower(approver.id)
                if approver.sudo(SUPERUSER_ID).user_id:
                    holiday.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
                        [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        return True
