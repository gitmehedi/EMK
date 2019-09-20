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
    #     try:
    #         compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = dict()
    #     ctx.update({
    #         'default_model': 'hr.applicant',
    #         'default_res_id': self.ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True,
    #         'custom_layout': "gbs_hr_recruitment.template_appointment_letter"
    #     })
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }

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