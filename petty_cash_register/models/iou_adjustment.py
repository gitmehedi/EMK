from openerp import models, fields, api, _
import time

class iou_adjustment(models.Model):
    
    _name = 'iou.adjustment' 
    
    name = fields.Char(string='Name')
    slip_id = fields.Many2one("iou.slip", string='Slip', required=True)
    adjustment_date = fields.Datetime(string="Adjustment Date")
    amount = fields.Float(string='Amount')
    
    state = fields.Selection([
            ('draft', 'Draft'),
            ('adjusted', 'Adjusted'),
            ], 'Status', readonly=True, copy=False, default='draft')
    
    
    
         
    def action_adjusted(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'adjusted'})
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'IOU Adjustment No must be unique per Company!'),
    ]
    _order = 'name desc'
    
    # Create auto sequence number
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'iou.adjustment') or '/'
        return super(iou_adjustment, self).create(cr, uid, vals, context=context)