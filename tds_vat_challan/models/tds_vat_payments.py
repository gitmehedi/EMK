from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError


class TDSVATPayment(models.Model):
    _name = 'tds.vat.payment'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'
    _description = 'TDS & VAT Payments'
    _rec_name = 'date'

    sequence = fields.Integer('Sequence', help="Gives the sequence of this line when displaying the invoice.")
    credit_account_id = fields.Many2one('account.account', string='Credit Account',
                                        track_visibility='onchange',
                                        help='Credit Account of the Payment')
    date = fields.Date(string='Date',default=fields.Date.context_today,
                       required=True,track_visibility='onchange', copy=False)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        track_visibility='onchange',
                                        default=lambda self: self.env.user.default_operating_unit_id)
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Float(string='Amount')
    account_move_line_ids = fields.Many2many('account.move.line', 'move_line_payment_rel', 'payment_id', 'move_line_id',
                                             string='Payment Move Lines')
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')

    state = fields.Selection([
        ('draft', "Draft"),
        ('approved', "Approved"),
        ('cancel', "Cancel"),
    ], default='draft', string="Status", track_visibility='onchange')

    @api.multi
    def action_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        self.write({'state': 'approved'})
        self.suspend_security().action_journal_creation()
        self.account_move_line_ids.write(
            {'is_paid': True, 'is_pending': False, 'is_challan': False, 'pending_for_paid': False})
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    @api.multi
    def action_reject(self):
        self.write({'state': 'cancel'})
        self.account_move_line_ids.write({'pending_for_paid': False})
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload',
        # }

    @api.multi
    def action_journal_creation(self):
        for rec in self:
            date = fields.Date.context_today(self)
            account_conf_pool = self.env.user.company_id
            if not account_conf_pool.tds_vat_transfer_journal_id:
                raise UserError(
                    _(
                        "Account Settings are not properly set. Please contact your system administrator for assistance."))
            acc_journal_objs = account_conf_pool.tds_vat_transfer_journal_id
            account_move_obj = self.env['account.move']
            account_move_line_obj = self.env['account.move.line'].with_context(check_move_validity=False)
            move_obj = rec.suspend_security()._generate_move(acc_journal_objs, account_move_obj, date)
            for line in rec.account_move_line_ids:
                self._generate_debit_move_line(line, date, move_obj.id, account_move_line_obj)
            self._generate_credit_move_line(date, move_obj.id,account_move_line_obj)
            move_obj.write({'operating_unit_id': self.operating_unit_id.id,})
            move_obj.sudo().post()
        return True

    def _generate_move(self, journal, account_move_obj, date):
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'),
                            _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        name = journal.with_context(ir_sequence_date=date).sequence_id.next_by_id()
        account_move_id = False
        if not account_move_id:
            account_move_dict = {
                'name': name,
                'date': date,
                'ref': '',
                'company_id': self.operating_unit_id.company_id.id,
                'journal_id': journal.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
            account_move = account_move_obj.create(account_move_dict)
        return account_move

    def _generate_credit_move_line(self, date, account_move_id, account_move_line_obj):
        account_move_line_credit = {
            'account_id': self.credit_account_id.id,
            'credit': self.amount,
            'date_maturity': date,
            'debit': False,
            'name': '/',
            'operating_unit_id': self.operating_unit_id.id,
            'move_id': account_move_id,
        }
        account_move_line_obj.create(account_move_line_credit)
        return True

    def _generate_debit_move_line(self, line, date, account_move_id, account_move_line_obj):
        account_move_line_debit = {
            'account_id': line.account_id.id,
            # 'analytic_account_id': line.acc_move_line_id.analytic_account_id.id,
            'credit': False,
            'date_maturity': date,
            'debit': line.credit,
            'name': 'challan/' + line.name,
            'operating_unit_id': line.operating_unit_id.id,
            'move_id': account_move_id,
            'product_id': line.product_id.id or False,
            # 'partner_id': acc_inv_line_obj.partner_id.id,
        }
        account_move_line_obj.create(account_move_line_debit)
        return True

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'draft')]