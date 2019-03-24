from odoo import api, fields, models


class EmailTemplateWizard(models.TransientModel):
    _name = 'email.template.wizard'

    def _load_all_employee(self):
        return self.env['hr.employee'].sudo().search([])

    subject = fields.Char('Subject', required= True)
    # employee_ids = fields.Many2many('hr.employee', string="Send To", required=True, default=_load_all_employee)
    user_ids = fields.Many2many('res.users', string="Send To", required=True)
    massage = fields.Text('Notes', required=True)


    @api.multi
    def sendMail(self):

        if len(self.user_ids) == 0:
            return

        email_server_list = []
        email_list = []
        for user in self.user_ids:
            if user.login:
                email_list.append((user.login).strip())

        template_obj = self.env['mail.mail']
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC', limit=1)

        if email_server_obj:
            for email in email_server_obj:
                if email.smtp_user:
                    server = email.smtp_user
                    email_server_list.append(server)

        template_data = {
            'subject': self.subject,
            'body_html': self.massage,
            'email_from': email_server_list[0] if email_server_list else None,
            'email_to': ", ".join(email_list)
        }
        template_id = template_obj.create(template_data)
        template_obj.send(template_id)