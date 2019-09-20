from odoo import api, fields, models,_
from openerp.exceptions import Warning as UserError


class HRCandidateApproval(models.Model):
    _name = 'hr.candidate.approval'
    _inherit = ['mail.thread']
    _rec_name = 'approval_form_name'

    approval_form_name = fields.Char(string='Candidate Name',required=True)
    manpower_requisition_id = fields.Many2one('hr.employee.requisition', string='Manpower Requisition Reference',
                                              store=True,required=True,domain=[('state', '=', 'approved')])
    department_id = fields.Many2one('hr.department', string='Department',related='manpower_requisition_id.department_id',
                                    store=True,readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Title',related='manpower_requisition_id.job_id',
                             store=True,readonly=True)
    applicant_ids = fields.One2many('hr.candidate.details', 'candidate_approval_id')
    check_edit_access = fields.Boolean(string='Check', compute='_compute_check_user')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Confirmed'),
        ('cxo_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft',track_visibility='onchange')

    ####################################################
    # Business methods
    ####################################################

    @api.onchange('manpower_requisition_id')
    def onchange_manpower_requisition_id(self):
        if self.manpower_requisition_id:
            val = []
            manpower_requisition_obj = self.env['hr.employee.requisition'].search([('id', '=', self.manpower_requisition_id.id)])

            if manpower_requisition_obj:
                applicant_pool=self.env['hr.applicant'].search([('department_id','=',self.department_id.id),('job_id','=',self.job_id.id)])
                for record in applicant_pool:
                    val.append((0, 0, {'applicant_name': record.partner_name,
                                       'education_id': record.type_id.id,
                                       'proposed_designation': record.job_id.id,
                                       'expected_salary': record.salary_expected,
                                       'joining_date': record.availability,
                                       'applicant_id':record.id,
                                       'state':'draft',
                                       }))
            self.applicant_ids = val

    @api.multi
    def _compute_check_user(self):
        user = self.env.user.browse(self.env.uid)
        for i in self:
            if user.has_group('hr_recruitment.group_hr_recruitment_user') and i.state=='draft':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_general_manager') and i.state=='gm_approve':
                i.check_edit_access = True
            elif user.has_group('gbs_application_group.group_cxo') and i.state=='cxo_approve':
                i.check_edit_access = True
            else:
                i.check_edit_access = False

    @api.one
    @api.constrains('manpower_requisition_id','department_id','job_id')
    def _check_duplications(self):
        domain = [('manpower_requisition_id', '=', self.manpower_requisition_id.id),
                  ('department_id', '=', self.department_id.id),
                  ('job_id', '=', self.job_id.id),
                  ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError('You can\'t create duplicate Approval process')
        return True

    @api.multi
    def action_confirm(self):
        for applicant_details_id in self.applicant_ids:
            if applicant_details_id.is_selected==True:
                applicant_details_id.write({'state': 'gm_approve'})
                applicant_pool = self.env['hr.applicant'].search([('id', '=', applicant_details_id.applicant_id)], limit=1)
                applicant_pool.write({'state': 'gm_approve'})
                applicant_details_id.is_selected = False
        self.state = 'gm_approve'

    @api.multi
    def action_gm_approve(self):
        for applicant_details_id in self.applicant_ids:
            if applicant_details_id.is_selected==True:
                applicant_details_id.write({'state': 'cxo_approve'})
                applicant_pool = self.env['hr.applicant'].search([('id', '=', applicant_details_id.applicant_id)], limit=1)
                applicant_pool.write({'state': 'cxo_approve'})
                applicant_details_id.is_selected=False
        self.state = 'cxo_approve'

    @api.multi
    def action_cxo_approve(self):
        for applicant_details_id in self.applicant_ids:
            if applicant_details_id.is_selected==True:
                applicant_details_id.write({'state': 'approved'})
                applicant_pool = self.env['hr.applicant'].search([('id', '=', applicant_details_id.applicant_id)], limit=1)
                applicant_pool.write({'state': 'approved'})
                applicant_details_id.is_selected = False
        self.state = 'approved'

    @api.multi
    def action_decline(self):
        for applicant_obj in self.applicant_ids:
            applicant_obj.write({'state': 'declined'})
            applicant_pool = self.env['hr.applicant'].search([('id', '=', applicant_obj.applicant_id)],limit=1)
            applicant_pool.write({'state': 'declined'})
            applicant_obj.is_selected = False
        self.state = 'declined'

    @api.multi
    def action_reset(self):
        for applicant_obj in self.applicant_ids:
            applicant_obj.write({'state': 'draft'})
            applicant_pool = self.env['hr.applicant'].search([('id', '=', applicant_obj.applicant_id)],limit=1)
            applicant_pool.write({'state': 'draft'})
            applicant_obj.is_selected = False
        self.state = 'draft'

    ####################################################
    # ORM Overrides methods
    ####################################################

    @api.multi
    def unlink(self):
        for excep in self:
            if excep.state == 'approved':
                raise UserError(_('You can not delete in this state!!'))
            else:
                return super(HRCandidateApproval, self).unlink()


class HRCandidateDetails(models.Model):
    _name = 'hr.candidate.details'

    candidate_approval_id = fields.Many2one('hr.candidate.approval')
    applicant_name = fields.Char(string="Applicant's Name")
    applicant_id = fields.Integer(string='Applicant Application Id')
    address = fields.Text(string='Address')
    education_id = fields.Many2one('hr.recruitment.degree',string='Education')
    experience = fields.Float(string='Experience')
    proposed_designation = fields.Many2one('hr.job', string='Proposed Designation', required=True)
    expected_salary = fields.Float(string='Expected Salary')
    joining_date = fields.Date(string='Joining Date')
    remarks = fields.Text(string='Remarks')
    is_selected=fields.Boolean(string='Selected')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('gm_approve', 'Confirmed'),
        ('cxo_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft')

    @api.multi
    def generate_appointletter(self):
        data = {}

        data['applicant_id']=self.applicant_id

        return self.env['report'].get_action(self, 'gbs_hr_recruitment.report_app_letter', data=data)