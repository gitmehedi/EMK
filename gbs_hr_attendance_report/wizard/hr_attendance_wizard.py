from openerp import models, fields


class HrBankSelectionWizard(models.TransientModel):
    _name = 'hr.attendance.report.wizard'

    check_in_out = fields.Selection([
        ('check_in', 'Check In'),
        ('check_out', 'Check Out'),
        ], string = 'Check Type', required=True, default="check_in")