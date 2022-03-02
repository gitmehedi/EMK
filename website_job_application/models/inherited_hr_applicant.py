from odoo import models, fields, api


class InheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    father_name = fields.Char(string='Father Name', size=60, track_visibility='onchange')
    mother_name = fields.Char(string='Mother Name', size=60, track_visibility='onchange')
    partner_last_name = fields.Char(string='Partner Last Name', size=60, track_visibility='onchange')
    birth_date = fields.Char(string='Date of Birth', track_visibility='onchange')
    birth_city = fields.Char(string='Home District', track_visibility='onchange')
    nationality = fields.Char(string='Nationality', size=60, track_visibility='onchange')
    gender_id = fields.Many2one('res.gender', track_visibility='onchange')
    religion = fields.Char('res.religion', string='Religion', track_visibility='onchange')

    """Present Address"""
    pre_address_1 = fields.Char(string='House and Road(Name/No)', track_visibility='onchange')
    pre_address_2 = fields.Char(string='Vill/Para/Moholla', track_visibility='onchange')
    pre_zip_postal = fields.Char(string='Post Code', track_visibility='onchange')
    pre_district = fields.Char(string='District', track_visibility='onchange')
    pre_country_id = fields.Char(string='Country', track_visibility='onchange')

    """Permanent Address"""
    per_address_1 = fields.Char(string='House and Road(Name/No)', track_visibility='onchange')
    per_address_2 = fields.Char(string='Vill/Para/Moholla', track_visibility='onchange')
    per_zip_postal = fields.Char(string='Post Code', track_visibility='onchange')
    per_district = fields.Char(string='District', track_visibility='onchange')
    pre_country_id = fields.Char(string='Country', track_visibility='onchange')

    @api.multi
    def write(self, vals):
        print(vals)
        res = super(InheritedHrApplicant, self).write(vals)
        # for val in vals['description'].split("\n"):
        #     value = val.split(":")
        #     if len(value) > 1:
        #         super(InheritedHrApplicant, self).write({value[0].encode("utf-8").strip(): str(value[1].encode('utf-8').strip())})
        print(res)
        return res
