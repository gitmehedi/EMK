from odoo import models, fields, api


class BMDInheritedHrJob(models.Model):
    _inherit = 'hr.job'

    job_publish_date = fields.Date(string='Published Date')
    job_publish_number = fields.Char(string='Published Number')
    required_education = fields.Many2one('hr.recruitment.degree',string = 'Educational Qualification')
    authorize_district = fields.Many2many('bd.district','job_district_rel', 'job_id', 'job_district_id')

