from odoo import api, fields, models,_

class EmployeePayroll(models.Model):

    _inherit = "hr.employee"
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.job_id:
                name = "%s [%s]" % (name,record.job_id.name_get()[0][1])
            result.append((record.id, name))
        return result