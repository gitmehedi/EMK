from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.amount_to_text_en import amount_to_text


def _amount_total_text(self, cursor, user, ids, name, arg, context=None):
    res = {}
    for order in self.browse(cursor, user, ids, context=context):
        a = ''
        b = ''
        if order.currency_id.name == 'THB':
            a = 'Baht'
            b = 'Satang'
        if order.currency_id.name == 'USD':
            a = 'Dollar'
            b = 'Cent'
        if order.currency_id.name == 'EUR':
            a = 'Euro'
            b = 'Cent'
        if order.currency_id.name == 'BDT':
            a = 'Taka'
            b = 'Paisa'
            
        res[order.id] = amount_to_text(order.amount, 'en', a).replace('Cents', b).replace('Cent', b)
        
    return res


class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    _columns = {
        'amount_text': fields.function(_amount_total_text, string='Amount Total (Text)', type='char'),
    }
    
account_voucher()