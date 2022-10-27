from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_user_id = fields.Integer()

    @api.multi
    def create_login(self):
        for data in self:
            groups = self.env['res.groups'].sudo().search([('name', '=', 'Employee'), ('category_id.name', '=', 'Employees')])
            vals = {
                'partner_id': data.id,
                'login': data.email,
                'email': data.email,
                'groups_id': groups,
                'active': True,
            }
            users = self.env['res.users'].sudo().create(vals)
            if users:
                data.sudo().write({'partner_user_id': users.id})


