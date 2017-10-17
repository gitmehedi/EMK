from odoo import models, fields, api


class BMDInheritedHrJob(models.Model):
    _inherit = 'hr.job'

    job_publish_date = fields.Date(string='Published Date')
    authorize_district = fields.Many2many('job.district', 'job_id', 'job_district_id', 'trans_id')



class BMDJobDistrict(models.Model):
    _name = 'job.district'

    name = fields.Char(string='District Name')