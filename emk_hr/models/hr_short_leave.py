from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeShortLeave(models.Model):

    _inherit = "hr.short.leave"


    @api.constrains('number_of_days')
    def _check_number_of_days(self):
        if self.number_of_days:
            if self.number_of_days>5.00 or self.number_of_days<4.00:
                raise ValidationError('Short leave takes only 4 hours!')
            else:
                pass