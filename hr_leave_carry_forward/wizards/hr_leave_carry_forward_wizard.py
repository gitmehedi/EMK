from odoo import models, fields, api


class HrLeaveCarryForwardWizard(models.TransientModel):
    _name = 'hr.leave.carry.forward.wizard'
    
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    
    @api.multi
    def process_employee_line(self,context):
        vals = {}
        vals1 = {}
        line_obj = self.env['hr.leave.carry.forward.line']
        holiday_ins = self.env['hr.holidays']        
        
        selected_ids_for_line  = line_obj.search([('parent_id', '=', context['active_id'])])
        inserted_employee_ids = set([val.employee_id.id for val in selected_ids_for_line])
        duplicate_employee_ids_filter = list(set(self.employee_ids.ids)-(inserted_employee_ids))
        
        for val in self.employee_ids:
            if val.id in duplicate_employee_ids_filter:
                leave_days = holiday_ins.search([('employee_id','=',val.id)])
                pending_leave = sum([ v.number_of_days for v in leave_days]) 
                
                ''' Maximum and minimum earned leave days to be carry forwarded '''
                """ Need to refactor """
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
               
                line_ids  = line_obj.search([('employee_id', '=', val.id)])

                #carry_forward_obj = self.env['hr.leave.carry.forward'].search(['leave_type','=',name.id])


                holiday_status_obj = self.env['hr.holidays.status'].search([('leave_carry_forward','=',True)])

                for hso in holiday_status_obj:
                    for l_id in line_ids:
                        vals1['holiday_status_id'] = hso.id  #leave type
                        vals1['employee_id'] = l_id.employee_id.id
                        vals1['holiday_type'] = 'employee'
                        vals1['number_of_days_temp'] = l_id.leave_days_to_be_caryy_forwarded
                        vals1['state'] = 'validate' #status
                        vals1['type'] = 'add' #type
                        vals1['name'] = hso.name #Description

                        holiday_ins.create(vals1)
            
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.leave.carry.forward',
            'res_model': 'hr.leave.carry.forward',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': context['active_id']
        }
