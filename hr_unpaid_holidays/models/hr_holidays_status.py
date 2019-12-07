# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    unpaid = fields.Boolean(
        'Unpaid',
        help="If checked, leave will considered as unpaid.", default=False
    )