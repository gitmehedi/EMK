from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class CloneCalendarWizard(models.TransientModel):
    _name = "clone.calendar.wizard"
    
    holiday_year_id = fields.Many2one('calendar.holiday.type', string="Holiday Year")


    @api.multi
    def clone_calendar(self,context):
        obj = self.env['calendar.holiday.type.details']
        pub_data= obj.search([('public_type_id','=',self.holiday_year_id.id)])
        week_data= obj.search([('weekly_type_id','=',self.holiday_year_id.id)])

        self.insert_holiday(pub_data,context)
        self.insert_holiday(week_data,context)


        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'calendar.holiday.type',
            'res_model': 'calendar.holiday.type',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': context['active_id']
        }

    def insert_holiday(self,data,context):
        obj = self.env['calendar.holiday.type.details']
        print data,"---------------------data------------------",context
        for val in data:
            print "------------------individual data------------------",val
            default = {}


            default['date'] = val.date
            default['status'] = val.status

            print  "---public type id ",val.public_type_id
            if val.public_type_id:
                default['public_type_id'] = context['active_id']
                default['type'] = "Public Holiday"
                default['name'] = val.name
                default['color'] = "YELLOW"
            else:
                default['weekly_type_id'] = context['active_id']
                default['weekly_type'] = val.weekly_type


            print  "---weekly type id ", val.weekly_type_id

            print "---------default------------------------",default

            obj.create(default)