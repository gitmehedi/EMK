from odoo import models, fields, api


class BMDInheritedHrJob(models.Model):
    _inherit = 'hr.job'

    job_publish_date = fields.Date(string='Published Date')