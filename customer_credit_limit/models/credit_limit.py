from odoo import api, fields, models, _
import time
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class customer_creditlimit_assign(models.Model):
    _name = 'customer.creditlimit.assign'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Credit limit assign"

    name = fields.Char(string='Name', index=True, readonly=True)
    sequence_id = fields.Char('Sequence', readonly=True)
    approve_date = fields.Date('Approved Date',
                               states={'draft': [('invisible', True)], 'confirm': [('invisible', True)],
                                       'validate1': [('invisible', True)],
                                       'approve': [('invisible', False), ('readonly', True)]})
    credit_limit = fields.Float('Credit Limit',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'approve': [('readonly', True)]})
    days = fields.Integer('Credit Days',
                          states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                  'approve': [('readonly', True)]})
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user,
                                   readonly=True)
    approver1_id = fields.Many2one('res.users', string='First Approval', readonly=True)
    approver2_id = fields.Many2one('res.users', string='Second Approval', readonly=True)

    """ Relational Fields """
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'approve': [('readonly', True)]})

    """ State fields for containing various states """
    state = fields.Selection(
        [('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
         ('validate1', 'Second Approval'), ('approve', 'Approved'), ], default='draft')

    """ All functions """

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('customer.creditlimit.assign') or '/'
        vals['name'] = seq
        return super(customer_creditlimit_assign, self).create(vals)

    @api.multi
    def approve_creditlimit_run(self):
        self.limit_ids.write({'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')})
        self.approver2_id = self.env.user
        return self.write({'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def unlink(self):
        for limit in self:
            if limit.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink()

    @api.constrains('credit_limit', 'days')
    def _check_value(self):
        if self.credit_limit <= 0 or self.days <= 0:
            raise Warning("[Error] Limit or Days never take zero or negative value!")

    # @api.constrains('name')
    # def _check_unique_constraint(self):
    #     if self.name:
    #         filters = [['name', '=ilike', self.name]]
    #         name = self.search(filters)
    #         if len(name) > 1:
    #             raise Warning('[Unique Error] Name must be unique!')

    @api.multi
    def action_confirm(self):
        val_id = []
        for line in self.limit_ids:
            if val_id != []:
                if line.partner_id.id in val_id:
                    raise ValidationError('Same Customer can not be added')
            val_id.append(line.partner_id.id)

        for limit in self:
            limit.state = 'confirm'
            # limit.name = self.env['ir.sequence'].get('sequence_id')

    @api.multi
    def action_validate(self):
        for record in self:
            record.approver1_id = self.env.user
            record.state = 'validate1'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', 'Limits', domain=[('state', '=', 'approve')])
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit',)
    remaining_credit_limit = fields.Float(string='Remaining Credit Limit')

    """ All functions """

    @api.constrains('name')
    def _check_unique_name(self):
        name = self.env['res.partner'].search([('name', '=', self.name)])
        if len(name) > 1:
            raise ValidationError('Customer already exists.')

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
            if len(results) > 0:
                partner.credit_limit = results[0]['value']
            else:
                partner.credit_limit = 0


class res_partner_credit_limit(models.Model):
    _name = 'res.partner.credit.limit'
    _order = "partner_id asc"

    partner_id = fields.Many2one('res.partner', "Customer", required=True)
    assign_date = fields.Date("Credit Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'))
    value = fields.Float('Credit Limit')
    day_num = fields.Integer('Credit Days')
    assign_id = fields.Many2one('customer.creditlimit.assign')

    # sl_num = fields.Integer(string="SL")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ], select=True, readonly=True, default='draft')

    # def unlink(self, context=None):
    #     for limit in self.browse(cr, uid, ids, context=context):
    #         if limit.state in ['approve']:
    #             raise models.except_models(_('Warning!'),_('You cannot delete a value which is not draft state!'))
    #     return super(res_partner_credit_limit, self).unlink(cr, uid, ids, context)

    # _defaults = {
    #     'assign_date': lambda *a: time.strftime('%Y-%m-%d')
    # }

    # @api.constrains('value')
    # def check_credit_limit(self):
    #     if self.value <= 0.00:
    #         raise ValidationError('Limit can not be zero or negative')

    # @api.constrains('assign_id','partner_id')
    # def check_partner_id(self):
    #     val_id=[]
    #     for i in self.assign_id.limit_ids:
    #         val_id.append(i.assign_id)
    #     for i in self.count:
    #         if val_id.count(i.assign_id)>1:
    #             raise ValidationError('Same Customer')


    @api.constrains('day_num')
    def check_credit_days(self):
        if self.day_num <= 0.00:
            raise ValidationError('Days can not be zero or negative')
