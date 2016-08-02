from openerp import api, exceptions, fields, models
from openerp.addons.helper import validator

class CloneCalendarWizard(models.TransientModel):
    _name = "clone.calendar.wizard"
    
    holiday_year_id = fields.Many2one('calendar.holiday.type', string="Holiday Year")


    @api.multi
    def clone_calendar(self,context):
        obj= self.env['calendar.holiday.type'].browse(context['active_id'])
        res = obj.clone_calendar(context)

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'calendar.holiday.type',
            'res_model': 'calendar.holiday.type',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': res.id
        }
