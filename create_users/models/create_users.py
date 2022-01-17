# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_temporary = fields.Boolean(string="Temporary User", default=False)

    @api.model
    def create_temp_user(self, login, groups):
        res_id = self.env['res.users'].search([('email', '=', login)])
        res_id.write({'is_temporary': True})
        groups = self.env['res.groups'].search(
            [('name', '=', groups['grp_name']), ('category_id.name', '=', groups['cat_name'])])
        groups.write({'users': [(6, 0, [res_id.id])]})
        return res_id
