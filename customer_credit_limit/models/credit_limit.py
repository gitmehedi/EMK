from odoo import api, fields, models, _
import time
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class customer_creditlimit_assign(models.Model):
    _name = 'customer.creditlimit.assign'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Credit Limit"
    _order = 'id DESC'

    name = fields.Char(string='Name', index=True, readonly=True)
    sequence_id = fields.Char('Sequence', readonly=True)
    approve_date = fields.Date('Approved Date',
                               states={'draft': [('invisible', True)], 'confirm': [('invisible', True)],
                                       'validate1': [('invisible', True)],
                                       'approve': [('invisible', False), ('readonly', True)]})
    credit_limit = fields.Float('Credit Limit',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'approve': [('readonly', True)]}, track_visibility='onchange')
    days = fields.Integer('Credit Days',
                          states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                  'approve': [('readonly', True)]})
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user,
                                   readonly=True)
    approver1_id = fields.Many2one('res.users', string='First Approval', track_visibility='onchange', readonly=True)
    approver2_id = fields.Many2one('res.users', string='Second Approval', track_visibility='onchange', readonly=True)

    """ Relational Fields """
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'approve': [('readonly', True)]})

    """ State fields for containing various states """
    state = fields.Selection(
        [('draft', 'To Submit'),
         ('confirm', 'To Approve'),
         ('validate', 'Validate'),
         ('validate1', 'Accounts Approval'),
         ('approve', 'Approved'),

         ('refuse', 'Refused'),
         ('cancel', 'Cancelled'), ],
        default='draft', track_visibility='onchange')

    """ All functions """

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('customer.creditlimit.assign') or '/'
        vals['name'] = seq
        return super(customer_creditlimit_assign, self).create(vals)

    @api.multi
    def approve_creditlimit_run(self):

        self.limit_ids.write(
            {'credit_limit': self.credit_limit, 'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')})
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
            raise Warning("Limit or Days never take zero or negative value!")

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

    @api.multi
    def action_validate_sales_head(self):
        self.state = 'validate'

    @api.multi
    def action_validate(self):
        for record in self:
            record.approver1_id = self.env.user
            record.state = 'validate1'

    @api.multi
    def action_refuse(self):
        self.state = 'refuse'

    ### Showing batch
    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['confirm'])]


        ## mail notification
        # @api.multi
        # def _notify_approvers(self):
        #     approvers = self.employee_id._get_employee_manager()
        #     if not approvers:
        #         return True
        #     for approver in approvers:
        #         self.sudo(SUPERUSER_ID).add_follower(approver.id)
        #         if approver.sudo(SUPERUSER_ID).user_id:
        #             self.sudo(SUPERUSER_ID)._message_auto_subscribe_notify(
        #                 [approver.sudo(SUPERUSER_ID).user_id.partner_id.id])
        #     return True


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # credit = fields.Monetary(compute='_credit_debit_get',
    #                          string='Total Receivable', help="Total amount this customer owes you.", store=True)

    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', 'Limits', domain=[('state', '=', 'approve')])
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit', )
    remaining_credit_limit = fields.Float(compute='_current_limit', string='Remaining Credit Limit')

    """ All functions """

    # @api.multi
    # def _credit_debit_get(self):
    #     res = super(ResPartner, self)._credit_debit_get()
    #     return res

    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name)])
            if len(name) > 1:
                raise ValidationError('Customer already exists.')

    @api.multi
    def _current_limit(self, context=None):
        date = time.strftime('%Y-%m-%d')

        for partner in self:
            sql_query = """SELECT * FROM res_partner_credit_limit
                            WHERE partner_id = %s
                            AND assign_date <= %s
                            AND state = %s
                            ORDER BY assign_date desc, id desc LIMIT 1"""

            params = (partner.id, date, 'approve')
            self.env.cr.execute(sql_query, params)
            results = self.env.cr.dictfetchall()

            if len(results) > 0:
                partner.credit_limit = results[0]['value']
                # partner.remaining_credit_limit = results[0]['remaining_credit_limit']
            else:
                partner.credit_limit = 0
                # partner.remaining_credit_limit = 0


class res_partner_credit_limit(models.Model):
    _name = 'res.partner.credit.limit'
    _order = "id DESC"


    @api.multi
    def _default_credit_limit_and_days(self):
        return self.assign_id.credit_limit


    # @api.multi
    # def _default_credit_days(self):
    #     return self.assign_id.days


    assign_id = fields.Many2one('customer.creditlimit.assign')
    partner_id = fields.Many2one('res.partner', "Customer", required=True)
    assign_date = fields.Date(string="Credit Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'))
    value = fields.Float(string='Credit Limit', default=_default_credit_limit_and_days)
    remaining_credit_limit = fields.Float(string='Remaining Credit Limit')
    day_num = fields.Integer(string='Credit Days', )


    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ], select=True, readonly=True, default='draft')


    @api.constrains('day_num')
    def check_credit_days(self):
        if self.day_num <= 0.00:
            raise ValidationError('Days can not be zero or negative')


