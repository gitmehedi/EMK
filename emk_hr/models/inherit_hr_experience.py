from odoo import api, fields, models, _
from odoo.addons.opa_utility.helper.utility import Utility
from odoo.exceptions import UserError, ValidationError


class HR_Academic(models.Model):

    _inherit = "hr.academic"

    passed_date = fields.Date('Passed Date', required=True, track_visibility="onchange")


class HR_Professional(models.Model):
    _inherit = "hr.experience"

    passed_date = fields.Date('Passed Date', required=True, track_visibility="onchange")

class HR_Certification(models.Model):
    _inherit = "hr.certification"

    passed_date = fields.Date('Passed Date', required=True, track_visibility="onchange")