from odoo import api, fields, models


class InheritAccountPayment(models.Model):
    _inherit = 'account.payment'

    sale_order_id = fields.Many2many('sale.order', string='Sale Order',
                                    readonly=True,
                                    states={'draft': [('readonly', False)]})
    is_this_payment_checked = fields.Boolean(string='Is This Payment checked with SO', default=False)
    my_menu_check = fields.Boolean(string='Check')
    is_cash_payment = fields.Boolean(string='Cash Payment', default=True)

    ## if cash
    deposited_bank = fields.Char(string='Deposited Bank', readonly=True, states={'draft': [('readonly', False)]})
    bank_branch = fields.Char(string='Branch', readonly=True,states={'draft': [('readonly', False)]})
    deposit_slip = fields.Integer(string='Deposit Slip No.',readonly=True,states={'draft': [('readonly', False)]})

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
    def onchange_partner_id(self):
        for ds in self:
            so_id_list = []
            if ds.partner_id:
                so_objs = self.env['sale.order'].sudo().search([('partner_id', '=', ds.partner_id.id),
                                                                    ('state', '=', 'done')])
                if so_objs:
                    for so_obj in so_objs:
                        so_id_list.append(so_obj.id)

                return {'domain': {'sale_order_id': [('id', 'in', so_id_list)]}}


