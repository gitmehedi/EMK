from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class ReceiveOutstandingAdvance(models.Model):
    _name = 'receive.outstanding.advance'
    _inherit = ['mail.thread']
    _description = 'Receive Outstanding Advance'
    _order = 'name desc'

    @api.multi
    def _get_partner_ids(self):
        partner_obj = self.env['vendor.advance'].sudo().search([('state', '=', 'inactive'), ('active', '=', False),
                                                                ('outstanding_amount', '>', 0)])
        partner_list = list({obj.partner_id.id for obj in partner_obj})
        return [(6, 0, partner_list)]

    name = fields.Char('Name', required=True, track_visibility='onchange', copy=False, default='/')
    date = fields.Date(string='Date ', default=fields.Date.today(), track_visibility='onchange',
                       readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', string='Partner', ondelete='restrict',
                                 track_visibility='onchange', required=True,
                                 domain=[('parent_id', '=', False), ('supplier', '=', True)], readonly=True,
                                 states={'draft': [('readonly', False)]})
    advance_ids = fields.Many2many('vendor.advance', string='Advance', track_visibility='onchange', readonly=True,
                                   required=True, states={'draft': [('readonly', False)]}, copy=False,
                                   domain=[('active', '=', False)])
    amount = fields.Float('Amount', required=True, track_visibility='onchange', readonly=True,
                          states={'draft': [('readonly', False)]}, copy=False)
    narration = fields.Char('Particulars', readonly=True, states={'draft': [('readonly', False)]},
                            track_visibility='onchange')
    partner_id_domain_ids = fields.Many2many('res.partner', default=_get_partner_ids,
                                             readonly=True, store=False)
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange',
                               copy=False)
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange', copy=False)
    history_ids = fields.One2many('receive.outstanding.advance.history', 'roa_id', String='History')
    move_id = fields.Many2one('account.move', string='Journal', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, track_visibility='onchange',
                                 states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env['res.company']._company_default_get())
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    debit_account_id = fields.Many2one('account.account', string="Debit GL Account", required=True, readonly=True,
                                       track_visibility='onchange', states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', "Draft"),
        ('confirm', "Waiting For Approval"),
        ('approve', "Approved"),
        ('cancel', "Canceled")], default='draft', string="Status",
        track_visibility='onchange')

    @api.onchange('advance_ids')
    def _onchange_advance_ids(self):
        for rec in self:
            rec.amount = sum(advance.outstanding_amount for advance in self.advance_ids)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        for rec in self:
            rec.advance_ids = None

    @api.multi
    def action_confirm(self):
        for rec in self:
            if rec.state == 'draft':
                if not rec.advance_ids:
                    raise ValidationError("[Validation Error] Please Select at least one Vendor Advance")
                if rec.advance_ids:
                    rec._check_outstanding_amount(rec.advance_ids, rec.amount)
                sequence = self.env['ir.sequence'].next_by_code('receive.outstanding.advance') or ''
                rec.write({
                    'state': 'confirm',
                    'name': sequence,
                    'maker_id': self.env.user.id
                })

    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.state == 'confirm':
                if self.env.user.id == rec.maker_id.id and self.env.user.id != SUPERUSER_ID:
                    raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
                if rec.advance_ids:
                    rec._check_outstanding_amount(rec.advance_ids, rec.amount)
                    history_obj = self.env['receive.outstanding.advance.history']
                    balance = rec.amount
                    for advance in rec.advance_ids:
                        if balance > 0:
                            adjusted_amount = 0
                            if advance.outstanding_amount <= balance:
                                adjusted_amount = advance.outstanding_amount
                                balance -= advance.outstanding_amount
                            elif advance.outstanding_amount > balance > 0:
                                adjusted_amount = balance
                                balance = 0
                            total_adjusted_amount = advance.adjusted_amount + adjusted_amount
                            advance.write({'adjusted_amount': total_adjusted_amount})
                            history_obj.create({
                                'roa_id': rec.id,
                                'advance_id': advance.id,
                                'amount': adjusted_amount
                            })
                journal_id = self.env.ref('vendor_advance.vendor_advance_journal')
                move = self.create_account_move(journal_id)

                rec.write({
                    'state': 'approve',
                    'move_id': move.id,
                    'approver_id': self.env.user.id
                })

    @api.multi
    def create_account_move(self, journal_id):
        move_data = {}
        move_data['journal_id'] = journal_id.id
        move_data['date'] = self.date or fields.Date.today()
        move_data['state'] = 'draft'
        move_data['name'] = self.name
        move_data['partner_id'] = self.partner_id.id
        move_data['company_id'] = self.company_id.id

        move_line_data = []
        debit_item_data = self.get_debit_item_data()
        debit_item = [0, 0, debit_item_data]
        move_line_data.append(debit_item)

        for line in self.history_ids:
            advance_item_data = self.get_advance_credit_item(line)
            move_line_data.append([0, 0, advance_item_data])

        move_data['line_ids'] = move_line_data
        move = self.env['account.move'].create(move_data)
        move.sudo().post()
        return move

    def get_debit_item_data(self):
        debit_item_data = {
                'name': self.narration or 'Receive Outstanding Advance',
                'ref': self.name,
                'date': self.date or fields.Date.today(),
                'account_id': self.debit_account_id.id,
                'debit': self.amount,
                'credit': 0.0,
                'company_id': self.company_id.id
            }
        return debit_item_data

    def get_advance_credit_item(self, advance_line):
        advance_credit_item = {
            'name': self.narration or 'Receive Outstanding Advance',
            'ref': self.name,
            'date': self.date or fields.date.today(),
            'account_id': advance_line.advance_id.account_id.id,
            'debit': 0.0,
            'credit': advance_line.amount,
            'company_id': self.company_id.id
        }
        return advance_credit_item

    @api.multi
    def action_cancel(self):
        for rec in self:
            if rec.state == 'confirm':
                rec.write({
                    'state': 'cancel'
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('You cannot delete a record which is not draft state!'))
        return super(ReceiveOutstandingAdvance, self).unlink()

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount < 0:
                raise ValidationError("Please Check Your Amount!! \n Amount Never Take Negative Value!")
            if rec.advance_ids:
                rec._check_outstanding_amount(rec.advance_ids, rec.amount)

    def _check_outstanding_amount(self, advance_ids, amount):
        for advance in advance_ids:
            if advance.outstanding_amount <= 0:
                raise ValidationError(_("This Advance has already been fully adjusted : %s") % (advance.name))
        total_amount = sum(advance.outstanding_amount for advance in advance_ids)
        if amount > total_amount:
            raise ValidationError(_("Sorry! This amount is bigger than Summation of outstanding amount of selected advances. "
                                    "Summation of outstanding amount of selected advances is %s") % (total_amount))


class ReceiveOutstandingAdvanceHistory(models.Model):
    _name = 'receive.outstanding.advance.history'
    _description = 'Receive Outstanding Amount History'
    _order = 'id desc'

    roa_id = fields.Many2one('receive.outstanding.advance', required=True)
    advance_id = fields.Many2one('vendor.advance', required=True)
    amount = fields.Float(string="Amount", readonly=True,
                          track_visibility='onchange')
