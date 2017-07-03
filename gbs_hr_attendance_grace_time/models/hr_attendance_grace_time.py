from odoo import api,fields,models,_
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class HrAttendanceGraceTime(models.Model):
    _name = 'hr.attendance.grace.time'
    _order = 'effective_from_date desc,id desc'
    _rec_name='effective_from_date'

    grace_time = fields.Float(string='Grace Time',required='True')
    effective_from_date=fields.Date(string='From Effective Day' ,required='True', default = fields.Date.today())
    effective_to_date = fields.Date(string='To Effective Day')
    company_id = fields.Many2one('res.company', string='Company',required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', 'Select Operating Unit',
                                        required='True',
                                        default=lambda self: self.env['res.users'].
                                        operating_unit_default_get(self._uid)
                                        )

    @api.onchange('effective_from_date')
    def onchange_effective_from_date(self):
        update_to_date=''
        if self.effective_from_date:
            current_from_date = datetime.strptime(self.effective_from_date, "%Y-%m-%d")
            update_to_date = current_from_date - timedelta(days=1)

        query = """select MAX(id) from hr_attendance_grace_time"""
        self._cr.execute(query, tuple())
        get_previous_row_id = self._cr.fetchone()

        if get_previous_row_id:
            query =""" UPDATE hr_attendance_grace_time SET effective_to_date = %s WHERE id = %s"""
            self._cr.execute(query, tuple([update_to_date,get_previous_row_id]))
            return

    @api.constrains('effective_from_date')
    def _check_validation(self):
        query = """select MAX(id),MAX(effective_from_date) from hr_attendance_grace_time"""
        self._cr.execute(query, tuple())
        get_previous_row_value = self._cr.fetchall()
        get_previous_row_effective_from_date = get_previous_row_value[0][1]
        if  get_previous_row_effective_from_date> self.effective_from_date :
            raise ValidationError(_("Present effective date can not less then previous effective date!!"))