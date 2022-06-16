from odoo import api, fields, models, _


class HR_Academic(models.Model):

    _inherit = "hr.academic"

    passed_date = fields.Date('Passed Date', required=True, track_visibility="onchange")
    passed_institute = fields.Char('Institute Name', track_visibility="onchange")


class HR_Professional(models.Model):
    _inherit = "hr.experience"

    employer_name = fields.Char('Employer Name', track_visibility="onchange")

class HR_Certification(models.Model):
    _inherit = "hr.certification"

    passed_date = fields.Date('Passed Date', required=True, track_visibility="onchange")
    issued_by = fields.Char('Issued By', track_visibility="onchange")