from odoo import api, fields, models
import datetime
#from datetime import datetime

class InheritHrContract(models.Model):
    _inherit = 'hr.contract'

    bonus_application = fields.Boolean('Bonus Application',compute='_compute_bonus_applicable')

    @api.one
    def _compute_bonus_applicable(self):
        self.bonus_application = False
        #if datetime.strptime(self.trial_date_end, '%Y-%m-%d') > datetime.date.today():
        # current_date = datetime.date.today()
        # if self.trial_date_end > current_date:
        #     self.bonus_application = True


