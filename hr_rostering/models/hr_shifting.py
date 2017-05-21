from openerp import fields
from openerp import api,models,_
from openerp.exceptions import ValidationError,Warning


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

