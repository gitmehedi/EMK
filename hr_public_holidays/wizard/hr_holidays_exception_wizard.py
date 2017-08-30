from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

class HrHolidaysExceptionWizard(models.TransientModel):
    _name = 'hr.holiday.exception.wizard'
    _description = 'Select Employee Batch'



