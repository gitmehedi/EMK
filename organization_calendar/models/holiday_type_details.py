from openerp import models, fields, api, exceptions

class CalendarHolidayTypeDetails(models.Model):
    _name='calendar.holiday.type.details'


    name = fields.Char(size=100, string="Title")
    date = fields.Datetime(string="Date")
    weekly_type = fields.Selection([('saturday', 'Saturday'), ('sunday', 'Sunday'),('monday', 'Monday'),('tuesday', 'Tuesday'),('wednesday', 'Wednesday')
                             ,('thursday', 'Thurday'),('friday', 'Friday')])
    status = fields.Boolean(string='Status', default=True)

    # many2one fields

    public_type_id = fields.Many2one('calendar.holiday.type')
    weekly_type_id = fields.Many2one('calendar.holiday.type')

    @api.multi
    def clone_calendar(self, default=None):
        default = dict(default or {})
        # if default['create_version']:
        #     # Set Value for the new record
        #     default['version'] = self.version + 1
        #     default['ref_style'] = self.id
        #     default['name'] = self.name
        # else:
        #     default['style_id'] = ''
        #     default['version'] = 1

        res = super(CalendarHolidayTypeDetails, self).copy(default)

        # # Update the current record
        # if default['create_version']:
        #     self.write({'visible': False, 'style_id': res.id})
        #     for st in self.style_ids:
        #         st.write({'style_id': res.id})
        return res