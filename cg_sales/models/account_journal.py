from openerp.osv import osv, fields


class account_journal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'code': fields.char('Code', size=30, required=True, help="The code will be displayed on reports."),
    }
    
account_journal()    