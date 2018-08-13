from odoo import api, fields, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class InheritHrContract(models.Model):
    _inherit = 'hr.contract'

    bonus_applicable = fields.Boolean('Bonus Applicable',compute='_compute_bonus_applicable')

    @api.one
    def _compute_bonus_applicable(self):
        self.bonus_applicable = False
        current_date = datetime.now().date()
        if self.trial_date_end > current_date.strftime(
                DEFAULT_SERVER_DATE_FORMAT):
            self.bonus_applicable = True


