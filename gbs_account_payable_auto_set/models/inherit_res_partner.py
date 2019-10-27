from odoo import api, models


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

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

        acc = acc_pool.create(vals)
        return acc
