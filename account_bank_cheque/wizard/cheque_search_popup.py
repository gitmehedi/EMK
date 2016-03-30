from openerp import models, fields, api, exceptions
import datetime

class ChequeSearchPopup(models.TransientModel):
    _name='account.postdated.cheque.search.popup'
    
    # Database field
    date_from = fields.Date(string="From Date", default=fields.Date.today(), required=True)
    date_to = fields.Date(string="To Date", default=fields.Date.today(), required=True)
    partner_info = fields.Many2one('res.partner', string='Name of Customer', help='Please enter customer name.')
    issuing_bank = fields.Many2one('account.postdated.bank', string='Name of Bank', help='Please enter bank name.')
    cheque_number = fields.Char(string='Cheque Number', size=50, help='Please enter cheque number.')
    deposit_date = fields.Date(string='Cheque Deposit Date', default=fields.Date.today(), help='Please enter cheque deposit date.')
    account_number_id = fields.Many2one('res.partner.bank', ondelete='set null', string='Company Account')
    
    @api.multi
    def action_deposit_cheque(self):
        active_ids = self.env.context.get('active_ids', []) or []
        proxy = self.env['account.postdated.cheque']
                
        for record in proxy.search([('id', 'in', active_ids)]):
            if record.state not in ('draft'):
                raise osv.except_osv(_('Warning!'), _("Selected Data cannot be accessible as they are not in 'Draft' state."))
            record.account_number_id = self.account_number_id
            record.deposit_date = self.deposit_date
            record.deposit_cheque();
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def search_cheque(self,val):
        date_from=self.date_from
        date_to=self.date_to
                
        domain = ['&',('posting_date', '>=', self.date_from),('posting_date', '<=', self.date_to)]
        
#         obj=self.env['account.postdated.cheque']
#         records=obj.search([('posting_date','>=',date_from),('posting_date','<=',date_to)])    
    
        if self.partner_info:
            domain += [('partner_info', '=', self.partner_info.id)]
            
        if self.issuing_bank:
            domain += [('issuing_bank', '=', self.issuing_bank.id)]       
        
        if self.cheque_number:
            domain += [('cheque_number', '=', self.cheque_number)]
               
        print "----------------------", domain
        return {
            'name': 'Cheque List',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.postdated.cheque',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            }
        