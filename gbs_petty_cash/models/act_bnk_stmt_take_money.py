from odoo import fields, models, api


class InheritedAccountBankStatementTMO(models.Model):
    _inherit = 'account.bank.statement'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(InheritedAccountBankStatementTMO, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu)
        if toolbar:
            actions_in_toolbar = res['toolbar'].get('action')
            if actions_in_toolbar:
                temp_actions_in_toolbar = actions_in_toolbar
                for action in temp_actions_in_toolbar:
                    if action['xml_id'] == "account.action_cash_box_out":
                        res['toolbar']['action'].remove(action)
        return res
