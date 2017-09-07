# -*- coding: utf-8 -*-
# ©  2016 Md Mehedi Hasan <md.mehedi.info@gmail.com>
import datetime
import time

from datetime import date
from openerp import fields, models, api
from openerp.exceptions import Warning as UserError


class HrPublicHolidays(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'name'
    _order = "id"

    display_name = fields.Char("Name",compute="_compute_display_name", readonly=True, store=True)
    year = fields.Integer("Calendar Year", default=date.today().year)
    country_id = fields.Many2one('res.country','Country')
    
    name = fields.Char(size=100, string="Title", required="True")
    status = fields.Boolean(string='Status', default=True)

    """ many2one fields """ 
    year_id = fields.Many2one('hr.leave.fiscal.year', string="Leave Year")

    """ one2many fields """
    public_details_ids = fields.One2many('hr.holidays.public.line', 'public_type_id', string="Public Details")
    weekly_details_ids = fields.One2many('hr.holidays.public.line', 'weekly_type_id', string="Weekly Details")
    """ many2many fields """
    operating_unit_ids = fields.Many2many('operating.unit', 'public_holiday_operating_unit_rel','public_holiday_id','operating_unit_id',string="Operating Unit")

    
    """ Custom activity """

    @api.multi
    def geneare_yearly_calendar(self):
        vals = {}
        chd_obj = self.env["calendar.holiday"]
        data = chd_obj.search([('year_id','=',self.year_id.id)])
        
        if data:
            data.unlink()
        
        for val in self.public_details_ids:
            vals['name'] = val.name
            vals['type'] = "public"
            vals['date'] = val.date
            vals['color'] = "RED"
            vals['status'] = True

            chd_obj.create(vals)

        for val in self.weekly_details_ids:
            vals['name'] = "Weekly Holiday"
            vals['type'] = "weekly"
            vals['color'] = "Yellow"
            vals['status'] = True
            vals['year_id'] = self.year_id.id

            if not self.year_id.date_start:
                raise exceptions.ValidationError("Please provide start date of fiscal year")
            if not self.year_id.date_stop:
                raise exceptions.ValidationError("Please provide end date of fiscal year")

            start_date = self.year_id.date_start.split('-')
            end_date = self.year_id.date_stop.split('-')

            days = datetime.datetime(int(end_date[0]), int(end_date[1]), int(end_date[2]))-datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2]))

            noOfDays = days.days + 1
            curTime = time.mktime(datetime.datetime(int(start_date[0]), int(start_date[1]), int(start_date[2])).timetuple())

            for i in range(noOfDays):
                searchTime = (i * 86400 + curTime)
                dayName = datetime.datetime.fromtimestamp(int(searchTime))
                if dayName.strftime('%A') == val.weekly_type.title():
                    vals['date'] = dayName
                    chd_obj.create(vals)

        return True
    
    @api.one
    @api.constrains('year_id', 'country_id')
    def _check_year(self):
        if self.country_id:
            domain = [('year_id', '=', self.year_id.id),
                      ('country_id', '=', self.country_id.id),
                      ('id', '!=', self.id)]
        else:
            domain = [('year_id', '=', self.year_id.id),
                      ('country_id', '=', False),
                      ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError('You can\'t create duplicate public holiday '
                            'per year')
        return True

    @api.one
    @api.depends('year', 'name')
    def _compute_display_name(self):
        if self.year:
            self.display_name = '%s (%s)' % (self.name, self.year)
        else:
            self.display_name = self.name

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.name))
        return result

    @api.model
    @api.returns('hr.holidays.public.line')
    def get_holidays_list(self, year, employee_id=None):
        """
        Returns recordset of hr.holidays.public.line
        for the specified year and employee
        :param year: year as string
        :param employee_id: ID of the employee
        :return: recordset of hr.holidays.public.line
        """
        holidays_filter = [('year', '=', year)]
        employee = False
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)

        pholidays = self.search(holidays_filter)
        if not pholidays:
            return list()

        states_filter = [('public_type_id', 'in', pholidays.ids)]

        hhplo = self.env['hr.holidays.public.line']
        holidays_lines = hhplo.search(states_filter)
        return holidays_lines

    @api.model
    def is_public_holiday(self, selected_date, employee_id=None):
        """
        Returns True if selected_date is a public holiday for the employee
        :param selected_date: datetime object or string
        :param employee_id: ID of the employee
        :return: bool
        """
        if isinstance(selected_date, basestring):
            selected_date = fields.Date.from_string(selected_date)
        holidays_lines = self.get_holidays_list(
            selected_date.year, employee_id=employee_id)
        if holidays_lines and len(holidays_lines.filtered(
                lambda r: r.date == fields.Date.to_string(selected_date))):
            return True
        return False
    
    
