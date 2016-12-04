from openerp import api, exceptions, fields, models
from bzrlib.timestamp import format_patch_date

class CloneCalendarWizard(models.TransientModel):
    _name = "clone.calendar.wizard"
    
    holiday_year_id = fields.Many2one('calendar.holiday.type', string="Holiday Year")


    @api.multi
    def clone_calendar(self,context):
        ch_data = {}
        ch_data['name']= self.holiday_year_id.name
        ch_data['status']= self.holiday_year_id.status
        ch_insert = self.env['calendar.holiday.type'].create(ch_data)

        chtd_obj = self.env['calendar.holiday.type.details']
        pub_data= chtd_obj.search([('public_type_id','=',self.holiday_year_id.id)])
        week_data= chtd_obj.search([('weekly_type_id','=',self.holiday_year_id.id)])
        
        if ch_create:
            self.insert_holiday(pub_data,context,ch_create)
            self.insert_holiday(week_data,context,ch_create)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'calendar.holiday.type',
            'res_model': 'calendar.holiday.type',
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

            self.env['calendar.holiday.type.details'].create(default)
            
            