# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class CreateUser(models.TransientModel):
    _name = 'partner.user'
    _description = 'Create login from partner'

    @api.model
    def default_get(self, fields):
        res = super(CreateUser, self).default_get(fields)
        vals = []
        for aid in self._context.get('active_ids'):
            partner_id = self.env['res.partner'].browse(aid)
            vals.append((0, 0, {'partner_id': partner_id.id, 'login': partner_id.email}))
        res['user_data'] = vals
        return res

    user_data = fields.One2many('user.datas', 'rel_id')

    # if 'application' in self.state:
    #     vals = {
    #         'template': 'member_signup.member_application_rejection_email_template',
    #         'email_to': self.email,
    #         'context': {'name': self.name},
    #     }
    #     self.mailsend(vals)
    #     self.state = 'reject'
    #     if self.user_ids.active:
    #         self.user_ids.active = False

    @api.model
    def create_temp_user(self, login, groups):
        res_id = self.env['res.users'].search([('email', '=', login)])
        res_id.write({'is_temporary': True})
        group_ids = self.env['res.groups'].search(
            [('name', '=', groups['grp_name']), ('category_id.name', '=', groups['cat_name'])])
        group_ids.write({'users': [(6, 0, [res_id.id])]})
        return res_id

    @api.multi
    def create_login(self):
        for data in self:
            vals = {}
            for da in data.user_data:
                vals = {
                    'partner_id': da.partner_id.id,
                    'login': da.login,
                    'groups_id': da.groups_id,
                    'active': True,
                }
                self.env['res.users'].create(vals)


class CreateUserData(models.TransientModel):
    _name = 'user.datas'

    rel_id = fields.Many2one('partner.user')
    partner_id = fields.Many2one('res.partner', string='Partner')
    login = fields.Char('Login')
    groups_id = fields.Many2many('res.groups', column1='user_datas_id', column2="group_id", string='Groups')


