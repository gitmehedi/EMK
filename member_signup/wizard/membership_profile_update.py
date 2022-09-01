from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class MembershipProfileUpdateWizard(models.TransientModel):
    _name = 'membership.profile.update.wizard'

    website = fields.Char(string='Website', track_visibility="onchange")
    occupation = fields.Many2one('member.occupation', string='Occupation', track_visibility="onchange")
    occupation_other = fields.Char(string='Occupation Others', track_visibility="onchange")
    subject_of_interest = fields.Many2many('member.subject.interest', string='Subjects of Interest',
                                           track_visibility="onchange")
    subject_of_interest_others = fields.Char(string="Subject of Interest Others", track_visibility="onchange")
    last_place_of_study = fields.Char(string='Last or Current Place of Study', track_visibility="onchange")
    highest_certification = fields.Many2one('member.certification', string='Highest Certification Achieved',
                                            track_visibility="onchange")
    highest_certification_other = fields.Char(string='Highest Certification Achieved Others',
                                              track_visibility="onchange")
    place_of_study = fields.Char(string='Place of Study', track_visibility="onchange")
    field_of_study = fields.Char(string='Field of Study', track_visibility="onchange")
    usa_work_or_study = fields.Selection([('yes', 'Yes'), ('no', 'No')], default='no',
                                         string="Have you worked, or studied in the U.S?", track_visibility="onchange")
    alumni_institute = fields.Char(track_visibility="onchange",
                                   string='If you are an alumni of an American institution, which school did you attend?')
    usa_work_or_study_place = fields.Text(string="If yes, where in the U.S have you worked, or studied?",
                                          track_visibility="onchange")

    street = fields.Char(track_visibility="onchange")
    street2 = fields.Char(track_visibility="onchange")
    zip = fields.Char(track_visibility="onchange",change_default=True)
    city = fields.Char(track_visibility="onchange")
    state_id = fields.Many2one("res.country.state", track_visibility="onchange")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',track_visibility="onchange")
    phone = fields.Char(track_visibility="onchange")
    fax = fields.Char(track_visibility="onchange")
    mobile = fields.Char(track_visibility="onchange")
    current_employee = fields.Char(string='Current Employer', track_visibility="onchange")
    work_title = fields.Char(string='Work Title', track_visibility="onchange")
    work_phone = fields.Char(string='Work Phone', track_visibility="onchange")
    info_about_emk = fields.Text(string="How did you learn about the EMK Center?", track_visibility="onchange")

    @api.multi
    def update_profile(self):

        vals = {}
        if self.website:
            vals['website'] = self.website
        if self.occupation:
            vals['occupation'] = self.occupation.id
        if self.occupation_other:
            vals['occupation_other'] = self.occupation_other
        if self.subject_of_interest:
            vals['subject_of_interest'] = [(6, 0, self.subject_of_interest.ids)]
        if self.subject_of_interest_others:
            vals['subject_of_interest_others'] = self.subject_of_interest_others
        if self.last_place_of_study:
            vals['last_place_of_study'] = self.last_place_of_study
        if self.highest_certification:
            vals['highest_certification'] = self.highest_certification.id
        if self.highest_certification_other:
            vals['highest_certification_other'] = self.highest_certification_other
        if self.place_of_study:
            vals['place_of_study'] = self.place_of_study
        if self.field_of_study:
            vals['field_of_study'] = self.field_of_study
        if self.usa_work_or_study:
            vals['usa_work_or_study'] = self.usa_work_or_study
        if self.alumni_institute:
            vals['alumni_institute'] = self.alumni_institute
        if self.usa_work_or_study_place:
            vals['usa_work_or_study_place'] = self.usa_work_or_study_place
        if self.street:
            vals['street'] = self.street
        if self.street2:
            vals['street2'] = self.street2
        if self.zip:
            vals['zip'] = self.zip
        if self.city:
            vals['city'] = self.city
        if self.state_id:
            vals['state_id'] = self.state_id.id
        if self.country_id:
            vals['country_id'] = self.country_id.id
        if self.phone:
            vals['phone'] = self.phone
        if self.mobile:
            vals['mobile'] = self.mobile
        if self.current_employee:
            vals['current_employee'] = self.current_employee
        if self.work_title:
            vals['work_title'] = self.work_title
        if self.work_phone:
            vals['work_phone'] = self.work_phone
        if self.info_about_emk:
            vals['info_about_emk'] = self.info_about_emk

        member = self.env['res.partner'].browse(self._context['active_id'])

        if len(vals) > 0:
            member.sudo().write(vals)

            return {
                'view_type': 'form',
                'view_mode': 'form',
                'src_model': 'res.partner',
                'res_model': 'res.partner',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': member.id
            }
