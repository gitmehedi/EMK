from openerp import models, fields, api
from .. models.attendance_processor import AttendanceProcessor

class HrAttendanceSummaryWizard(models.TransientModel):
    _name = 'attendance.summary.wizard.a'
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel_1_a', 'payslip_id',
                                    'employee_id', 'Employees',domain="[('operating_unit_id','=',operating_unit_id)]")

    @api.multi
    def process_employee_line(self,context):
        vals = {}
        line_obj = self.env['hr.attendance.summary.line']
        #holiday_ins = self.env['hr.holidays']

        summaryId = context['active_id']

        operating_unit_id = self.env['hr.attendance.summary'].browse(summaryId).operating_unit_id.id

        selected_ids_for_line = line_obj.search([('att_summary_id', '=', summaryId)])
        inserted_employee_ids = set([val.employee_id.id for val in selected_ids_for_line])
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids)-(inserted_employee_ids))

        attendanceProcess = self.env['hr.attendance.summary.temp']
        attendanceProcess.process(duplicate_employee_ids_filter, summaryId, operating_unit_id)




        # for val in self.employee_ids:
        #     if val.id in duplicate_employee_ids_filter:
        #         #leave_days = holiday_ins.search([('employee_id','=',val.id)])
        #
        #         #Hardcoded values for now
        #         vals['employee_id'] = val.id
        #         vals['attendance_1'] = 1
        #         vals['attendance_summary'] = 1
        #         vals['over_time_1'] = 1
        #         vals['over_time_summary'] = 1
        #         vals['parent_id'] = context['active_id']
        #
        #         line_obj.create(vals)
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.attendance.summary',
            'res_model': 'hr.attendance.summary',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': context['active_id']
        }
