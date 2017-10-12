from odoo import api, fields, models,_
from openerp.exceptions import Warning as UserError


class HrApplicantInherit(models.Model):
    _inherit = ['hr.applicant']

    manager_id = fields.Many2one('hr.employee', string='Manager', related='department_id.manager_id',
                                 readonly=True, copy=False)
    gender = fields.Selection([('male', 'Male'),('female', 'Female'),('other','Other')],
                               string='Gender')
    marital_status = fields.Selection([('single', 'Single'),('married', 'Married'),('other','Other')],
                               string='Marital Status')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Confirmed'),
        ('cxo_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft',track_visibility='onchange')

    @api.multi
    def generate_appointment_letter(self):
        data = {}

        data['applicant_id'] = self.id
        return self.env['report'].get_action(self, 'gbs_hr_recruitment.report_app_letter', data=data)

    # @api.multi
    # def generate_appointment_letter(self):
    #
    #     self.ensure_one()
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data.get_object_reference('gbs_hr_recruitment', 'template_appointment_letter')[1]
    #     except ValueError:
    #         template_id = False
    #
    #     base_template = self.env.ref("gbs_hr_recruitment.template_appointment_letter", raise_if_not_found=False)
    #
    #     data = {
    #
    #     }
    #
    #     return self.env['report'].render('gbs_hr_recruitment.report_letter', data)


    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.multi
    def write(self, vals):
        if self.state == 'approved':
            raise UserError(_('You can not edit in this state!!'))
        else:
            return super(HrApplicantInherit, self).write(vals)

    @api.multi
    def unlink(self):
        for excep in self:
            if excep.state == 'approved':
                raise UserError(_('You can not delete in this state!!'))
            else:
                return super(HrApplicantInherit, self).unlink()