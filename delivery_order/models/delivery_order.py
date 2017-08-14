from openerp import api, fields, models, exceptions, _

class SaleDeliveryOrder(models.Model):
    _name = 'delivery.order'
    _description = 'Delivery Order'

    def _current_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    name = fields.Char(size=100, string="Name", required=True)
    so_date = fields.Date('Sales Order Date',readonly= True)
    approve_date = fields.Date('Approve Date')
    deli_address = fields.Char('Delivery Address')
    approve_by = fields.Many2one('hr.employee', string="Approved By", default=_current_employee, readonly= True)



    """ All relations fields """

    sale_order_id = fields.Many2one('sale.order',string='Order Lines')
    parent_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', readonly=True)
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
    """ All Selection fields """
    state = fields.Selection([
        ('draft', "Draft"),
        ('applied', "Applied"),
        ('approved', "Approved"),
    ], default='draft')

    so_type = fields.Selection([
        ('credit_sales', 'Credit Sales'),
        ('lc_sales', 'LC Sales'),
    ], string='Sale Order Type',readonly= True)

    """All function which process data and operation"""

    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'applied'

    @api.multi
    def action_done(self):
        self.state = 'approved'

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