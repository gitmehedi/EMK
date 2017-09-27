from odoo import api, fields, models,_
from openerp.exceptions import Warning as UserError


class HrApplicantInherit(models.Model):
    _inherit = ['hr.applicant']

    manager_id = fields.Many2one('hr.employee', string='Manager', related='department_id.manager_id',
                                 readonly=True, copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Confirmed'),
        ('cxo_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    @api.multi
    def generate_appointment_letter(self):
        data = {}

        data['applicant_id'] = self.id
        return self.env['report'].get_action(self, 'gbs_hr_recruitment.report_app_letter', data=data)

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