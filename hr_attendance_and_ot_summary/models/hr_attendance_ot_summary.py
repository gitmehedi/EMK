from openerp import models, fields
from openerp import api

class HrAttendanceOTSummary(models.Model):    
    _name = 'hr.attendance.ot.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'    

    name = fields.Char(size=100, string='Title', required='True')       
    
    period = fields.Selection([
        ('january', "January"),
        ('february', "February"),
        ('march', "March"),
        ('april', "April"),
        ('may', "May"),
        ('june', "June"),
        ('july', "July"),
        ('august', "August"),
        ('september', "September"),
        ('october', "October"),
        ('november', "November"),
        ('december', "December"),
    ], required='True')
    
    state = fields.Selection([
        ('draft', "Draft"),
        ('generated', "Generated"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft')
    
    """ Relational Fields """
    
    line_ids = fields.One2many('hr.attendance.ot.summary.line','parent_id', string="Line Ids")
    
    @api.multi
    def action_generated(self):
        self.state = 'generated'        
    
    @api.multi
    def get_summary_data(self):
        print '------------------------------'
        print 'it works!!'
    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def action_confirm(self):
        for attendance in self:
            attendance.state = 'confirmed'
            
    @api.multi
    def action_done(self):
        for attendance in self:
            self.state = 'approved'
  