from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountAssetCategoryWizard(models.TransientModel):
    _name = 'account.asset.category.wizard'

    @api.model
    def default_name(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).name

    @api.model
    def default_status(self):
        context = self._context
        return self.env[context['active_model']].search([('id', '=', context['active_id'])]).active

    status = fields.Boolean(string='Active', default=default_status)
    name = fields.Char(string='Requested Name')

    @api.multi
    def act_change_name(self):
        id = self._context['active_id']
        obj = self.env['account.asset.category']
        asset = obj.browse(id)
        if asset.parent_id:
            name = obj.search([('name', '=ilike', self.name.strip()), ('parent_id', '!=', None),
                               '|', ('active', '=', True), ('active', '=', False)])
        elif not asset.parent_id:
            name = obj.search([('name', '=ilike', self.name.strip()), ('parent_id', '=', None),
                                '|', ('active', '=', True), ('active', '=', False)])

        if len(name) > 0:
            raise Warning('[Unique Error] Name must be unique!')

        pending = self.env['history.account.asset.category'].search([('state', '=', 'pending'), ('line_id', '=', id)])
        if len(pending) > 0:
            raise Warning('[Warning] You already have a pending request!')

        self.env['history.account.asset.category'].create(
            {'change_name': self.name, 'request_date': fields.Datetime.now(), 'line_id': id, 'status': self.status})
        record = self.env['account.asset.category'].search(
            [('id', '=', id), '|', ('active', '=', False), ('active', '=', True)])
        if record:
            record.write({'pending': True})
