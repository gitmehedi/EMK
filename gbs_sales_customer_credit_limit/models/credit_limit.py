from odoo import api, fields, models,_
import time
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class customer_creditlimit_assign(models.Model):
    
    _name = 'customer.creditlimit.assign'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _description = "Credit limit assign"

    name = fields.Char('Name', required=True,
           states={'confirm': [('readonly', True)],'validate1': [('readonly', True)],'approve': [('readonly',True)]})
    approve_date = fields.Datetime('Approve Date',
                   states = {'draft': [('invisible', True)],'confirm': [('invisible', True)],'validate1': [('invisible', True)], 'approve': [('invisible',False),('readonly',True)]})
    credit_limit = fields.Float('Limit',required=True,
                   states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)], 'approve': [('readonly', True)]})

    """ Relational Fields """
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits',
                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)], 'approve': [('readonly', True)]})


    """ State fields for containing various states """
    state = fields.Selection([('draft', 'To Submit'),('cancel', 'Cancelled'),('confirm', 'To Approve'),('refuse', 'Refused'),
                              ('validate1', 'Second Approval'),('approve', 'Approved'),],default='draft')

    """ All functions """
    @api.multi
    def approve_creditlimit_run(self):
        self.limit_ids.write({'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')})
        return self.write({'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def unlink(self):
        for limit in self:
            if limit.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink()

    @api.multi
    def action_confirm(self):
        self.state = 'confirm'

    @api.multi
    def action_validate(self):
        self.state = 'validate1'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'



class res_partner(models.Model):
    
    _inherit = 'res.partner'
    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', 'Limits', domain=[('state','=','approve')])
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit')

    """ All functions """
    @api.multi
    def _current_limit(self, context=None):
        date = time.strftime('%Y-%m-%d')
        for partner in self:
            sql_query = """SELECT value FROM res_partner_credit_limit
                            WHERE partner_id = %s
                            AND assign_date <= %s
                            AND state = %s
                            ORDER BY assign_date desc, id desc LIMIT 1"""
            params = (partner.id, date, 'approve')
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()
            if len(results)>0:
                partner.credit_limit = results[0]['value']
            else:
                partner.credit_limit = 0



class res_partner_credit_limit(models.Model):
    
    _name = 'res.partner.credit.limit'
    _order = "assign_date desc, id desc"

    partner_id = fields.Many2one('res.partner', "Customer", required=True)
    assign_date = fields.Date("Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'))
    value = fields.Float('Limit')
    assign_id = fields.Many2one('customer.creditlimit.assign')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ],select=True, readonly=True, default='draft')
    # def unlink(self, context=None):
    #     for limit in self.browse(cr, uid, ids, context=context):
    #         if limit.state in ['approve']:
    #             raise models.except_models(_('Warning!'),_('You cannot delete a value which is not draft state!'))
    #     return super(res_partner_credit_limit, self).unlink(cr, uid, ids, context)
    
    # _defaults = {
    #     'assign_date': lambda *a: time.strftime('%Y-%m-%d')
    # }

