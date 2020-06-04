from openerp import models, fields,_
from openerp import api
from openerp.exceptions import UserError, ValidationError

class AttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'
    _order = 'id desc'

    name = fields.Char(size=100, string='Title', required='True')
    period = fields.Many2one("date.range", "Period", required=True,
                             domain="[('type_id.holiday_month', '=', True)]")
    company_id = fields.Many2one('res.company', string='Company', required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft',track_visibility='onchange')

    #button_show = fields.Boolean(string='Check')

    """ Relational Fields """
    att_summary_lines = fields.One2many('hr.attendance.summary.line', 'att_summary_id', string='Summary Lines',track_visibility='onchange')

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
        self.att_summary_lines.write({'state': 'draft'})
        
    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
        self.att_summary_lines.write({'state': 'confirmed'})
            
    @api.multi
    def action_done(self):
        self.state = 'approved'
        self.att_summary_lines.write({'state':'approved'})

    # Show a msg for applied & approved state should not be delete
    @api.multi
    def unlink(self):
        for summary in self:
            if summary.state != 'draft':
                raise UserError(_('You can not delete this.'))
            summary.att_summary_lines.unlink()
        return super(AttendanceSummary,self).unlink()