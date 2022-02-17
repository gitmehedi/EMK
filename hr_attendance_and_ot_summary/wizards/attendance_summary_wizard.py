from openerp import models, fields, api


class HrAttendanceSummaryWizard(models.TransientModel):
    _name = 'attendance.summary.wizard.a'

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel_1_a', 'payslip_id',
                                    'employee_id', 'Employees', domain="[('operating_unit_id','=',operating_unit_id)]")

    @api.multi
    def process_employee_line(self, context):
        summery_id = context['active_id']

        operating_unit_id = self.env['hr.attendance.summary'].browse(summery_id).operating_unit_id.id
        selected_ids_for_line = self.env['hr.attendance.summary.line'].search([('att_summary_id', '=', summery_id)])
        inserted_employee_ids = [val.employee_id.id for val in selected_ids_for_line]
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids) - set(inserted_employee_ids))

        attendance_process = self.env['hr.attendance.summary.temp']
        attendance_process.process(duplicate_employee_ids_filter, summery_id, operating_unit_id)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.attendance.summary',
            'res_model': 'hr.attendance.summary',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': summery_id
        }
