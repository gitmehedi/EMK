from openerp import fields,api
from openerp import models
import datetime


class HrShiftingHistory(models.Model):
    _name = 'hr.shifting.history'
    _order = "id DESC"
    _list_id = 0

    """ Required and Optional fields """
    effective_from = fields.Date(string='Effective Date', required=True)
    effective_end = fields.Date(string='Effective End Date', required=True)


    """ Relational Fields """
    employee_id = fields.Many2one("hr.employee", string='Employee Name', required=True)
    shift_id = fields.Many2one("resource.calendar", string="Shift Name", required=True)

    """Shift Batch Relational Fields """
    shift_batch_id =fields.Many2one('hr.shift.employee.batch', string='Shift Batch')

    # @api.multi
    # def onchange_employee_id(self,shift_id, date_from, date_to, employee_id=False, contract_id=False):
    #     return



    # @api.onchange('effective_from')
    # def _onchange_effective_from(self):
    #     # print "---------------------- Lists--------------------", self.employee_id.id
    #     if self.effective_from and self.employee_id and self.shift_id:
    #         self.effective_from
    #         shifting = self.env['hr.shifting.history'].search([('employee_id', '=', self.employee_id.id),
    #                                                                ('effective_from', '<=', self.effective_from)], order='effective_from desc', limit=1)
    #         if shifting:
    #             print "---------------- Calling -------------------", shifting.id
    #             effective_from_tmp = int(datetime.datetime.strptime(self.effective_from, '%Y-%m-%d').strftime("%s"))
    #             effective_end_tmp = datetime.datetime.fromtimestamp(effective_from_tmp - 86400).strftime('%Y-%m-%d')
    #
    #             for shift in shifting:
    #                 shift.effective_end = effective_end_tmp
