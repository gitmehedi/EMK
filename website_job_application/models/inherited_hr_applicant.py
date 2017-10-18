from odoo import models, fields, api


class InheritedHrApplicant(models.Model):
    _inherit = 'hr.applicant'

    father_name = fields.Char(string='Father Name', size=60)
    mother_name = fields.Char(string='Mother Name', size=60)
    partner_name_bangla = fields.Char(string='Partner Name Bangla', size=60)
    national_id = fields.Char(string='National ID', size=60)
    birth_registration_no = fields.Char(string='Birth Registration No', size=60)
    birth_date = fields.Char(string='Birth Date', size=60)
    birth_city = fields.Char(string='Home District', size=60)
    nationality = fields.Char(string='Nationality', size=60)
    gender = fields.Char(string='Gender', size=60)
    religion = fields.Char(string='Religion', size=60)
    occupation = fields.Char(string='Occupation', size=60)
    divisional_candiate = fields.Char(string='Divisional Candiate', size=60)
    ex_service_personnel = fields.Char(string='Ex-Service Personnel', size=60)
    quota = fields.Char(string='Quota', size=60)
    experience_remarks = fields.Char(string='Experience Remarks', size=60)
    curriculam_activities = fields.Char(string='Extra Curriculam Activities', size=60)
    authorize_district = fields.Char(string='Authorize District', size=60)

    """Present Address"""
    pre_address_1 = fields.Char(string='House and Road(Name/No)', size=60)
    pre_address_2 = fields.Char(string='Vill/Para/Moholla', size=60)
    pre_city_town = fields.Char(string='Union/Ward', size=60)
    pre_state_province = fields.Char(string='Upozilla', size=60)
    pre_zip_postal = fields.Char(string='Post Code', size=60)
    pre_district = fields.Char(string='District', size=60)

    """Permanent Address"""
    per_address_1 = fields.Char(string='House and Road(Name/No)', size=60)
    per_address_2 = fields.Char(string='Vill/Para/Moholla', size=60)
    per_city_town = fields.Char(string='Union/Ward', size=60)
    per_state_province = fields.Char(string='Upozilla', size=60)
    per_zip_postal = fields.Char(string='Post Code', size=60)
    per_district = fields.Char(string='District', size=60)

    """Treasury Information"""
    treasury_challan = fields.Char(string="Treasury Challan")
    treasury_date = fields.Char(string="Treasury Date")
    bank_branch_name = fields.Char(string="Bank and Branch Name")

    """Educational Information"""

    """SSC"""
    exm_ssc = fields.Char(string='SSC', size=60)
    exm_ssc_subject = fields.Char(string='SSC Subject', size=60)
    exm_ssc_institute = fields.Char(string='SSC Institute', size=60)
    exm_ssc_passing_year = fields.Char(string='SSC Passing Year', size=60)
    exm_ssc_board = fields.Char(string='SSC Board', size=60)
    exm_ssc_class = fields.Char(string='SSC GPA/CLASS', size=60)

    """HSC"""
    exm_hsc = fields.Char(string='HSC', size=60)
    exm_hsc_subject = fields.Char(string='HSC Subject', size=60)
    exm_hsc_institute = fields.Char(string='HSC Institute', size=60)
    exm_hsc_passing_year = fields.Char(string='HSC Passing Year', size=60)
    exm_hsc_board = fields.Char(string='HSC Board', size=60)
    exm_hsc_class = fields.Char(string='HSC GPA/CLASS', size=60)

    """BSC"""
    exm_bsc = fields.Char(string='BSC', size=60)
    exm_bsc_subject = fields.Char(string='BSC Subject', size=60)
    exm_bsc_institute = fields.Char(string='BSC Institute', size=60)
    exm_bsc_passing_year = fields.Char(string='BSC Passing Year', size=60)
    exm_bsc_board = fields.Char(string='BSC Board', size=60)
    exm_bsc_class = fields.Char(string='BSC GPA/CLASS', size=60)

    """MSC"""
    exm_msc = fields.Char(string='MSC', size=60)
    exm_msc_subject = fields.Char(string='MSC Subject', size=60)
    exm_msc_institute = fields.Char(string='MSC Institute', size=60)
    exm_msc_passing_year = fields.Char(string='MSC Passing Year', size=60)
    exm_msc_board = fields.Char(string='MSC Board', size=60)
    exm_msc_class = fields.Char(string='MSC GPA/CLASS', size=60)

    """OTHERS"""
    exm_other = fields.Char(string='Other', size=60)
    exm_other_subject = fields.Char(string='Other Subject', size=60)
    exm_other_institute = fields.Char(string='Other Institute', size=60)
    exm_other_passing_year = fields.Char(string='Other Passing Year', size=60)
    exm_other_board = fields.Char(string='Other Board', size=60)
    exm_other_class = fields.Char(string='Other GPA/CLASS', size=60)

    @api.multi
    def write(self, vals):
        res = super(InheritedHrApplicant, self).write(vals)
        for val in vals['description'].split("\n"):
            value = val.split(":")
            if len(value) > 1:
                super(InheritedHrApplicant, self).write({value[0].encode("utf-8").strip(): str(value[1].encode('utf-8').strip())})

        return res