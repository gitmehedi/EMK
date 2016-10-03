# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
 
class AccountVoucherExtend(models.Model):
    
    _inherit = 'account.voucher'
    
    cheque_date = fields.Date(string='Cheque Date', default=fields.Date.today(), help='Please enter cheque date.')        
    cheque_number = fields.Char(string='Cheque Number', size=50,  help='Please enter cheque number.')
    issuing_bank = fields.Many2one('res.bank', ondelete='set null', string='Name of Bank', help='Please enter bank name.') 
    bank_branch_name = fields.Char(string='Branch Name', size=100, help='Please enter branch name.')
    
    def _is_select_cheque_journal(self):
        if self.journal_id.id==self.env.ref('account_check_deposit.check_received_journal').id:
            self.is_select_cheque=True
        else:
            self.is_select_cheque=False
    
    is_select_cheque = fields.Boolean(compute='_is_select_cheque_journal', store=False,string='Flag')
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        if ttype in ('sale', 'receipt'):
            account_id = journal.default_debit_account_id
        elif ttype in ('purchase', 'payment'):
            account_id = journal.default_credit_account_id
        else:
            account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id

        period_ids = self.pool['account.period'].find(cr, uid, dt=date, context=dict(context, company_id=company_id))
        is_select_cheque=False
        
        check_journal_internal_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_check_deposit', 'check_received_journal')[1]
        if journal.id==check_journal_internal_id:
            is_select_cheque=True
        else:
            is_select_cheque=False
        
        vals['value'].update({
            'currency_id': currency_id,
            'payment_rate_currency_id': currency_id,
            'period_id': period_ids and period_ids[0] or False,
            'is_select_cheque':is_select_cheque
        })
        
        
        
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context)
            for key in res.keys():
                vals[key].update(res[key])
        
        return vals