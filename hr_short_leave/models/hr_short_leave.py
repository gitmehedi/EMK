from openerp import models, fields
import datetime
from openerp import api

class HrShortLeave(models.Model):
    _name = 'hr.short.leave'
    _description = "Short Leave"
    _order = 'name desc'
    
    name = fields.Char('Description',required=True)
    payslip_status = fields.Boolean('Reported in last payslips',
        help='Green this button when the leave has been taken into account in the payslip.')
    report_note = fields.Text('HR Comments')
    notes = fields.Text('Reasons', readonly=True)
    number_of_days_temp = fields.Float('Allocation Days', copy=False)
    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "To Approved"),
        ('approved', "Approved"),
        ('refuse', 'Refused'),
    ], default='draft')
    
    #category_id = fields.Many2one('hr.employee.category', string='Employee Tag', readonly=True)
    holiday_type = fields.Selection([
        ('employee', 'By Employee'),
        ('category', 'By Employee Tag')
    ], string='Allocation Mode', readonly=True, required=True, default='employee')
    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee,
                                  required=True, ondelete='cascade', index=True)
                                 
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id" , store=True)  
    
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def action_confirm(self):
        self.state = 'applied'
                       
    @api.multi
    def action_approve(self):
        self.state = 'approved'
        
    @api.multi
    def action_refuse(self):
        self.state = 'refuse'
            
        
        
        
        
        