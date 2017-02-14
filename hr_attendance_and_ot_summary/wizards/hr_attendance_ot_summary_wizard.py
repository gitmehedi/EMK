from openerp import models, fields, api

class HrAttendanceOTSummaryWizard(models.TransientModel):
    _name = 'hr.attendance.ot.summary.wizard'
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel_1', 'payslip_id', 
                                    'employee_id', 'Employees')
    
    @api.multi
    def process_employee_line(self,context):
        vals = {}
        line_obj = self.env['hr.attendance.ot.summary.line']
        holiday_ins = self.env['hr.holidays']
        
        selected_ids_for_line  = line_obj.search([('parent_id', '=', context['active_id'])])
        inserted_employee_ids = set([val.employee_id.id for val in selected_ids_for_line])
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids)-(inserted_employee_ids))

        
        for val in self.employee_ids:
            if val.id in duplicate_employee_ids_filter:
                leave_days = holiday_ins.search([('employee_id','=',val.id)])            
                pending_leave = sum([ v.number_of_days for v in leave_days]) 
                
                ''' Maximum and minimum earned leave days to be encashed '''
                if pending_leave is not None:
                    if pending_leave > 10:
                        leave_days_to_be_encashed = 10
                    elif pending_leave == 5: 
                        leave_days_to_be_encashed = 5
                    elif pending_leave > 5:
                        leave_days_to_be_encashed = pending_leave
                    elif pending_leave < 5:
                        leave_days_to_be_encashed = 0        
                
                vals['employee_id'] = val.id
                vals['attendance_1'] = pending_leave
                vals['attendance_summary'] = leave_days_to_be_encashed
                vals['over_time_1'] = True
                vals['over_time_summary'] = True
                vals['parent_id'] = context['active_id']
                
                line_obj.create(vals)
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.attendance.ot.summary',
            'res_model': 'hr.attendance.ot.summary',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': context['active_id']
        }
