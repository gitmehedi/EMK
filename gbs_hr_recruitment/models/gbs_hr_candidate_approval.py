from odoo import api, fields, models


class HRCandidateApproval(models.Model):
    _name = 'hr.candidate.approval'
    _inherit = ['mail.thread']
    _rec_name = 'approval_form_name'

    approval_form_name = fields.Char(string='Candidate Name',required=True)
    manpower_requisition_id = fields.Many2one('hr.employee.requisition', string='Manpower Requisition Reference', required=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    store=True, required='True')
    job_id = fields.Many2one('hr.job', string='Job Title',
                             store=True,required='True')
    applicant_ids = fields.One2many('hr.candidate.details', 'candidate_details_id')
    check_edit_access = fields.Boolean(string='Check', compute='_compute_check_user')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Confirmed'),
        ('cxo_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    @api.onchange('manpower_requisition_id')
    def onchange_manpower_requisition_id(self):
        if self.manpower_requisition_id:
            val = []
            manpower_requisition_obj = self.env['hr.employee.requisition'].search([('id', '=', self.manpower_requisition_id.id)])

            if manpower_requisition_obj:
                self.department_id = manpower_requisition_obj.department_id.id
                self.job_id = manpower_requisition_obj.job_id.id

                applicant_pool=self.env['hr.applicant'].search([('job_id','=',self.job_id.id)])
                for record in applicant_pool:
                    val.append((0, 0, {'applicant_name': record.partner_name,
                                       'education_id': record.type_id.id,
                                       'proposal_designation': record.job_id.id,
                                       'expected_salary': record.salary_expected,
                                       'joining_date': record.availability,
                                       }))
            self.applicant_ids = val

    @api.multi
    def _compute_check_user(self):
        user = self.env.user.browse(self.env.uid)
        for i in self:
            if user.has_group('hr_recruitment.group_hr_recruitment_manager') and i.state=='draft':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_general_manager') and i.state=='gm_approve':
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


class HRCandidateDetails(models.Model):
    _name = 'hr.candidate.details'

    candidate_details_id = fields.Many2one('hr.candidate.approval')
    applicant_name = fields.Char("Applicant's Name")
    address = fields.Text(string='Address')
    education_id = fields.Many2one('hr.recruitment.degree',string='Education')
    experience = fields.Float(string='Experience')
    proposed_designation = fields.Many2one('hr.job', string='Proposed Designation', required=True)
    expected_salary = fields.Float(string='Expected Salary')
    joining_date = fields.Date(string='Joining Date')
    remarks = fields.Text(string='Remarks')

