# -*- coding: utf-8 -*-
from openerp import api, fields, models
import logging
_logger = logging.getLogger(__name__)
import base64

class SurveyUserInputLead(models.Model):

    _inherit = "survey.user_input"
    
    lead_id = fields.Many2one('crm.lead', string="Lead")