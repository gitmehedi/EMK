from openerp import api, exceptions, fields, models

class HrCalendarCloneWizard(models.TransientModel):
    _name = "hr.calendar.clone.wizard"
    
    holiday_year_id = fields.Many2one('hr.holidays.public', string="Holiday Year")


    @api.multi
    def clone_calendar(self,context):
        ch_data = {}
        ch_data['name']= 'Please set a Calendar Title and Calendar Year'
        ch_data['status']= self.holiday_year_id.status
        ch_insert = self.env['hr.holidays.public'].create(ch_data)

        chtd_obj = self.env['hr.holidays.public.line']
        pub_data= chtd_obj.search([('public_type_id','=',self.holiday_year_id.id)])
        week_data= chtd_obj.search([('weekly_type_id','=',self.holiday_year_id.id)])
        
        if ch_insert:
            self.insert_holiday(pub_data,context,ch_insert)
            self.insert_holiday(week_data,context,ch_insert)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'hr.holidays.public',
            'res_model': 'hr.holidays.public',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': ch_insert.id
        }


    def insert_holiday(self,data,context,ch_create):
        for val in data:
            default = {}
            default['date'] = val.date
            default['status'] = val.status

            if val.public_type_id:
                default['public_type_id'] = ch_create.id
                default['type'] = "Public Holiday"
                default['name'] = val.name
                default['color'] = "YELLOW"
            else:
                default['weekly_type_id'] = ch_create.id
                default['weekly_type'] = val.weekly_type

            self.env['hr.holidays.public.line'].create(default)
            
            