import ast

from odoo import api, fields, models, _


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.multi
    def get_needaction_data(self):
        res = dict()
        for menu in self:
            if menu.action and menu.action.context:
                new_context = dict()
                try:
                    new_context = ast.literal_eval(menu.action.context)
                    new_context.update(self.env.context)
                except:
                    new_context = self.env.context
            res.update(super(IrUiMenu, menu.with_context(new_context)).get_needaction_data())

        return res
