from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class VendorSecurityReturn(models.Model):
    _name = 'vendor.security.return'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Vendor Security Return'
    _order = 'id desc'

    @api.multi
    def _get_partner_ids(self):
        partner_obj = self.env['vendor.security.deposit'].sudo().search([('state', '=', 'approve'),
                                                                         ('outstanding_amount', '>', 0)])
        partner_list = list({obj.partner_id.id for obj in partner_obj})
        return [(6, 0, partner_list)]

    name = fields.Char(required=True, copy=False, track_visibility='onchange', string='Name', default='Draft VSR')
    date = fields.Date(track_visibility='onchange', string='Date', copy=False,
                       readonly=True, states={'draft': [('readonly', False)]})
    filtered_partner_ids = fields.Many2many('res.partner', 'res_partner_vendor_security_return_rel',
                                            'vendor_security_return_id', 'res_partner_id',
                                            default=lambda self: self._get_partner_ids())
    partner_id = fields.Many2one('res.partner', string='Vendor', ondelete='restrict', required=True,
                                 track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    vsd_ids = fields.Many2many('vendor.security.deposit', 'vendor_security_deposit_return_rel',
                               'return_id', 'deposit_id', string='Security Deposits',
                               readonly=True, states={'draft': [('readonly', False)]})
    input_vsd_ids = fields.Many2many('vendor.security.deposit',
                                        'vendor_security_deposit_return_optional_rel',
                                        'return_id', 'deposit_id',
                                        required=True, string='Security Deposits', readonly=True,
                                        states={'draft': [('readonly', False)]})
    amount = fields.Float(string="Amount", readonly=True, track_visibility='onchange', digits=(16, 2),
                          required=True, states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('vendor.security.return.line', 'return_id',
                               string='Security Return Lines')
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Confirmed"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')
    maker_id = fields.Many2one('res.users', 'Maker', track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    description = fields.Char('Particulars', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    move_id = fields.Many2one('account.move', string='Journal', readonly=True, copy=False)

    @api.onchange('input_vsd_ids')
    def _onchange_amount(self):
        for rec in self:
            amount = 0
            if rec.input_vsd_ids:
                for vsd in rec.input_vsd_ids:
                    remaining_vsd_amount = vsd.amount - vsd.adjusted_amount
                    amount = amount + remaining_vsd_amount
                rec.amount = amount
            else:
                rec.amount = 0

    @api.onchange('input_vsd_ids')
    def _onchange_vsd_ids(self):
        for rec in self:
            rec.vsd_ids = rec.input_vsd_ids

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.input_vsd_ids = None
            rec.amount = 0.0

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                if not rec.vsd_ids:
                    raise ValidationError("[Validation Error] No Vendor Security Deposit is selected")
                if not rec.amount > 0:
                    raise ValidationError("[Validation Error] Amount must be greater than Zero")
                if rec.vsd_ids:
                    rec._check_deposit_amount(rec.vsd_ids, rec.amount)
                name = self.env['ir.sequence'].sudo().next_by_code('vendor.security.return') or 'New'
                rec.write({
                    'state': 'confirm',
                    'name': name,
                    'maker_id': self.env.user.id
                })

    @api.multi
    def action_approve(self):
        security_return_line_obj = self.env['vendor.security.return.line']
        for rec in self:
            if rec.state == 'confirm':
                if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                    raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
                remaining_balance = rec.amount
                if rec.vsd_ids:
                    rec._check_deposit_amount(rec.vsd_ids, rec.amount)
                    for vsd in rec.vsd_ids:
                        security_deposit_obj = self.env['vendor.security.deposit'].sudo().search([('id', '=', vsd.id)])
                        remaining_vsd_balance = vsd.amount - vsd.adjusted_amount
                        line_vals = {
                            'vsd_id': vsd.id,
                            'return_id': rec.id,
                            'date': self.date or fields.date.today()
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
                journal_id = self.env.ref('vendor_advance.vendor_advance_journal')
                # journal_id = self.env['account.journal'].search([('code', '=', 'MISC')], limit=1)
                move = rec.create_account_move(journal_id)

                rec.write({
                    'state': 'approve',
                    'approver_id': self.env.user.id,
                    'move_id': move.id
                })

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

    def create_account_move(self, journal_id):
        ogl_data = {}
        ogl_data['journal_id'] = journal_id.id
        ogl_data['date'] = self.date or fields.date.today()
        ogl_data['state'] = 'draft'
        ogl_data['name'] = self.name
        ogl_data['partner_id'] = self.partner_id.id
        ogl_data['company_id'] = self.company_id.id

        journal_item_data = []
        for line in self.line_ids:
            deposit_debit_item_data = self.get_deposit_debit_item(line)
            journal_item_data.append([0, 0, deposit_debit_item_data])

        supplier_credit_item_data = self.get_supplier_credit_item(journal_id)
        supplier_credit_item = [0, 0, supplier_credit_item_data]
        journal_item_data.append(supplier_credit_item)
        ogl_data['line_ids'] = journal_item_data
        move = self.env['account.move'].create(ogl_data)
        move.sudo().post()
        return move

    def get_deposit_debit_item(self, deposit_line):
        deposit_debit_item_data = {
            'name': self.description or 'Vendor Security Return',
            'ref': deposit_line.vsd_id.name,
            'date': self.date or fields.date.today(),
            'account_id': deposit_line.vsd_id.account_id.id,
            'debit': deposit_line.amount,
            'credit': 0.0,
            'company_id': self.company_id.id

        }
        return deposit_debit_item_data

    def get_supplier_credit_item(self, journal_id):
        supplier_credit_item_data = {
                'name': self.description or 'Vendor Security Return',
                'ref': self.name,
                'date': self.date or fields.date.today(),
                'account_id': self.partner_id.property_account_payable_id.id,
                'debit': 0.0,
                'credit': self.amount,
                'company_id': self.company_id.id

            }
        return supplier_credit_item_data

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError("Please Check Your Amount!! \n Amount Never Take Negative Value!")
            if rec.input_vsd_ids:
                rec._check_deposit_amount(rec.input_vsd_ids, rec.amount)

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', 'not in', ['cancel', 'draft'])])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    def _check_deposit_amount(self, vsd_ids, amount):
        for vsd in vsd_ids:
            if vsd.amount <= vsd.adjusted_amount:
                raise ValidationError(_("This Security Deposit has already been fully returned : %s") % (vsd.name))
        total_amount = sum(vsd.amount - vsd.adjusted_amount for vsd in vsd_ids)
        if amount > total_amount:
            raise ValidationError(_("Sorry! This amount is bigger than Summation of outstanding amount of selected deposits. "
                                    "Summation of adjustment amount of deposits is %s") % (total_amount))


class VendorSecurityReturnLine(models.Model):
    _name = 'vendor.security.return.line'
    _description = 'Vendor Security Return Line'
    _order = 'id desc'

    return_id = fields.Many2one('vendor.security.return', string="Return Id")
    vsd_id = fields.Many2one('vendor.security.deposit', string="Deposit Id")
    date = fields.Date('Return Date')
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange')