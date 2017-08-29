from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime, timedelta

class HrShiftEmployeeBatch(models.Model):
    _name='hr.shift.employee.batch'

    name = fields.Char(string='Batch Name',required=True)
    effective_from = fields.Date(string='Effective Date',default=date.today())
    effective_end = fields.Date(string='Effective End Date')
    shift_id = fields.Many2one("resource.calendar", string="Shift Name")
    company_id = fields.Many2one('res.company', string='Company',required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    shift_emp_ids = fields.One2many('hr.shifting.history', 'shift_batch_id')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Name is already in use'),
    ]

    @api.multi
    def unlink(self):
        for a in self:
            if str(a.effective_from) < str(date.today()):
                user = self.env.user.browse(self.env.uid)
                if user.has_group('base.group_system'):
                    pass
                else:
                    raise UserError(_('You can not delete this.'))

            query = """ delete from hr_shifting_history where shift_batch_id=%s"""
            self._cr.execute(query, tuple([self.id]))
            return super(HrShiftEmployeeBatch, self).unlink()