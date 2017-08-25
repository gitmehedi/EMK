from openerp import api, fields, models, exceptions, _
from openerp.exceptions import UserError, ValidationError
import time,datetime

class SaleDeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(size=100, string="Name", required=True ,readonly=True,
                             states={'draft': [('readonly', False)]})
    so_date = fields.Date('Sales Order Date', readonly=True,
                             states={'draft': [('readonly', False)]})
    deli_address = fields.Char('Delivery Address', readonly=True,
                             states={'draft': [('readonly', False)]})
    """ All relations fields """

    sale_order_id = fields.Many2one('sale.order',string='Order Lines', required=True, readonly=True,
                             states={'draft': [('readonly', False)]})
    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True,
                             states={'draft': [('readonly', False)]})
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True,
                             states={'draft': [('readonly', False)]})
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True,
                             states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('delivery.order.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})
    cash_ids = fields.One2many('cash.payment.line', 'pay_cash_id', string="Payment Terms:Cash", readonly=True,
                               states={'draft': [('readonly', False)]})

    cheque_ids=  fields.One2many('cheque.payment.line', 'pay_cash_id', string="Payment Terms:Cash", readonly=True,
                               states={'draft': [('readonly', False)]})
    tt_ids = fields.One2many('tt.payment.line', 'pay_tt_id', string="Payment Terms:Cash", readonly=True,
                                 states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.payment.line', 'pay_lc_id', string="Payment Terms:Cash", readonly=True,
                             states={'draft': [('readonly', False)]})

    requested_by = fields.Many2one('hr.employee', string="Requested By", default=_current_employee, readonly=True)

    approver1_id = fields.Many2one('hr.employee', string="Approved By",
                                   readonly=True)
    approver2_id = fields.Many2one('hr.employee', string="Confirmed By",
                                   readonly=True)

    requested_date = fields.Date(string="Requested Date", default=datetime.date.today(), readonly=True)
    approved_date = fields.Date('Approved Date',
                                states={'draft': [('invisible', True)],
                                        'validate': [('invisible', True)],
                                        'close': [('invisible', False), ('readonly', True)],
                                        'approve': [('invisible', False), ('readonly', True)]})
    confirmed_date = fields.Date(string="Confirmed Date", _defaults=lambda *a: time.strftime('%Y-%m-%d'), readonly=True)


    """ State fields for containing various states """
    so_type = fields.Selection([
        ('cash', 'Cash'),
        ('credit_sales', 'Credit'),
        ('lc_sales', 'L/C'),
    ], string='Sale Order Type', readonly=True, states={'draft': [('readonly', False)]})

    """ State fields for containing various states """
    state = fields.Selection([
        ('draft', "To Submit"),
        ('validate', "To Approve"),
        ('approve', "Second Approval"),
        ('close', "Approved")
    ], default='draft')
    """ All functions """

    @api.multi
    def unlink(self):
        for order in self:
            if order.state != 'draft':
                raise UserError(_('You can not delete this.'))
            order.line_ids.unlink()
        return super(SaleDeliveryOrder, self).unlink()

    @api.one
    def action_draft(self):
        self.state = 'draft'
        self.line_ids.write({'state':'draft'})

    @api.one
    def action_approve(self):
        self.state = 'approve'
        self.line_ids.write({'state':'approve'})
        self.approver2_id = self.env.user.employee_ids.id
        return self.write({'state': 'approve', 'approved_date': time.strftime('%Y-%m-%d %H:%M:%S')})

    @api.one
    def action_validate(self):
        self.state = 'validate'
        self.line_ids.write({'state':'validate'})

    @api.one
    def action_close(self):
        self.state = 'close'
        self.line_ids.write({'state':'close'})
        self.approver1_id = self.env.user.employee_ids.id
        return self.write({'state': 'close', 'confirmed_date': time.strftime('%Y-%m-%d %H:%M:%S')})


    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        if self.sale_order_id:
            sale_order_obj = self.env['sale.order'].search([('id', '=',self.sale_order_id.id)])
            if sale_order_obj:
                self.parent_id = sale_order_obj.partner_id.id
                self.payment_term_id = sale_order_obj.payment_term_id.id
                self.warehouse_id = sale_order_obj.warehouse_id.id
                self.so_type = sale_order_obj.credit_sales_or_lc
                self.so_date = sale_order_obj.confirmation_date


