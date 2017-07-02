from odoo import api,fields,models

class HrAttendanceGraceTime(models.Model):
    _name = 'hr.attendance.grace.time'

    grace_time = fields.Float(string='Grace Time')
    effective_from_date=fields.Float(string='From Effective Day')
    effective_to_date = fields.Float(string='To Effective Day')
    company_id = fields.Many2one('res.company', string='Company',
                                 states={'applied': [('readonly', True)], 'approved': [('readonly', True)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )


