# -*- coding: utf-8 -*-
from odoo import fields, models, _,api
from datetime import datetime
from odoo import SUPERUSER_ID


class ReminderVisa(models.Model):
    _inherit = 'hr.employee'

    anniversary = fields.Date('Date of Anniversary')

    @api.model
    def birthday_mail_reminder(self):
        today = datetime.now()
        employees = self.env['hr.employee'].search([])
        for i in employees:
            if i.birthday:
                daymonth = datetime.strptime(i.birthday, "%Y-%m-%d")
                if today.day == daymonth.day and today.month == daymonth.month:
                    self.send_birthday_wish(i.id)
        return

    @api.model
    def send_birthday_wish(self, emp_id):
        tmpl_id = 'birth_day_notification.birthday_notification'
        return self.send_wish_email(emp_id, tmpl_id)

    @api.model
    def anniversary_mail_reminder(self):
        today = datetime.now()
        employees = self.env['hr.employee'].search([])
        for i in employees:
            if i.anniversary:
                daymonth = datetime.strptime(i.anniversary, "%Y-%m-%d")
                if today.day == daymonth.day and today.month == daymonth.month:
                    self.send_anniversary_wish(i.id)
        return

    @api.model
    def send_anniversary_wish(self, emp_id):
        tmpl_id = 'birth_day_notification.anniversary_wish_notify'

        return self.send_wish_email(emp_id,tmpl_id)

    def send_wish_email(self,emp_id,tmpl_id):
        su_id = self.env['res.partner'].browse(SUPERUSER_ID)
        template = self.env.ref(tmpl_id, raise_if_not_found=False)
        employee = self.env['hr.employee'].browse(emp_id)
        context = {
            'res_id': False,
            'lang': self.env.user.lang,
        }

        template.with_context(context).send_mail(emp_id, force_send=True, raise_exception=True)

