from odoo import api, fields, models, SUPERUSER_ID

class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_1st_level_approval(self):
        ### IF SUPERUSER
        if SUPERUSER_ID == self.env.user.id:
            return True

        ### If Department Manager
        if self.department_id.manager_id.user_id.id == self.env.user.id:
            return True

        ### If Line Manager
        if self.parent_id.user_id.id == self.env.user.id:
            return True

        return False