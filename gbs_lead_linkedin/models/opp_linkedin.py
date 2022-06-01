# -*-coding:utf-8-*-
from odoo import models, fields


class Linkedin_Opp(models.Model):
    _inherit = 'crm.lead'
    linkedin = fields.Char('Linkedin')
    emp_size = fields.Char('Employee Size')
