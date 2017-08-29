from odoo import api, fields, models

class HrHolidaysImportError(models.Model):
    _name = 'hr.holidays.import.error'

    employee_id = fields.Char(string='Employee')
    holiday_status_id = fields.Char(string='Leave Type')
    number_of_days_temp = fields.Char(string='Remaining Days')

    import_id = fields.Many2one('hr.holidays.import', 'id', ondelete='cascade')
    