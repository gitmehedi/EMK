from odoo import fields, models, api, _


class InheritedAccountJournal(models.Model):
    _inherit = 'account.journal'

    petty_cash_journal = fields.Boolean(default=False)

    @api.multi
    def cash_statements_action(self):
        action_name = self._context.get('action_name', False)
        if not action_name:
            if self.type == 'bank':
                action_name = 'action_view_bank_statement_tree_petty_cash'
            elif self.type == 'cash':
                action_name = 'action_view_bank_statement_tree_petty_cash'
            elif self.type == 'sale':
                action_name = 'action_invoice_tree1'
            elif self.type == 'purchase':
                action_name = 'action_invoice_tree2'
            else:
                action_name = 'action_move_journal_line'

        _journal_invoice_type_map = {
            ('sale', None): 'out_invoice',
            ('purchase', None): 'in_invoice',
            ('sale', 'refund'): 'out_refund',
            ('purchase', 'refund'): 'in_refund',
            ('bank', None): 'bank',
            ('cash', None): 'cash',
            ('general', None): 'general',
        }
        invoice_type = _journal_invoice_type_map[(self.type, self._context.get('invoice_type'))]

        ctx = self._context.copy()
        ctx.pop('group_by', None)
        ctx.update({
            'journal_type': self.type,
            'default_journal_id': self.id,
            'search_default_draft': 1,
        })

        [action] = self.env.ref('gbs_petty_cash.%s' % action_name).read()
        action['context'] = ctx
        # domain_ctx = self._context.get('use_domain', [])
        # domain_ctx.append({
        #     'journal_id': self.id
        # })
        action['domain'] = [('journal_id', '=', self.id)]
        if action_name in ['action_view_bank_statement_tree_petty_cash']:
            action['views'] = False
            action['view_id'] = False
        return action

    @api.multi
    def create_cash_statement_cash_in(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash',
                    'default_type_of_operation': 'cash_in'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }

    @api.multi
    def create_cash_statement_cash_out(self):
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id, 'default_journal_type': 'cash',
                    'default_type_of_operation': 'cash_out'})
        return {
            'name': _('Create cash statement'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement',
            'context': ctx,
        }