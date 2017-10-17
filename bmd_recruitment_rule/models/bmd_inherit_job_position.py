from odoo import models, fields, api


class BMDInheritedHrJob(models.Model):
    _inherit = 'hr.job'

    job_publish_date = fields.Date(string='Published Date')
    required_education = fields.Many2one('hr.recruitment.degree',string = 'Educational Qualification')
    authorize_district = fields.Many2many('job.district', 'job_id', 'job_district_id', 'trans_id')