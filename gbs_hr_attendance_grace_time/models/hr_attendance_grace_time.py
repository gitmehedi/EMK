from odoo import api,fields,models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date,datetime, timedelta


class HrAttendanceGraceTime(models.Model):
    _name = 'hr.attendance.grace.time'
    _order = 'effective_from_date desc,id desc'
    _rec_name='effective_from_date'

    @api.multi
    def _get_current_date(self):
        return date.today()

    grace_time = fields.Float(string='Grace Time',required='True',default = 00.50)
    effective_from_date=fields.Date(string='From Effective Day' ,required='True',default = _get_current_date)
    effective_to_date = fields.Date(string='To Effective Day')
    company_id = fields.Many2one('res.company', string='Company',required='True',
                                 default=lambda self: self.env['res.company']._company_default_get())
    operating_unit_id = fields.Many2one('operating.unit', string='Select Operating Unit',
                                        required='True',
                                        )

    @api.onchange('company_id')
    def onchange_company_id(self):
        com_obj = self.env['operating.unit'].search([('company_id', '=', self.company_id.id)])
        res_op_list = com_obj.ids
        return {'domain': {'operating_unit_id': [('id', 'in', res_op_list)]}}

    @api.model
    def create(self, vals):
        from_date= vals['effective_from_date']
        if from_date:
            current_from_date = datetime.strptime(from_date, "%Y-%m-%d")
            update_to_date = current_from_date - timedelta(days=1)

            query = """select MAX(id) from hr_attendance_grace_time where company_id=%s and operating_unit_id=%s"""
            self._cr.execute(query, tuple([vals['company_id'],vals['operating_unit_id']]))
            get_previous_row_id = self._cr.fetchone()

            if get_previous_row_id:
                query = """ UPDATE hr_attendance_grace_time SET effective_to_date = %s WHERE id = %s"""
                self._cr.execute(query, tuple([update_to_date, get_previous_row_id]))

            return super(HrAttendanceGraceTime, self).create(vals)

    @api.constrains('effective_from_date')
    def _check_validation(self):
        query = """select MAX(effective_from_date) from hr_attendance_grace_time where company_id=%s and operating_unit_id=%s"""
        self._cr.execute(query, tuple([self.company_id.id,self.operating_unit_id.id]))
        get_previous_row_effective_from_date = self._cr.fetchone()
        if get_previous_row_effective_from_date[0] > self.effective_from_date:
            raise ValidationError(_("Present effective date can not less then previous effective date!!"))

    @api.multi
    def write(self, vals):
        from_date= self.effective_from_date
        query = """select id from hr_attendance_grace_time where company_id=%s and operating_unit_id=%s order by id desc limit 2"""
        self._cr.execute(query, tuple([self.company_id.id,self.operating_unit_id.id]))
        get_previous_row_value = self._cr.fetchall()

        if len(get_previous_row_value)>1:
            current_from_date = datetime.strptime(from_date, "%Y-%m-%d")
            update_to_date = current_from_date - timedelta(days=1)
            if get_previous_row_value:
                get_previous_row_id = get_previous_row_value[1][0]
                if get_previous_row_id:
                    query = """ UPDATE hr_attendance_grace_time SET effective_to_date = %s WHERE id = %s"""
                    self._cr.execute(query, tuple([update_to_date, get_previous_row_id]))
        return super(HrAttendanceGraceTime, self).write(vals)

    @api.multi
    def unlink(self):
        for a in self:
            if str(a.effective_from_date) < str(date.today()):
                user = self.env.user.browse(self.env.uid)
                if user.has_group('base.group_system'):
                    pass
                else:
                    raise UserError(_('You can not delete previous dated record.'))

            return super(HrAttendanceGraceTime, self).unlink()