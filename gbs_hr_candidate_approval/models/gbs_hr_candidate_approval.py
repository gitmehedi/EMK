from openerp import api, fields, models
from datetime import date


class HRCandidateApproval(models.Model):
    _name='hr.candidate.approval'
    _inherit = ['mail.thread']
    _rec_name = 'candidate_name'

    candidate_name = fields.Char(string='Candidate Name',required=True)
    address = fields.Text(string='Address',required=True)
    education = fields.Char(string='Education',required=True)
    experience = fields.Float(string='Experience',required=True)
    department = fields.Many2one('hr.department', string='Department',required=True)
    proposal_designation = fields.Many2one('hr.job', string='Proposal Designation',required=True)
    expected_salary = fields.Float(string='Expected Salary',required=True)
    joining_date = fields.Date(string='Joining Date', required=True)
    remarks=fields.Text(string='Remarks')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Verify'),
        ('cxo_approve', 'CXO Verify'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    check_edit_access=fields.Boolean(string='Check',compute='_compute_check_user' )

    @api.multi
    def _compute_check_user(self):
        user = self.env.user.browse(self.env.uid)
        for i in self:
            if user.has_group('hr_recruitment.group_hr_recruitment_manager') and i.state=='gm_approve':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_cxo') and i.state=='cxo_approve':
                i.check_edit_access = True
            else:
                i.check_edit_access = False

    @api.multi
    def action_confirm(self):
        self.state = 'gm_approve'

    @api.multi
    def action_gm_approve(self):
        self.state = 'cxo_approve'

    @api.multi
    def action_cxo_approve(self):
        self.state = 'approved'

    @api.multi
    def action_decline(self):
        self.state = 'declined'

    @api.multi
    def action_reset(self):
        self.state = 'draft'