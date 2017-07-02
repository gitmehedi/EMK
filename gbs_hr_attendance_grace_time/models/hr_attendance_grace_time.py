from odoo import api,fields,models

class HrAttendanceGraceTime(models.Model):
    _name = 'hr.attendance.grace.time'

    grace_time = fields.Float(string='Grace Time',required='True')
    effective_from_date=fields.Date(string='From Effective Day' ,required='True',default=fields.Date.today())
    effective_to_date = fields.Date(string='To Effective Day')
    company_id = fields.Many2one('res.company', string='Company',required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )


