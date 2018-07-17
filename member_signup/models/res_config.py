# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    member_signup_reset_password = fields.Boolean(string='Enable password reset from Login page', help="This allows users to trigger a password reset from the Login page.")
    member_signup_uninvited = fields.Boolean(string='Allow external users to sign up', help="If unchecked, only invited users may sign up.")
    member_signup_template_user_id = fields.Many2one('res.users', string='Template user for new users created through signup')

    @api.model
    def get_default_member_signup_template_user_id(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        # we use safe_eval on the result, since the value of the parameter is a nonempty string
        return {
            'member_signup_reset_password': safe_eval(IrConfigParam.get_param('member_signup.reset_password', 'False')),
            'member_signup_uninvited': safe_eval(IrConfigParam.get_param('member_signup.allow_uninvited', 'False')),
            'member_signup_template_user_id': safe_eval(IrConfigParam.get_param('member_signup.template_user_id', 'False')),
        }

    @api.multi
    def set_member_signup_template_user_id(self):
        self.ensure_one()
        IrConfigParam = self.env['ir.config_parameter']
        # we store the repr of the values, since the value of the parameter is a required string
        IrConfigParam.set_param('member_signup.reset_password', repr(self.member_signup_reset_password))
        IrConfigParam.set_param('member_signup.allow_uninvited', repr(self.member_signup_uninvited))
        IrConfigParam.set_param('member_signup.template_user_id', repr(self.member_signup_template_user_id.id))
