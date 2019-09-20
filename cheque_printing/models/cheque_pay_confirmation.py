from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ChequePayConfirmation(models.Model):
    _name = 'cheque.pay.confirmation'
    _inherit = ['mail.thread']
    _rec_name = 'name'


    name = fields.Char(string='name', readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved')
    ], default='draft')

    line_ids = fields.One2many('cheque.pay.confirmation.line', 'parent_id', string="Line Ids")


    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('cheque.pay.confirmation') or '/'
        vals['name'] = seq
        return super(ChequePayConfirmation, self).create(vals)


    def action_approved(self):
        self.cheque_info_journal_enrty()
        self.state = 'approved'


    @api.multi
    def cheque_info_journal_enrty(self):

        for cr in self:
            for line in cr.line_ids:
                line_ids = []
                debit_sum = 0.0
                credit_sum = 0.0

                # @todo : Need clarification if it will be Cheques date or current systems date
                date = line.cheque_date

                move_dict = {
                    'journal_id': line.partner_id.company_id.bank_journal_ids.id,
                    'date': date,
                }

                amount = line.amount

                debit_account_id = line.partner_id.company_id.bank_journal_ids.default_debit_account_id
                credit_account_id = line.partner_id.company_id.bank_journal_ids.default_credit_account_id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': debit_account_id.name,
                        'partner_id': line.partner_id.id,
                        'account_id': debit_account_id.id,
                        'journal_id': line.partner_id.company_id.bank_journal_ids.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                    })

                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': credit_account_id.name,
                        'partner_id': line.partner_id.id,
                        'account_id': credit_account_id.id,
                        'journal_id': line.partner_id.company_id.bank_journal_ids.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                    })

                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']

                move_dict['line_ids'] = line_ids
                move = self.env['account.move'].create(move_dict)
                move.post()



    @api.multi
    def unlink(self):
        for cheque in self:
            if cheque.state != 'draft':
                raise ValidationError('You can not delete record which is not in Draft state')
            cheque.unlink()
        return super(ChequePayConfirmation, self).unlink()


class ChequePayConfirmationLine(models.Model):
    _name = 'cheque.pay.confirmation.line'


    partner_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)])
    cheque_number = fields.Integer(string='Cheque No.')
    cheque_date = fields.Date(string='Date', )
    amount = fields.Float(string='Amount',)

    parent_id = fields.Many2one('cheque.pay.confirmation', ondelete='cascade')

