from odoo import api, fields, models


class EmailTemplateWizard(models.TransientModel):
    _name = 'email.template.wizard'


    subject = fields.Char('Subject', required= True)
    employee_ids = fields.Many2many('hr.employee', string="Send To", required=True)
    massage = fields.Text('Notes', required=True)


    @api.multi
    def sendMail(self):

        if len(self.employee_ids) == 0:
            return

        email_server_list = []
        email_list = []
        for emp in self.employee_ids:
            if emp.work_email:
                email_list.append((emp.work_email).strip())

        template_obj = self.env['mail.mail']
        email_server_obj = self.env['ir.mail_server'].search([], order='id ASC')

        for email in email_server_obj:
            if email.smtp_user:
                server = email.smtp_user
                email_server_list.append(server)

        template_data = {
            'subject': self.subject,
            'body_html': self.massage,
            'email_from': email_server_list[0],
            'email_to': ", ".join(email_list)
        }
        template_id = template_obj.create(template_data)
        template_obj.send(template_id)