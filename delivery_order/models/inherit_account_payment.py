from odoo import api, fields, models


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order',
                                    domain=[('state', '=', 'done')], readonly=True,
                                    states={'draft': [('readonly', False)]})
    is_this_payment_checked = fields.Boolean(string='Is This Payment checked with SO', default=False)
    my_menu_check = fields.Boolean(string='Check')
    is_cash_payment = fields.Boolean(string='Cash Payment', default=True)

    ## if cash
    deposited_bank = fields.Char(string='Deposited Bank', readonly=True, states={'draft': [('readonly', False)]})
    bank_branch = fields.Char(string='Branch', readonly=True,states={'draft': [('readonly', False)]})
    deposit_slip = fields.Integer(string='Deposit Slip',readonly=True,states={'draft': [('readonly', False)]})

    # if Bank
    cheque_no = fields.Char(string='Cheque No',readonly=True,states={'draft': [('readonly', False)]})
    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money'),
        ('transfer', 'Internal Transfer')
    ], string='Payment Type', default='inbound')

    payment_transaction_id = fields.Many2one('payment.transaction', string="Payment Transaction",readonly=True,states={'draft': [('readonly', False)]})
    # partner_type = fields.Selection([
    #         ('customer', 'Customer'),
    #         ('supplier', 'Vendor')
    #     ],readonly=True,states={'draft': [('readonly', False)]})

    @api.onchange('partner_id')
    def _onchange_partner_id(self):

        if (self.partner_type == 'customer'):
            so_pool = self.env['sale.order'].search([('partner_id', '=', self.partner_id.id)])

            for order in so_pool:
                self.sale_order_id = order.id
