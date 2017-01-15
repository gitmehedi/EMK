from openerp import models, fields, api

class HrLeaveCarryForwardWizard(models.TransientModel):
    _name = 'hr.leave.carry.forward.wizard'
    
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 
                                    'employee_id', 'Employees')
    
    @api.multi
    def process_employee_line(self,context):
        vals = {}
        line_obj = self.env['hr.leave.carry.forward.line']
        holiday_ins = self.env['hr.holidays']
        
        
        for val in self.employee_ids:
            leave_days = holiday_ins.search([('employee_id','=',val.id)])
            pending_leave = sum([ v.number_of_days for v in leave_days]) 
            
            ''' Maximum and minimum earned leave days to be carry forwarded '''
            if pending_leave is not None:
                if pending_leave > 10:
                    leave_days_to_be_carry_forwarded = 10
                elif pending_leave == 5: 
                    leave_days_to_be_carry_forwarded = 5
                elif pending_leave > 5:
                    leave_days_to_be_carry_forwarded = pending_leave
                elif pending_leave < 5:
                    leave_days_to_be_carry_forwarded = 0  
            
            vals['employee_id'] = val.id
            vals['pending_leave'] = pending_leave
            vals['leave_days_to_be_caryy_forwarded'] = leave_days_to_be_carry_forwarded
            vals['want_to_carry_forward'] = True
            vals['parent_id'] = context['active_id']
            
            line_obj.create(vals)
        
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.leave.carry.forward',
            'res_model': 'hr.leave.carry.forward',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': context['active_id']
        }
