from openerp.osv import osv, fields
import time

class account_voucher(osv.osv):
    '''
    Account Voucher
    '''
    _inherit = 'account.voucher'    

    _columns = {
        'bank_id':fields.many2one("res.bank", 'Bank Name'),
        'branch_name':fields.char('Branch Name'),
        'cheque_no':fields.char('Cheque No'),
        'receipt_date':fields.date('Receive Date'),
    }
    
    _defaults = {
        'receipt_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
            
account_voucher()