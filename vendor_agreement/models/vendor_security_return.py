from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorSecurityReturn(models.Model):
    _name = 'vendor.security.return'
    _inherit = ['mail.thread']
    _description = 'Vendor Security Return'
    _order = 'name desc'

    @api.multi
    def _get_partner_ids(self):
        partner_obj = self.env['vendor.security.deposit'].sudo().search([('state', '=', 'draft')])
        partner_list = list({obj.partner_id.id for obj in partner_obj})
        return [(6, 0, partner_list)]

    name = fields.Char(required=False, track_visibility='onchange', string='Name', default='Draft VSR')
    filtered_partner_ids = fields.Many2many('res.partner', 'res_partner_vendor_security_return_rel',
                                            'vendor_security_return_id', 'res_partner_id',
                                            default=lambda self: self._get_partner_ids())
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    vsd_ids = fields.Many2many('vendor.security.deposit', 'vendor_security_deposit_return_rel',
                               'return_id', 'deposit_id', string='Security Deposits',
                               readonly=True, states={'draft': [('readonly', False)]})
    optional_vsd_ids = fields.Many2many('vendor.security.deposit',
                                        'vendor_security_deposit_return_optional_rel',
                                        'return_id', 'deposit_id',
                                        string='Security Deposits', readonly=True,
                                        states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Amount", readonly=True, track_visibility='onchange',
                          states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('vendor.security.return.line', 'return_id',
                               string='Security Return Lines')
    state = fields.Selection([
        ('draft', "Pending"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    description = fields.Text('Particulars', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    payment_line_ids = fields.One2many('payment.instruction', 'security_return_id', readonly=True, copy=False)
    total_payment_amount = fields.Float('Total Payment', compute='_compute_payment_amount',
                                        store=True, readonly=True, track_visibility='onchange', copy=False)
    total_payment_approved = fields.Float('Advance Paid', compute='_compute_payment_amount',
                                          store=True, readonly=True, track_visibility='onchange', copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    payment_btn_visible = fields.Boolean(compute='_compute_payment_btn_visible', default=False,
                                         string="Is Visible")


    @api.one
    @api.depends('payment_line_ids.amount', 'payment_line_ids.state')
    def _compute_payment_amount(self):
        for rec in self:
            rec.total_payment_amount = sum(line.amount for line in rec.payment_line_ids if line.state not in ['cancel'])
            rec.total_payment_approved = sum(line.amount for line in rec.payment_line_ids if line.state in ['approved'])

    @api.onchange('vsd_ids')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.vsd_ids:
                for vsd in rec.vsd_ids:
                    remaining_vsd_amount = vsd.amount - vsd.adjusted_amount
                    amount = amount + remaining_vsd_amount
                rec.amount = amount
            else:
                rec.amount = 0

    @api.depends('amount', 'total_payment_amount')
    def _compute_payment_btn_visible(self):
        for record in self:
            if record.state == 'approve':
                if record.amount and record.total_payment_amount \
                        and record.amount <= record.total_payment_amount:
                    record.payment_btn_visible = False
                else:
                    record.payment_btn_visible = True
            else:
                record.payment_btn_visible = False

    @api.onchange('vsd_ids')
    def _onchange_vsd_ids(self):
        for rec in self:
            rec.optional_vsd_ids = rec.vsd_ids

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.vsd_ids = None
            rec.amount = 0.0

    @api.multi
    def action_confirm(self):
        for rec in self:
            if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            if not rec.vsd_ids:
                raise Warning("No Vendor Security Deposit is selected")
            if not rec.amount > 0:
                raise ValidationError("Amount must be greater than Zero")
            name = self.env['ir.sequence'].sudo().next_by_code('vendor.security.return') or 'New'
            rec.write({
                'state': 'confirm',
                'name': name
            })

    @api.multi
    def action_approve(self):
        security_return_line_obj = self.env['vendor.security.return.line']
        for rec in self:
            if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
            remaining_balance = rec.amount
            if rec.vsd_ids:
                for vsd in rec.vsd_ids:
                    security_deposit_obj = self.env['vendor.security.deposit'].sudo().search([('id', '=', vsd.id)])
                    remaining_vsd_balance = vsd.amount - vsd.adjusted_amount
                    line_vals = {
                        'vsd_id': vsd.id,
                        'return_id': rec.id,
                        'date': fields.datetime.now()
                    }
                    if remaining_balance >= remaining_vsd_balance:
                        line_vals['amount'] = remaining_vsd_balance
                        remaining_balance = remaining_balance - remaining_vsd_balance
                        security_return_line_obj.create(line_vals)
                        new_vsd_adjusted_amount = vsd.amount
                        security_deposit_obj.write({
                            'adjusted_amount': new_vsd_adjusted_amount,
                            'state': 'done'
                        })

                    elif remaining_vsd_balance > remaining_balance > 0:
                        line_vals['amount'] = remaining_balance
                        security_return_line_obj.create(line_vals)
                        new_vsd_adjusted_amount = vsd.adjusted_amount + remaining_balance
                        security_deposit_obj.write({
                            'adjusted_amount': new_vsd_adjusted_amount
                        })
                        break

            self._cr.execute('DELETE FROM res_partner_vendor_security_return_rel WHERE vendor_security_return_id={}'
                             .format(self.id))
            self.create_journal()

            rec.write({
                'state': 'approve',
                'approver_id': self.env.user.id
            })

    def action_payment(self):
        res = self.env.ref('vendor_agreement.view_security_return_payment_instruction_wizard')

        return {
            'name': _('Payment Instruction'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'security.return.payment.instruction.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {'amount': self.amount - self.total_payment_amount or 0.0,
                        'total_payment_approved': self.total_payment_approved or 0.0,
                        'currency_id': self.currency_id.id or False,
                        'operating_unit_id': self.company_id.head_branch_id.id or False,
                        'partner_id': self.partner_id.id or False,
                        'company_id': self.company_id.id
                        },
        }

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.write({'state': 'cancel'})

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(VendorSecurityReturn, self).unlink()

    def create_journal(self):
        journal_id = self.env.ref('vendor_agreement.vendor_advance_journal')
        ogl_data = {}
        ogl_data['journal_id'] = journal_id.id
        ogl_data['date'] = fields.date.today()
        ogl_data['operating_unit_id'] = journal_id.operating_unit_id.id
        ogl_data['state'] = 'posted'
        ogl_data['name'] = self.name

        journal_item_data = []
        for line in self.line_ids:
            journal_item_data.append([
                0, 0, {
                    'name': self.description or 'Vendor Security Return',
                    'ref': line.vsd_id.name,
                    'date': fields.date.today(),
                    'account_id': self.company_id.security_deposit_account_id.id,
                    'operating_unit_id': journal_id.operating_unit_id.id,
                    'debit': line.amount,
                    'credit': 0.0,
                    'due_date': fields.date.today()

                }
            ])

        supplier_credit_item = [
            0, 0, {
                'name': self.description or 'Vendor Security Return',
                'ref': self.name,
                'date': fields.date.today(),
                'account_id': self.partner_id.property_account_payable_id.id,
                'operating_unit_id': journal_id.operating_unit_id.id,
                'debit': 0.0,
                'credit': self.amount,
                'due_date': fields.date.today()

            }
        ]
        journal_item_data.append(supplier_credit_item)
        ogl_data['line_ids'] = journal_item_data
        self.env['account.move'].create(ogl_data)

    @api.constrains('amount')
    def _check_amount(self):
        for line in self:
            total_amount = sum(vsd.amount for vsd in line.vsd_ids)
            if line.amount > total_amount:
                raise ValidationError(_("Sorry! This amount is bigger than Summation of deposits amount. "
                                        "Summation of deposits amount is %s") % (total_amount))


class PaymentInstruction(models.Model):
    _inherit = 'payment.instruction'

    security_return_id = fields.Many2one('vendor.security.return', string='Vendor Security Return')




