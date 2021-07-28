# -*- coding: utf-8 -*-
from openerp import api, fields, models
import logging
_logger = logging.getLogger(__name__)
import base64

class SurveyQuestionConditional(models.Model):

    _inherit = "survey.question"
    
    conditional = fields.Boolean(string="Conditional")
    conditional_question_id = fields.Many2one('survey.question', string="Condition Question", help="The question which determines if this question is shown")
    conditional_option_id = fields.Many2one('survey.label', string="Condition Option", help="The option which determines if this question is shown")
    type = fields.Selection( selection_add=[('binary', 'File Select')] )
    
    @api.model
    def validate_binary(self, question, post, answer_tag):
        errors = {}
        
        #answer = base64.encodestring(post[answer_tag].read() )

        # Empty answer to mandatory question
        if question.constr_mandatory and not answer:
            errors.update({answer_tag: question.constr_error_msg})
        return errors
