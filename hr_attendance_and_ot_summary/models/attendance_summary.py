from openerp import models, fields
from openerp import api

class AttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'    

    name = fields.Char(size=100, string='Title', required='True')
    period = fields.Many2one("account.period", "Period", required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('generated', "Generated"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft')


    """ Relational Fields """
    att_summary_lines = fields.One2many('hr.attendance.summary.line', 'att_summary_id', string='Summary Lines')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(AttendanceSummary, self).fields_view_get(view_id, view_type, toolbar, submenu)
    #
    #     return res
    
    @api.multi
    def action_generated(self):
        self.state = 'generated'        

    
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
