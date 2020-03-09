from odoo import api, models


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_max_code_for_account_receivable(self, company_id, name):
        acc_pool = self.env['account.account'].search(
            [('company_id', '=', company_id), ('user_type_id.type', '=', 'receivable')])

        code_list = []
        for acc_code in acc_pool:
            code_list.append(acc_code.code)

        new_coa_obj = self._create_receivable_account(max(code_list), company_id, name, acc_pool[0].user_type_id.id,
                                                      acc_pool[0].parent_id.id)
        return new_coa_obj.id

    @api.multi
    def _create_receivable_account(self, max_code, company_id, name, type_id, parent_id):
        acc_pool = self.env['account.account']

        vals = {
            'code': str(int(max_code) + 1),
            'name': name + '-AR',
            'user_type_id': type_id,
            'company_id': company_id,
            'reconcile': True,
            'parent_id': parent_id
        }

        acc = acc_pool.create(vals)
        return acc

    @api.model
    def create(self, vals):
        if 'parent_id' in vals and not vals['parent_id']:
            if vals['customer']:
                receivable_id = self._get_max_code_for_account_receivable(vals['company_id'], vals['name'])
                vals['property_account_receivable_id'] = receivable_id

            elif vals['supplier']:
                payable_id = self._get_max_code_for_account_payable(vals['company_id'], vals['name'])
                vals['property_account_payable_id'] = payable_id

            elif vals['is_cnf']:
                payable_id = self._get_max_code_for_account_payable(vals['company_id'], vals['name'])
                vals['property_account_payable_id'] = payable_id

            else:
                pass

        return super(InheritResPartner, self).create(vals)

    # @api.multi
    # def unlink(self):
    #     for ptr in self:
    #         if ptr.customer is True:
    #             receivable_id = ptr.property_account_receivable_id
    #
    #             if receivable_id:
    #                 res = super(InheritResPartner, self).unlink()
    #                 if res:
    #                     receivable_id.unlink()
    #
    #                 return res

    @api.multi
    def unlink(self):
        for rec in self:
            if not rec.parent_id.id:
                # get account id
                if rec.customer:
                    account_account_id = rec.property_account_receivable_id
                elif rec.supplier:
                    account_account_id = rec.property_account_payable_id
                else:
                    # if cnf agent
                    account_account_id = rec.property_account_payable_id

                if super(InheritResPartner, rec).unlink():
                    res = account_account_id.unlink() if account_account_id.id else False

            else:
                res = super(InheritResPartner, rec).unlink()
