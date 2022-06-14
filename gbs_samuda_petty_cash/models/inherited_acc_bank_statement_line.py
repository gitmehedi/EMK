from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class InheritAccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    @api.multi
    def process_reconciliations(self, data):
        if data:
            for rec in data:
                if 'new_aml_dicts' in rec:
                    for aml in rec['new_aml_dicts']:
                        if 'account_id' in aml:
                            account_id = self.env['account.account'].browse(aml['account_id'])
                            if not 'department_id' in aml and account_id.user_type_id.department_required:
                                raise UserError('Department is required for account : ' + (
                                            str(account_id.code) + " " + str(account_id.name)))
                            if not 'operating_unit_id' in aml and account_id.user_type_id.operating_unit_required:
                                raise UserError('Operating Unit is required for account : ' + (
                                            str(account_id.code) + " " + str(account_id.name)))
                            if not 'cost_center_id' in aml and account_id.user_type_id.cost_center_required:
                                raise UserError('Cost Center is required for account : ' + (
                                            str(account_id.code) + " " + str(account_id.name)))
                            if not 'partner_id' in aml and account_id.user_type_id.partner_required:
                                raise UserError('Partner is required for account : ' + (
                                            str(account_id.code) + " " + str(account_id.name)))
                            if not 'analytic_account_id' in aml and account_id.user_type_id.analytic_account_required:
                                raise UserError('Analytic Account is required for account : ' + (
                                            str(account_id.code) + " " + str(account_id.name)))
                        else:
                            raise UserError('You need to select an account to reconcile.')

        super(InheritAccountBankStatementLine, self).process_reconciliations(data)
