from odoo import api, models
from odoo.exceptions import ValidationError

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

        acc = acc_pool.suspend_security().create(vals)
        return acc

    @api.model
    def create(self, vals):
        if 'parent_id' in vals and not vals['parent_id']:
            name = vals['name'].strip()
            if vals['customer']:
                partners = self._check_res_partner_duplicate(name, "customer")
                if len(partners) > 0:
                    raise ValidationError("Customer name already in use")

                receivable_id = self._get_max_code_for_account_receivable(vals['company_id'], vals['name'])
                vals['property_account_receivable_id'] = receivable_id

            elif vals['supplier'] and not vals['supplier_type'] == 'foreign':
                partners = self._check_res_partner_duplicate(name, "supplier")
                if len(partners) > 0:
                    raise ValidationError("Supplier name already in use")

                if 'supplier_type' in vals:
                    if not vals['supplier_type'] == 'foreign':
                        payable_id = self._get_max_code_for_account_payable(vals['company_id'], vals['name'])
                        vals['property_account_payable_id'] = payable_id
                else:
                    payable_id = self._get_max_code_for_account_payable(vals['company_id'], vals['name'])
                    vals['property_account_payable_id'] = payable_id

            elif vals['supplier'] and vals['supplier_type'] == 'foreign':
                partners = self._check_res_partner_duplicate(name, "supplier")
                if len(partners) > 0:
                    raise ValidationError("Supplier name already in use")

            elif vals['is_cnf']:
                partners = self._check_res_partner_duplicate(name, "is_cnf")
                if len(partners) > 0:
                    raise ValidationError("CNF Agent name already in use")

                payable_id = self._get_max_code_for_account_payable(vals['company_id'], vals['name'])
                vals['property_account_payable_id'] = payable_id
            else:
                pass

            if 'child_ids' in vals:
                child_ids = vals['child_ids']
                vals['child_ids'] = []
                for index, child in enumerate(child_ids):
                    if child[2]:
                        child[2]['customer'] = False
                        child[2]['supplier'] = False
                        vals['child_ids'].append(child)
            vals['name'] = name
        return super(InheritResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'name' in vals:
            name = vals['name'].strip()
            if self.customer:
                partners = self._check_res_partner_duplicate(name, "supplier")
                if len(partners) > 0:
                    raise ValidationError("Customer name already in use")
            elif self.supplier:
                partners = self._check_res_partner_duplicate(name, "supplier")
                if len(partners) > 0:
                    raise ValidationError("Supplier name already in use")
            elif self.is_cnf:
                partners = self._check_res_partner_duplicate(name, "is_cnf")
                if len(partners) > 0:
                    raise ValidationError("CNF Agent name already in use")
            vals['name'] = name

        if 'child_ids' in vals:
            child_ids = vals['child_ids']
            vals['child_ids'] = []
            for index, child in enumerate(child_ids):
                if child[2]:
                    child[2]['customer'] = False
                    child[2]['supplier'] = False
                    vals['child_ids'].append(child)
        return super(InheritResPartner, self).write(vals)
    
    def _check_res_partner_duplicate(self, name, key):
        sql = """SELECT * FROM res_partner WHERE name ='%s' and %s=True""" % (name.strip(), key)
        self._cr.execute(sql)
        return self._cr.fetchall()


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
                    res = account_account_id.suspend_security().unlink() if account_account_id.id else False

            else:
                res = super(InheritResPartner, rec).unlink()
