from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

import time


class customer_creditlimit_assign(models.Model):
    _name = 'customer.creditlimit.assign'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Credit Limit"
    _order = 'id DESC'

    name = fields.Char(string='Name', index=True, readonly=True)
    description = fields.Char(string='Description',size=50,index=True, states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                  'validate': [('readonly', True)],
                                  'approve': [('readonly', True)]})
    sequence_id = fields.Char('Sequence', readonly=True)
    approve_date = fields.Date('Approved Date', track_visibility='onchange',
                               states={'draft': [('invisible', True)], 'confirm': [('invisible', True)],
                                       'validate1': [('invisible', True), ], 'validate': [('invisible', True)],
                                       'approve': [('invisible', False), ('readonly', True)]})
    credit_limit = fields.Float('Credit Limit',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'validate': [('readonly', True)], 'approve': [('readonly', True)]},
                                track_visibility='onchange')
    days = fields.Integer('Credit Days',
                          states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                  'validate': [('readonly', True)],
                                  'approve': [('readonly', True)]})
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user,
                                   readonly=True, track_visibility='onchange')

    approver1_id = fields.Many2one('res.users', string='Accounts Approval By', track_visibility='onchange',readonly=True)
    approver2_id = fields.Many2one('res.users', string='Final Approval By', track_visibility='onchange', readonly=True)
    approver3_id = fields.Many2one('res.users', string='Sales Approval By', track_visibility='onchange', readonly=True)

    """ Relational Fields """
    limit_ids = fields.One2many('res.partner.credit.limit', 'assign_id', 'Limits',
                                states={'confirm': [('readonly', True)], 'validate1': [('readonly', True)],
                                        'validate': [('readonly', True)], 'approve': [('readonly', True)]})

    """ State fields for containing various states """
    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Sales Approval'),
         ('validate', 'Accounts Approval'),
         ('validate1', 'CXO Approval'),
         ('approve', 'Approved'),
         ('refuse', 'Refused'),
         ('cancel', 'Cancelled'), ],
        default='draft', track_visibility='onchange')

    """ All functions """

    @api.model
    def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('customer.creditlimit.assign') or '/'
        # vals['name'] = seq
        return super(customer_creditlimit_assign, self).create(vals)

    @api.multi
    def approve_creditlimit_run(self):

        self.limit_ids.write(
            {'remaining_credit_limit': self.credit_limit, 'state': 'approve', 'assign_date': time.strftime('%Y-%m-%d')})
        self.approver2_id = self.env.user
        return self.write({'state': 'approve', 'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.multi
    def unlink(self):
        for limit in self:
            if limit.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(customer_creditlimit_assign, self).unlink()

    # @api.constrains('credit_limit', 'days')
    # def _check_value(self):
    #     if self.credit_limit <= 0 or self.days <= 0:
    #         raise Warning("Limit or Days never take zero or negative value!")

    @api.multi
    def action_confirm(self):
        seq = self.env['ir.sequence'].next_by_code('customer.creditlimit.assign') or '/'
        self.name = seq

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
        self.approver3_id = self.env.user

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
        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('gbs_application_group.group_cxo'):
            domain = [
                ('state', 'in', ['validate1'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_account'):
            domain = [
                ('state', 'in', ['validate'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_sale'):
            domain = [
                ('state', 'in', ['confirm'])]
            return domain
        else:
            return False

        return domain


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

    limit_ids = fields.One2many('res.partner.credit.limit', 'partner_id', 'Limits', readonly=True, domain=[('state', '=', 'approve')])
    credit_limit = fields.Float(compute='_current_limit', string='Credit Limit', )
    remaining_credit_limit = fields.Float(compute='_remaining_credit_limit', string='Remaining Credit Limit')

    """ All functions """

    @api.constrains('name')
    def _check_unique_name(self):
        if self.name:
            name = self.env['res.partner'].search([('name', '=ilike', self.name)])
            if len(name) > 1:
                raise ValidationError('Customer already exists.')


                ## Total Invoiced amount which is not in Paid state

    # @api.multi
    # def unpaid_total_invoiced_amount(self):
    #     for invc in self:
    #         acc_invoice_pool = invc.env['account.invoice'].search([('journal_id.type', '=', 'sale'),
    #                                                                ('partner_id', '=', invc.id),
    #                                                                ('state', '=', 'draft')])
    #
    #         total_list = []
    #         for inv_ in acc_invoice_pool:
    #             total_list.append(inv_.amount_total)
    #
    #         total_unpaid_amount = sum(total_list)
    #
    #     return total_unpaid_amount


    # Total DO Qty amount which is not delivered yet
    # @api.multi
    # def undelivered_do_qty_amount(self):
    #     tot_undelivered_amt = 0
    #     for stock in self:
    #         # picking_type_id.code "outgoing" means: Customer
    #         stock_pick_pool = stock.env['stock.picking'].search([('picking_type_id.code', '=', 'outgoing'),
    #                                                              ('picking_type_id.name', '=', 'Delivery Orders'),
    #                                                              ('partner_id', '=', stock.id),
    #                                                              ('state', '!=', 'done')])
    #
    #         stock_amt_list = []
    #         for stock_pool in stock_pick_pool:
    #             # We assume that delivery_order_id will never be null,
    #             # but to avoid garbage data added this extra checking
    #             if stock_pool.delivery_order_id:
    #                 for so_line in stock_pool.delivery_order_id.sale_order_id.order_line:
    #                     for prod_op_ids in stock_pool.pack_operation_product_ids:
    #                         unit_price = so_line.price_unit
    #                         product_qty = prod_op_ids.product_qty
    #                         stock_amt_list.append(unit_price * product_qty)
    #
    #             tot_undelivered_amt = sum(stock_amt_list)
    #
    #     return tot_undelivered_amt


    @api.multi
    def _remaining_credit_limit(self):
        for lim in self:

            total_credit_sale = 0
            sale_pool = lim.env['sale.order'].search(
                [('partner_id', '=', lim.id), ('credit_sales_or_lc', '=', 'credit_sales'),('state','=','done')])

            for s in sale_pool:
                total_credit_sale = s.amount_total + total_credit_sale

            customer_total_credit = total_credit_sale + lim.credit
            remain = lim.credit_limit - customer_total_credit

            if remain > 0:
                lim.remaining_credit_limit = remain
            else:
                lim.remaining_credit_limit = 0

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
            else:
                partner.credit_limit = 0


class res_partner_credit_limit(models.Model):
    _name = 'res.partner.credit.limit'
    _order = "id DESC"

    @api.multi
    def _default_credit_limit_and_days(self):
        return self.assign_id.credit_limit

    assign_id = fields.Many2one('customer.creditlimit.assign',ondelete='cascade')
    partner_id = fields.Many2one('res.partner', "Customer", required=True,domain="[('customer', '=', True),('parent_id', '=', False)]")

    #domain = [('customer', '=', True), ('parent_id', '=', False)]
    assign_date = fields.Date(string="Credit Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'))
    value = fields.Float(string='Credit Limit', default=_default_credit_limit_and_days)
    day_num = fields.Integer(string='Credit Days', )

    @api.constrains('value', 'day_num')
    def _check_value(self):
        for lim in self:
            if lim.value <= 0 or lim.day_num <= 0:
                raise Warning("Limit or Days never take zero or negative value!")



    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
    ], select=True, readonly=True, default='draft')

    @api.constrains('day_num')
    def check_credit_days(self):
        if self.day_num <= 0.00:
            raise ValidationError('Days can not be zero or negative')

    @api.multi
    def unlink(self):
        for limit in self:
            if limit.state != 'draft':
                raise UserError(_('You cannot delete credit limit which is not draft state!'))
        return super(res_partner_credit_limit, self).unlink()