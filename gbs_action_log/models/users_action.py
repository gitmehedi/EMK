from odoo import models, fields, api, _


class UsersAction(models.Model):
    _name = 'users.action'

    name = fields.Char(string='Action Name')
    model = fields.Char(string='Model Name')
    code = fields.Integer(string='Action Code')
