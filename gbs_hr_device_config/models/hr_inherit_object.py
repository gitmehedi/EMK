from openerp import models, fields
from openerp import api


class HrAttendance(models.Model):
    _inherit = ['hr.attendance']


    is_system_generated = fields.Boolean(string='Is System Generated', default=False)
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=False)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        return

class HrEmployee(models.Model):
    _inherit = ['hr.employee']

    device_employee_acc = fields.Integer(string='AC No.')





# class HrAttendanceImportError(models.Model):
#     _inherit = ['hr.attendance.import.error']
#
#     import_id = fields.Many2one('hr.attendance.import', 'id', ondelete='cascade', required=True)

