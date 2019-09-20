from odoo.osv import osv, orm
from odoo import api,fields
from datetime import date

class daily_attendance_report(orm.TransientModel):
    _name='daily.attendance.report.wizard'

    @api.multi
    def _get_current_date(self):
        return date.today()


    required_date = fields.Date('Attendance Date',required='True',default=_get_current_date)

    company_id = fields.Many2one('res.company', 'Company',required=True,
        default=lambda self: self.env.user.company_id)

    operating_unit_id = fields.Many2one('operating.unit','Select Operating Unit',required=True,
        default=lambda self: self.env.user.default_operating_unit_id)

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.env.user.has_group('operating_unit.group_multi_operating_unit'):
            self.operating_unit_id= []
        return {'domain': {'operating_unit_id': ['|',('active','=', False),('company_id','=', self.company_id.id)]}}


    @api.multi
    def process_report(self):
        data = {}

        data['company_id'] = self.company_id.id
        data['required_date'] = self.required_date
        if self.operating_unit_id.name=='All':
            data['operating_unit_id']=False
        else:
            data['operating_unit_id'] = self.operating_unit_id.id
        # data['operating_unit_name'] = self.operating_unit_id.name or False

        return self.env['report'].get_action(self, 'gbs_hr_attendance_report.report_daily_att_doc', data=data)
