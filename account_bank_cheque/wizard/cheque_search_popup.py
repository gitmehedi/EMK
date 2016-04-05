from openerp import models, fields, api, exceptions
import datetime
from duplicity.tempdir import default
from docutils.nodes import Invisible

class ChequeSearchPopup(models.TransientModel):
    _name = 'account.postdated.cheque.search.popup'
    
    # Database field
    date_from = fields.Date(string="From Date", default=fields.Date.today(), required=True)
    date_to = fields.Date(string="To Date", default=fields.Date.today(), required=True)
    partner_info = fields.Many2one('res.partner', string='Name of Customer', help='Please enter customer name.')
    issuing_bank = fields.Many2one('account.postdated.bank', string='Name of Bank', help='Please enter bank name.')
    cheque_number = fields.Char(string='Cheque Number', size=50, help='Please enter cheque number.')
    deposit_date = fields.Date(string='Cheque Deposit Date', default=fields.Date.today(), help='Please enter cheque deposit date.')
    confirm_date = fields.Date(string='Cheque Confirm Date', default=fields.Date.today(), help='Please enter cheque confirm date.')
    reject_date = fields.Date(string='Cheque Reject Date', default=fields.Date.today(), help='Please enter cheque reject date.')
    account_number_id = fields.Many2one('res.partner.bank', ondelete='set null', string='Company Account')
    state = fields.Selection([
               ('select', 'Select'),
               ('draft', 'Draft'),
               ('deposit', 'Deposit'),
               ('confirm', 'Confirm'),
               ('reject', 'Reject'),
           ], default='select', string='Status', copy=False)
    
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
    def action_confirm_cheque(self):
        active_ids = self.env.context.get('active_ids', []) or []
        proxy = self.env['account.postdated.cheque']
        
        for record in proxy.search([('id', 'in', active_ids)]):
            if record.state not in ('deposit'):
                raise osv.except_osv(_('Warning!'), _("Selected Data cannot be accessible as they are not in 'Deposit' state."))
            record.confirm_date = self.confirm_date
            record.confirm_cheque();         
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def confirm_message(self):
        return {'value':{},'warning':{'title':'warning','message':'Your message here.'}}        
    
    @api.multi
    def action_reject_cheque(self):
        active_ids = self.env.context.get('active_ids', []) or []
        proxy = self.env['account.postdated.cheque']
        
        for record in proxy.search([('id', 'in', active_ids)]):
            if record.state not in ('deposit'):
                raise osv.except_osv(_('Warning!'), _("Selected Data cannot be accessible as they are not in 'Deposit' state."))
            record.reject_date = self.reject_date
            record.reject_cheque();
        return {'type': 'ir.actions.act_window_close'}
    
    @api.multi
    def action_search_cheque(self, val):
        date_from = self.date_from
        date_to = self.date_to
        
        domain = ['&', ('posting_date', '>=', self.date_from), ('posting_date', '<=', self.date_to)]
      
        if self.partner_info:
            domain += [('partner_info', '=', self.partner_info.id)]
            
        if self.issuing_bank:
            domain += [('issuing_bank', '=', self.issuing_bank.id)]       
        
        if self.cheque_number:
            domain += [('cheque_number', '=', self.cheque_number)]
            
        if self.state != 'select':
            domain += [('state', '=', self.state)]
                     
        return {
            'name': 'Cheque List',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.postdated.cheque',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': domain,
            'nodestroy': False,
            }
        
