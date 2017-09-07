# -*- coding: utf-8 -*-
# ©  2016 Md Mehedi Hasan <md.mehedi.info@gmail.com>

from openerp import fields, models, api
from openerp.exceptions import Warning as UserError


class HrPublicHolidaysLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = "date, name desc"

    name = fields.Char('Name')
    date = fields.Date('Date')
    status = fields.Boolean(string='Status', default=True)

    variable = fields.Boolean('Date may change')
    state_ids = fields.Many2many('res.country.state','hr_holiday_public_state_rel','line_id','state_id','Related States')
    
    """many2one fields """ 

    public_type_id = fields.Many2one('hr.holidays.public', string="Public Type")
    weekly_type_id = fields.Many2one('hr.holidays.public', string="Weekly Type" )

    """ Selection fields """
    
    weekly_type = fields.Selection([
        ('friday', 'Friday'),
        ('saturday', 'Saturday'), 
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ])


    @api.multi
    def name_get(self):
        res = []
        for holiday in self:
            if holiday.date:
                res.append((holiday.id, holiday.name + ', ' + holiday.date))
            else:
                res.append((holiday.id, holiday.name))
        return res

#     @api.one
#     @api.constrains('date', 'state_ids')
#     def _check_date_state(self):
#         if fields.Date.from_string(self.date).year != self.public_type_id.year:
#             raise UserError(
#                 'Dates of holidays should be the same year '
#                 'as the calendar year they are being assigned to'
#             )
#         if self.state_ids:
#             domain = [('date', '=', self.date),
#                       ('public_type_id', '=', self.public_type_id.id),
#                       ('state_ids', '!=', False),
#                       ('id', '!=', self.id)]
#             holidays = self.search(domain)
#             for holiday in holidays:
#                 if self.state_ids & holiday.state_ids:
#                     raise UserError('You can\'t create duplicate public '
#                                     'holiday per date %s and one of the '
#                                     'country states.' % self.date)
#         domain = [('date', '=', self.date),
#                   ('public_type_id', '=', self.public_type_id.id),
#                   ('state_ids', '=', False)]
#         if self.search_count(domain) > 1:
#             raise UserError('You can\'t create duplicate public holiday '
#                             'per date %s.' % self.date)
#         return True
