from odoo import api, fields, models

class HrHolidaysImportError(models.Model):
    _name = 'hr.holidays.import.error'

    name = fields.Char(string='Discription')
    state = fields.Char(string='Status')
    employee_id = fields.Char(string='Employee')
    holiday_status_id = fields.Char(string='Leave Type')
    number_of_days = fields.Char(string='Remaining Days')
    type = fields.Char(string='Request Type')

    import_id = fields.Many2one('hr.holidays.import', 'id', ondelete='cascade')
    