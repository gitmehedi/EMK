from odoo import api, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError


class Holidays(models.Model):
    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'mail.thread']

    @api.one
    @api.constrains('number_of_days_temp')
    def _check_values(self):
        if self.number_of_days_temp == 0.0:
            raise ValidationError(_('Duration time should not be zero!!'))

    @api.model
    def create(self, vals):
        res = super(Holidays, self).create(vals)
        res._notify_approvers()
        return res

    @api.multi
    def write(self, values):
        employee_id = values.get('employee_id', False)
        if employee_id:
            self.pending_approver = self.env['hr.employee'].search([('id', '=', employee_id)]).holidays_approvers[
                0].approver.id
        res = super(Holidays, self).write(values)
        return res

    @api.multi
    def btn_action_approve(self):
        res = super(Holidays, self).btn_action_approve()
        self._notify_approvers()

        return res

    @api.multi
    def _notify_approvers(self):
        for holiday in self:
            if holiday.holiday_type != 'category' and not holiday.parent_id:
                if holiday.sudo(SUPERUSER_ID).pending_approver and \
                        holiday.sudo(SUPERUSER_ID).pending_approver.user_id:
                    self.message_post(body="",
                                      partner_ids=[holiday.sudo(SUPERUSER_ID).pending_approver.user_id.partner_id.id])

    @api.multi
    def _send_refuse_notification(self):
        for holiday in self:
            if holiday.holiday_type != 'category' and not holiday.parent_id:
                if holiday.sudo(SUPERUSER_ID).employee_id and \
                        holiday.sudo(SUPERUSER_ID).employee_id.user_id:
                    self.message_post(body="Your leave request has been refused.",
                                      partner_ids=[holiday.sudo(SUPERUSER_ID).employee_id.user_id.partner_id.id])

    @api.multi
    def action_refuse(self):
        # if not (self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        #         or self.env.user.has_group('gbs_application_group.group_dept_manager')):
        #     raise UserError(_('Only an HR Officer or Manager or Department Head can refuse leave requests.'))

        manager = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate', 'validate1']:
                raise UserError(_('Leave request must be confirmed or validated in order to refuse it.'))

            vals = {'state': 'refuse', 'pending_approver': None}
            if holiday.state == 'validate1':
                vals['manager_id'] = manager.id
            else:
                vals['manager_id2'] = manager.id

            holiday.write(vals)

            # Delete the meeting
            if holiday.meeting_id:
                holiday.meeting_id.unlink()
            # If a category that created several holidays, cancel all related
            holiday.linked_request_ids.action_refuse()
        self._remove_resource_leave()
        self._send_refuse_notification()

    def _check_state_access_right(self, vals):
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel', 'refuse'] and not self.env[
            'res.users'].has_group('hr_holidays.group_hr_holidays_user'):
            return False
        return True
