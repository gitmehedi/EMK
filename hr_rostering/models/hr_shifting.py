from openerp import api, fields, models, _,SUPERUSER_ID
from openerp.exceptions import UserError, ValidationError


class HrShifting(models.Model):
    _inherit = ['resource.calendar.attendance']

    # Fields of Model
    ot_hour_from = fields.Float(string='OT from')
    ot_hour_to = fields.Float(string='OT to')
    isIncludedOt = fields.Boolean(string='Is it included OT', default=False)
    grace_time = fields.Float(string='Grace Time', default='1.5')
    calendar_id = fields.Many2one("resource.calendar", string="Resource's Calendar", required=False)

    # @api.constrains('ot_hour_from','hour_from','hour_to')
    # def _check_validation(self):
    #     if (self.hour_from >= self.hour_to) or (self.ot_hour_from >= self.ot_hour_to) or (self.hour_to >= self.ot_hour_from) :
    #         raise Warning(_("OT to can not less then OT from or \n OT from can not less then Work to or \n Work to can not less then Work from"))

class HrResourceCal(models.Model):
    _name = "resource.calendar"
    _inherit = ['resource.calendar','mail.thread']

    name = fields.Char(required=True,states={'applied': [('readonly', True)],'approved': [('readonly', True)]})
    manager = fields.Many2one('res.users', string='Workgroup Manager', default=lambda self: self.env.uid,
                            states = {'applied': [('readonly', True)], 'approved': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Company',states = {'applied': [('readonly', True)], 'approved': [('readonly', True)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', string='Working Time',copy=True,
                                     states={'applied': [('readonly', True)], 'approved': [('readonly', True)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'applied'

    @api.multi
    def action_done(self):
        self.state = 'approved'

    @api.multi
    def action_reset(self):
        if self.state=='approved':
            if SUPERUSER_ID == self.env.user.id:
                self.write({'state': 'draft'})
            else:
                raise UserError(_('Only Admin can reset in this stage.'))
        else:
            self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for bill in self:
            if bill.state != 'draft':
                raise UserError(_('You can not delete this.'))
            bill.leave_ids.unlink()
        return super(HrResourceCal, self).unlink()



class HrEmployeeShifting(models.Model):
    _inherit = ['hr.employee']
    
    #Fields of Model
    current_shift_id = fields.Many2one('resource.calendar', compute='_compute_current_shift', string='Current Shift')    
    shift_ids = fields.One2many('hr.shifting.history', 'employee_id', string='Employee Shift History')


    @api.multi
    def _compute_current_shift(self):


        query = """SELECT h.shift_id FROM hr_shifting_history h
                                  WHERE h.employee_id = %s
                               ORDER BY h.effective_from DESC
                                  LIMIT 1"""
        for emp in self:
            self._cr.execute(query, tuple([emp.id]))
            res = self._cr.fetchall()
            if res:
                emp.current_shift_id = res[0][0]

