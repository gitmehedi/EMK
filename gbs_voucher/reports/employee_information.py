from odoo import api, fields, models, _


class EmployeeInformation(models.TransientModel):
    _name = "employee.information.from.user"

    def get_employee_information(self, user_id):
        query = '''
                SELECT rr.name, hd.name department, hj.name designation FROM resource_resource rr 
                LEFT JOIN 
                hr_employee he ON he.resource_id = rr.id 
                LEFT JOIN hr_department hd ON he.department_id = hd.id
                LEFT JOIN hr_job hj ON he.job_id = hj.id
                WHERE rr.user_id = %s
                LIMIT 1
        ''' % user_id

        self.env.cr.execute(query)
        information = []
        for vals in self.env.cr.dictfetchall():
            information.append(vals['name'])
            information.append(vals['department'])
            information.append(vals['designation'])

        user_obj = self.env['res.users'].suspend_security().browse(user_id)
        name = user_obj.login
        department = ''
        designation = ''
        if information == []:
            information.append(name)
            information.append(department)
            information.append(designation)

        return information

    def get_checked_by(self, mail_tracking_value_obj):
        for mail_track in mail_tracking_value_obj:
            if mail_track.new_value_char == 'Posted':
                employee_information = self.env['employee.information.from.user'].get_employee_information(
                    mail_track.mail_message_id.create_uid.id)
                return employee_information


    def get_prepared_by(self, mail_message_ids):
        mail_message_obj = self.env['mail.message'].browse(mail_message_ids[0])
        employee_information = self.env['employee.information.from.user'].get_employee_information(
            mail_message_obj.create_uid.id)
        return employee_information




