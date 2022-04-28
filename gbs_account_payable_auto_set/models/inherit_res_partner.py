from odoo import api, models
from odoo.exceptions import UserError, ValidationError, Warning


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('supplier_type')
    def _onchange_supplier_type(self):
        if self.supplier_type:
            if self.supplier and self.supplier_type == 'foreign':
                foreign_ap_account = self.env['ir.values'].get_default('account.config.settings', 'foreign_ap_account')
                if not foreign_ap_account:
                    raise UserError(
                        ("Foreign Account Payable Account not set. Please contact your system administrator for "
                         "assistance."))
                self.property_account_payable_id = foreign_ap_account

    @api.multi
    def _get_max_code_for_account_payable(self, company_id, name):
        acc_pool = self.env['account.account'].search(
            [('company_id', '=', company_id), ('user_type_id.type', '=', 'payable')])

        code_list = []
        for acc_code in acc_pool:
            code_list.append(acc_code.code)

        new_coa_obj = self._create_payable_account(max(code_list), company_id, name, acc_pool[0].user_type_id.id,
                                                   acc_pool[0].parent_id.id)
        return new_coa_obj.id

    @api.multi
    def _create_payable_account(self, max_code, company_id, name, type_id, parent_id):
        acc_pool = self.env['account.account']

        vals = {
            'code': str(int(max_code) + 1),
            'name': name + '-AP',
            'user_type_id': type_id,
            'company_id': company_id,
            'reconcile': True,
            'parent_id': parent_id,
        }

        acc = acc_pool.suspend_security().create(vals)
        return acc
