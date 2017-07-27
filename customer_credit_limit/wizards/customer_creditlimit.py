from openerp import models, fields, api
import time
from openerp.tools.translate import _

class creditlimit_partners(models.TransientModel):
    _name ='creditlimit.partners'
    _description = 'Generate creditlimit for all selected partners'

    partner_ids = fields.Many2many('res.partner', 'partner_limit_group_rel', 'limit_id', 'partner_id')
    
    def compute_sheet(self, cr, uid, ids, context=None):
        partner_pool = self.pool.get('res.partner')
        limit_pool = self.pool.get('res.partner.credit.limit')
        run_pool = self.pool.get('customer.creditlimit.assign')

        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['credit_limit'])
            print run_data
        limit_data = run_data.get('credit_limit', False)
        assign_id = run_data.get('id', False)
        assign_date =  time.strftime('%Y-%m-%d')        
        if not data['partner_ids']:
            raise models.except_osv(_("Warning!"), _("You must select customer(s) to generate limit(s)."))
        for partner in partner_pool.browse(cr, uid, data['partner_ids'], context=context):
            res = {
                'partner_id': partner.id,
                'assign_date': assign_date,
                'value': limit_data,
                'assign_id':assign_id,
                'state': 'draft',
            }
            
            limit_pool.create(cr, uid, res, context=context)
        
        return {'type': 'ir.actions.act_window_close'}

creditlimit_partners()

