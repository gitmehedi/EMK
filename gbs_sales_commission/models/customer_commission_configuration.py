import datetime
import time
from openerp.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class CustomerCommissionConfiguration(models.Model):
    _name = "customer.commission.configuration"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id DESC'

    _description = "Customer Commission"
    _rec_name = 'name'

    name = fields.Char(string='Name', index=True, readonly=True)
    requested_date = fields.Date(string="Requested Date", track_visibility='onchange', default=datetime.date.today(), readonly=True)
    approved_date = fields.Date('Approved Date',
                                states={'draft': [('invisible', True)],
                                        'validate': [('invisible', True)],
                                        'validate2': [('invisible', True)],
                                        'close': [('invisible', False), ('readonly', True)],
                                        'approve': [('invisible', True), ('readonly', True)]},
                                track_visibility='onchange')
    confirmed_date = fields.Date(string="Confirmed Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'), readonly=True)

    status = fields.Boolean(string='Status', default=True, required=True)

    commission_type = fields.Selection([
        ('by_product', 'By Product'),
        ('by_customer', 'By Customer')
    ], default='by_product', string='Commission Type', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product",
                                 domain="([('sale_ok','=','True')])",
                                 readonly=True, states={'draft': [('readonly', False)]})

    customer_id = fields.Many2one('res.partner', string="Customer", domain="[('customer', '=', True),('parent_id', '=', False)]",
                                  readonly=True, states={'draft': [('readonly', False)]})
    requested_by = fields.Many2one('res.users', string="Requested By", default=lambda self: self.env.user,
                                   readonly=True, track_visibility='onchange')

    approver1_id = fields.Many2one('res.users', string="Final Approval By", readonly=True, track_visibility='onchange')
    approver2_id = fields.Many2one('res.users', string="Accounts Approval By", readonly=True, track_visibility='onchange')
    approver3_id = fields.Many2one('res.users', string="Sales Approval By", readonly=True, track_visibility='onchange')

    config_product_ids = fields.One2many('customer.commission.configuration.product', 'config_parent_id',
                                         readonly=True, states={'draft': [('readonly', False)]})
    config_customer_ids = fields.One2many('customer.commission.configuration.customer', 'config_parent_id',
                                          readonly=True, states={'draft': [('readonly', False)]})

    """ State fields for containing various states """
    state = fields.Selection([
        ('draft', "Draft"),
        ('validate', "Sales Approval"),
        ('validate2', "Accounts Approval"),
        ('approve', "CXO Approval"),
        ('close', "Approved"),
        ('refused', 'Refused')
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    """ All functions """

    def action_sales_head(self):
        self.state = 'validate2'
        self.approver3_id = self.env.user


    ### Showing batch
    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        domain = []
        if users_obj.has_group('gbs_application_group.group_cxo'):
            domain = [
                ('state', 'in', ['approve'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_account'):
            domain = [
                ('state', 'in', ['validate2'])]
            return domain
        elif users_obj.has_group('gbs_application_group.group_head_sale'):
            domain = [
                ('state', 'in', ['validate'])]
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

    @api.model
    def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('customer.commission.configuration') or '/'
        # vals['name'] = seq
        return super(CustomerCommissionConfiguration, self).create(vals)


    @api.onchange('product_id')
    def onchange_product_id(self):

        if self.product_id:
            if self.commission_type == 'by_product':
                #prod_pool = self.env['product.template'].search([('id', '=', self.product_id.id)])

                if self.product_id.product_tmpl_id.commission_type == 'fixed':
                    for rec in self.config_customer_ids:
                        if rec.customer_id:
                            commission = self.env['customer.commission'].search(
                                [('product_id', '=', self.product_id.id),
                                 ('customer_id', '=', rec.customer_id.id),
                                 ('coms_type', '=', 'fixed'),
                                 ('status', '=', True)])

                            #self.currency_id = self.env.user.company_id.currency_id.id

                            if commission:
                                for coms in commission:
                                    rec.old_value = coms.commission_rate
                            else:
                                rec.old_value = 0

            for rec in self.config_customer_ids:
                if rec.customer_id:
                    commission = self.env['customer.commission'].search(
                        [('product_id', '=', self.product_id.id),
                         ('customer_id', '=', rec.customer_id.id),
                         ('coms_type', '=', 'percentage'),
                         ('status', '=', True)])

                    #self.currency_id = None

                    if commission:
                        for coms in commission:
                            rec.old_value = coms.commission_rate
                    else:
                        rec.old_value = 0


    @api.onchange('customer_id')
    def onchange_customer_id(self):
        for rec in self.config_product_ids:
            if rec.product_id:
                commission = self.env['customer.commission'].search(
                    [('product_id', '=', rec.product_id.id),
                     ('customer_id', '=', self.customer_id.id),
                     ('status', '=', True)])
                if commission:
                    for coms in commission:
                        rec.old_value = coms.commission_rate
                else:
                    rec.old_value = 0


    @api.multi
    def action_cancel(self):
        for coms in self:
            coms.state = 'refused'
            coms.status = False

    # @api.onchange('commission_type')
    # def onchange_commission_type(self):
    #     if self.commission_type:
    #         self.product_id = 0
    #         self.customer_id = 0
    #         self.config_product_ids = []
    #         self.config_customer_ids = []

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = ''

            if record.product_id:
                name = "Commission of Product [%s]" % (record.product_id.name)
            if record.customer_id:
                name = "Commission of Customer [%s]" % (record.customer_id.name)
            result.append((record.id, name))
        return result


    @api.one
    def action_draft(self):
        self.state = 'draft'


    @api.one
    def action_approve(self):
        self.state = 'approve'
        self.approver2_id = self.env.user
        return self.write({'state': 'approve'})


    @api.one
    def action_validate(self):
        seq = self.env['ir.sequence'].next_by_code('customer.commission.configuration') or '/'
        self.name = seq

        self.state = 'validate'


    @api.one
    def action_close(self):
        self.state = 'close'
        cusCom = self.env['customer.commission']
        cusComLine = self.env['customer.commission.line']
        customer_obj = self.env['res.partner']

        if self.commission_type == 'by_customer':
            customer = customer_obj.search([('id', '=', self.customer_id.id)])
            for rec in self.config_product_ids:
                vals, val_line = {}, {}
                vals['customer_id'] = self.customer_id.id
                vals['product_id'] = rec.product_id.id
                vals['commission_rate'] = rec.new_value
                commission = customer.commission_ids.create(vals)

                val_line['customer_id'] = self.customer_id.id
                val_line['product_id'] = rec.product_id.id
                val_line['effective_date'] = datetime.date.today()
                val_line['commission_rate'] = rec.new_value
                val_line['commission_id'] = commission.id
                cusComLine.create(val_line)
        else:
            for rec in self.config_customer_ids:
                customer = customer_obj.search([('id', '=', rec.customer_id.id)])
                find_cust = cusCom.search(
                    [('customer_id', '=', rec.customer_id.id), ('product_id', '=', self.product_id.id)])

                vals, val_line = {}, {}
                if not find_cust:
                    vals['customer_id'] = rec.customer_id.id
                    vals['product_id'] = self.product_id.id
                    vals['commission_rate'] = rec.new_value
                    vals['currency_id'] = rec.currency_id.id

                    commission = customer.commission_ids.create(vals)
                else:
                    for cust in find_cust:
                        cust.write({'currency_id':rec.currency_id.id, 'commission_rate': rec.new_value, 'coms_type': self.product_id.commission_type})

                update = cusComLine.search(
                    [('customer_id', '=', rec.customer_id.id), ('product_id', '=', self.product_id.id)])
                update.write({'status': False})

                val_line['customer_id'] = rec.customer_id.id
                val_line['product_id'] = self.product_id.id
                val_line['effective_date'] = datetime.date.today()
                val_line['commission_rate'] = rec.new_value
                val_line['currency_id'] = rec.currency_id.id

                if find_cust:
                    for custs in find_cust:
                        val_line['commission_id'] = custs.id
                        val_line['coms_type'] = self.product_id.commission_type
                else:
                    val_line['commission_id'] = commission.id

                val_line['status'] = True
                cusComLine.create(val_line)

        self.approver1_id = self.env.user
        return self.write({'state': 'close', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    @api.multi
    def unlink(self):
        for com in self:
            if com.state != 'draft':
                raise UserError(_('You can not delete this.'))
            com.config_customer_ids.unlink()
            com.config_product_ids.unlink()
        return super(CustomerCommissionConfiguration, self).unlink()
