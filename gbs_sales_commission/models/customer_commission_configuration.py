import datetime
import time
from odoo import api, fields, models


class CustomerCommissionConfiguration(models.Model):
    _name = "customer.commission.configuration"
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'confirmed_date desc'

    def _current_employee(self):
        return self.env.user.id

    requested_date = fields.Date(string="Requested Date", required=True, default=datetime.date.today(),
                                 readonly=True, states={'draft': [('readonly', False)]})
    approved_date = fields.Date('Approved Date',
                   states = {'draft': [('invisible', True)],
                             'validate': [('invisible', True)],
                             'close': [('invisible',False),('readonly',True)],
                             'approve': [('invisible',False),('readonly',True)]})
    confirmed_date = fields.Date(string="Confirmed Date",readonly=True)

    status = fields.Boolean(string='Status', default=True, required=True)

    commission_type = fields.Selection([
        ('by_product', 'By Product'),
        ('by_customer', 'By Customer')
    ], default='by_product', string='Commission Type', required=True,
        readonly=True, states={'draft': [('readonly', False)]})

    """ Relational Fields """
    product_id = fields.Many2one('product.product', string="Product",
                                 domain="([('sale_ok','=','True'),('type','=','consu')])",
                                 readonly=True, states={'draft': [('readonly', False)]})

    customer_id = fields.Many2one('res.partner', string="Customer", domain="([('customer','=','True')])",
                                  readonly=True, states={'draft': [('readonly', False)]})
    requested_by_id = fields.Many2one('res.partner', string="Requested By", required=True,
                                      default=_current_employee,
                                      readonly=True, states={'draft': [('readonly', False)]})
    approved_user_id = fields.Many2one('res.partner', string="Approved By", default=_current_employee,
                                       readonly=True, states={'draft': [('readonly', False)]})
    confirmed_user_id = fields.Many2one('res.partner', string="Confirmed By", default=_current_employee,
                                        readonly=True, states={'draft': [('readonly', False)]})

    config_product_ids = fields.One2many('customer.commission.configuration.product', 'config_parent_id',
                                         readonly=True, states={'draft': [('readonly', False)]})
    config_customer_ids = fields.One2many('customer.commission.configuration.customer', 'config_parent_id',
                                          readonly=True, states={'draft': [('readonly', False)]})

    """ State fields for containing various states """
    state = fields.Selection([
        ('draft', "To Submit"),
        # ('request', "Request"),
        ('validate', "To Approve"),
        # ('confirm', "Confirm"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], readonly=True, track_visibility='onchange', copy=False, default='draft')

    """ All functions """
    @api.onchange('commission_type')
    def onchange_commission_type(self):
        if self.commission_type:
            self.product_id = 0
            self.customer_id = 0
            self.config_product_ids = []
            self.config_customer_ids = []

    @api.multi
    def name_get(self):
        result = []
        for record in self:

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
        return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.one
    def action_validate(self):
        self.state = 'validate'

    @api.one
    def action_close(self):
        self.state = 'close'
    @api.one
    def action_close(self):
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
                    commission = customer.commission_ids.create(vals)
                else:
                    find_cust.write({'commission_rate': rec.new_value})

                update = cusComLine.search(
                    [('customer_id', '=', rec.customer_id.id), ('product_id', '=', self.product_id.id)])
                update.write({'status': False})

                val_line['customer_id'] = rec.customer_id.id
                val_line['product_id'] = self.product_id.id
                val_line['effective_date'] = datetime.date.today()
                val_line['commission_rate'] = rec.new_value
                val_line['commission_id'] = find_cust.id if find_cust  else commission.id
                val_line['status'] = True
                cusComLine.create(val_line)

            self.state = 'close'
            return self.write({'state': 'close', 'confirmed_date': time.strftime('%Y-%m-%d %H:%M:%S')})

