from odoo import api, fields, models

class HRHolidays(models.Model):
    _inherit = 'hr.holidays'

    first_approval = fields.Boolean('First Approval', default=False)

    @api.multi
    def check_first_approval(self):
        for h in self:
            h.first_approval = False


