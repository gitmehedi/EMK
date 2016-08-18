from openerp import api, fields, models, _
from datetime import timedelta
import datetime
import time

class iou_slip(models.Model):
    
    _name = 'iou.slip'    

    
    #@api.model
    #def _default_warehouse_id(self):
   #     branch = self.env.user.branch_id.id
     #   branch_ids = self.pool['res.branch'].search([('name', '=', branch)], limit=1)
     #   return branch_ids
    
    name = fields.Char(string='IOU Slip No', size=64, required=True,
            readonly=True, select=True)
    branch_id = fields.Many2one("res.branch", string='Branch', required=True)
    #branch_id = fields.Many2one('res.branch', string='Branch',
    #    required=True, readonly=True,
    #    default=_default_warehouse_id)
       
    request_date = fields.Datetime(string='Request Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now)
    #request_date = fields.Datetime(string='Request Date')
    request_by = fields.Many2one("hr.employee", string='Request By')
    adjust_date = fields.Datetime(string='Adjust Date')
    purpose = fields.Char(string="Purpose")
    amount = fields.Float(string="Amount")
    approved_by = fields.Many2one("res.users", string='Approved By', readonly=True)
    approved_date = fields.Datetime(string='Approved Date', readonly=True)
    disbursed_by = fields.Many2one("res.users", string='Disbursed By', readonly=True)
    disbursed_date = fields.Datetime(string='Disbursed Date', readonly=True)
    received_by = fields.Many2one("res.users", string='Received By')
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approved', 'Approved'),
            ('disbursed', 'Disbursed'),
            ], 'Status', select=True, readonly=True , default='draft')
    
    
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
        #'branch_id':_get_default_branch,
    }
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'IOU Slip No must be unique per Company!'),
    ]
    _order = 'name desc'
    
    # Create auto sequence number
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'iou.slip') or '/'
        return super(iou_slip, self).create(cr, uid, vals, context=context)
    
    def action_disbursed(self, cr, uid, ids, context=None):
        vals = {
            'state':'disbursed',
            'disbursed_by': uid,
            'disbursed_date':time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.write(cr, uid, ids, vals)
    
    #Create IOU Adjustment 
    def create_adjustment(self, cr, uid, ids, context=None):
        adjustment_obj = self.pool.get('iou.adjustment')

        adjustment_values = {
                    'slip_id': ids[0],
        }

        adjustment_id = adjustment_obj.create(cr, uid, adjustment_values, context=context)
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'iou.adjustment',
            'res_id': adjustment_id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
    
    def action_approved(self, cr, uid, ids, context=None):
        vals = {
            'state':'approved',
            'approved_by': uid,
            'approved_date':time.strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.write(cr, uid, ids, vals)