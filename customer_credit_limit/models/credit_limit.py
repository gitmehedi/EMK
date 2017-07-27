from openerp import models, fields,_
from openerp import api
import time
from openerp.tools.translate import _

class customer_creditlimit_assign(models.Model):
    
    _name = 'customer.creditlimit.assign'
    
    _description = "Credit limit assign"

    name = fields.Char('Name', required=True, states={'approve': [('readonly', True)]})
    approve_date = fields.Datetime('Approve Date')
    credit_limit = fields.Float('Limit', states={'approve': [('readonly', True)]})
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('approve', 'Approve'),
            ],select=True, readonly=True,default='draft')

    @api.multi
    def approve_creditlimit_run(self, cr, uid, ids, context=None):
        limit_pool = self.pool.get('res.partner.credit.limit')
        partner_pool = self.pool.get('res.partner')
        for assign in self.browse(cr, uid, ids, context):
            for limit in assign.limit_ids:
                limit_pool.write(cr, uid, [limit.id], {'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')}, context)
                partner_pool.write(cr, uid, [limit.partner_id.id], {'credit_limit':limit.value}, context=context)
        return self.write(cr, uid, ids, {'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        for limit in self.browse(cr, uid, ids, context=context):
            if limit.state in ['approve']:
                raise models.except_models(_('Warning!'),_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink(cr, uid, ids, context)


class res_partner(models.Model):
    
    _inherit = 'res.partner'
    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', 'Limits')
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit')

    @api.multi
    def _current_limit(self, context=None):
        date = time.strftime('%Y-%m-%d')
        for partner in self:
            sql_query = """SELECT value FROM res_partner_credit_limit
                            WHERE partner_id = %s
                            AND assign_date <= %s
                            AND state = %s
                            ORDER BY assign_date desc, id desc LIMIT 1"""
            params = (partner.id, date, 'draft')
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()


            # self.env.cr.execute('SELECT value FROM res_partner_credit_limit '
            #                 'WHERE partner_id = %s '
            #                 'AND assign_date <= %s '
            #                 'AND state = %s '
            #                 'ORDER BY assign_date desc, id desc LIMIT 1',
            #                 (id, date, "draft"))

            if len(results)>0:
                partner.credit_limit = results[0]['value']
            else:
                partner.credit_limit = 0



class res_partner_credit_limit(models.Model):
    
    _name = 'res.partner.credit.limit'
    _order = "assign_date desc, id desc"

    partner_id = fields.Many2one('res.partner', "Customer", required=True)
    assign_date = fields.Date("Date")
    value = fields.Float('Limit')
    assign_id = fields.Many2one(comodel_name='customer.creditlimit.assign')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ],select=True, readonly=True, default='draft')

    
    # def unlink(self, context=None):
    #     for limit in self.browse(cr, uid, ids, context=context):
    #         if limit.state in ['approve']:
    #             raise models.except_models(_('Warning!'),_('You cannot delete a value which is not draft state!'))
    #     return super(res_partner_credit_limit, self).unlink(cr, uid, ids, context)
    
    _defaults = {
        'assign_date': lambda *a: time.strftime('%Y-%m-%d')
    }

