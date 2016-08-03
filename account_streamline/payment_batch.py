import base64
import io
import urllib
import zipfile

from openerp import models
from openerp import fields
from openerp import api
from openerp import exceptions
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp


msg_invalid_line_type = _('Account type %s is not usable in payment vouchers.')
msg_invalid_partner_type_supplier = _('Partner %s is not a supplier.')
msg_invalid_partner_type_customer = _('Partner %s is not a customer.')
msg_define_dc_on_journal = _(
    'Please define default credit/debit accounts on the journal "%s".')
msg_already_reconciled = _(
    'The line %s is already reconciled.'
)


class PaymentBatch(models.Model):
    _name = 'account.payment_batch'
    _inherit = ['mail.thread']

    name = fields.Char(
        string=u"Number",
        required=True,
        size=8,
        default='PB00000',
        track_visibility='onchange',
    )
    date_maturity = fields.Date(
        string="Execution Date",
        required=True,
        track_visibility='onchange',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Payment Method',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])],
    )
    line_ids = fields.One2many(
        comodel_name='account.payment_batch.line',
        inverse_name='batch_id',
        string="Lines",
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('paid', 'Paid')
        ],
        string='State',
        track_visibility='onchange',
    )
    voucher_ids = fields.Many2many(
        comodel_name='account.voucher',
        relation='account_voucher_account_payment_batch_rel_',
        column1='voucher_id',
        column2='payment_batch_id',
        string="Vouchers",
    )
    validate_date = fields.Datetime(
        u"Validation Date",
        track_visibility='onchange',
    )
    validate_user_id = fields.Many2one(
        'res.users',
        u"Validator",
        track_visibility='onchange',
    )

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code(self._name)
        return super(PaymentBatch, self).create(vals)

    @api.multi
    def wkf_draft(self):
        self.state = 'draft'
        return True

    @api.multi
    def _generate_report_action(self, voucher_ids):
        """Generate a Payment Suggestion report action
        """

        context = self.env.context.copy()

        # active_ids contains move-line ids. remove them or the payment
        # suggestion object will use them by default.
        if 'active_ids' in self.env.context:
            del context['active_ids']

        # no way to call this function in a v8 form
        return self.pool.get('payment.suggestion').print_payment_suggestion(
            self.env.cr, self.env.uid, voucher_ids, context=context
        )

    @api.multi
    def generate_vouchers(self):
        voucher_obj = self.env['account.voucher']
        avl_obj = self.env['account.voucher.line']
        voucher_ids = []

        for line in self.line_ids:
            partner = line.partner_id
            journal = self.journal_id
            move_lines = line.line_ids.mapped('move_line_id')

            if not move_lines:
                continue

            vals = {
                'payment_batch_line_id': line.id,
                'partner_id': partner.id,
                'journal_id': journal.id,
                'payment_option': 'without_writeoff',
                'partner_bank_id': line.bank_id.id,
                'amount': line.subtotal,
                'type': 'payment',  # Payment batches are only for payment.

                # Define "pre_line" to ensure the voucher is aware of the
                # lines we are going to add; otherwise it doesn't show all
                # of them.
                'pre_line': True,
            }

            account = (
                journal.default_credit_account_id or
                journal.default_debit_account_id
            )
            if not account:
                raise exceptions.Warning(
                    _('Error!'),
                    msg_define_dc_on_journal % journal.name
                )

            vals['account_id'] = account.id

            voucher = voucher_obj.create(vals)
            voucher_ids.append(voucher.id)

            # now that we have a voucher id we'll add our lines to it
            for ml in move_lines:
                avl = avl_obj.create({
                    'name': ml.name,
                    'voucher_id': voucher.id,

                    # Voucher lines must use the same account as the move
                    # lines, in order to be able to reconcile them with the
                    # move lines created during the validation of the voucher.
                    'account_id': ml.account_id.id,
                    'type': 'dr' if ml.credit else 'cr',
                    'move_line_id': ml.id,
                })

                # Those values are not in the create for some unknown reasons.
                # Maybe we should check if they really need to be written after
                #  the creation process
                avl.write({
                    'reconcile': True,
                    'amount': avl.amount_unreconciled,
                })
                # Mark the lines as batched
                ml.payment_batch_id = self.id

        # Store the vouchers in the batch
        self.voucher_ids = [(6, 0, voucher_ids)]

    @api.multi
    def wkf_paid(self):

        self.generate_vouchers()
        # Validate the vouchers
        self.voucher_ids.signal_workflow('proforma_voucher')

        self.write({
            'validate_date': fields.Datetime.now(),
            'validate_user_id': self.env.uid,
            'state': 'paid',
        })
        return True

    @api.multi
    def unlink(self):
        self.mapped('line_ids').unlink()
        return super(PaymentBatch, self).unlink()


class PaymentBatchLine(models.Model):
    _name = 'account.payment_batch.line'

    batch_id = fields.Many2one(
        comodel_name='account.payment_batch',
        string="Batch",
        required=True,
        ondelete='cascade',
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner",
        required=True
    )
    subtotal = fields.Float(
        string="Subtotal",
        compute='_get_line_values',
        digits=dp.get_precision('Account'),
        store=True,
    )
    nb_lines = fields.Integer(
        string=u"Number of Move Lines",
        compute='_get_line_values',
        store=True,
    )
    line_ids = fields.One2many(
        'account.payment_batch.move.line',
        'batch_line_id',
        string='Move Lines',
    )
    bank_id = fields.Many2one(
        "res.partner.bank",
        "Bank account",
    )

    bank_iban = fields.Char(
        related=('bank_id', 'acc_number'),
        readonly=True,
        store=False,
    )

    bank_bic = fields.Char(
        related=('bank_id', 'bank_bic'),
        readonly=True,
        store=False,
    )

    bank_create_date = fields.Datetime(
        related=('bank_id', 'create_date'),
        string=u"Bank Account Created on",
        readonly=True,
        store=False,
    )

    bank_write_date = fields.Datetime(
        related=('bank_id', 'write_date'),
        string=u"Bank Account Last Updated on",
        readonly=True,
        store=False,
    )

    batch_state = fields.Selection(
        related=('batch_id', 'state')
    )

    @api.depends('line_ids')
    def _get_line_values(self):
        for line in self:
            line.subtotal = sum(
                line.line_ids.mapped(lambda l: l.credit - l.debit)
            )
            line.nb_lines = len(line.line_ids)

    @api.multi
    def save(self):
        return True

    @api.multi
    def open_batch_line_form(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'account_streamline', 'account_payment_batch_line_action'
        )
        res['res_id'] = self.id
        res['view_mode'] = 'form'
        return res

    @api.multi
    def unlink(self):
        self.mapped('line_ids').unlink()
        return super(PaymentBatchLine, self).unlink()


class PaymentBatchMoveLine(models.BaseModel):
    _name = 'account.payment_batch.move.line'

    move_line_id = fields.Many2one(
        'account.move.line',
        u"Move Line",
        required=True,
        delegate=True,
        ondelete='cascade'
    )

    batch_line_id = fields.Many2one(
        'account.payment_batch.line',
        u"Batch Line",
        required=True,
        ondelete='restrict'  # Needs to go through the unlink method
    )

    attachment_ids = fields.Many2many(
        compute='_get_attachment_ids',
        comodel_name='ir.attachment',
        string=u"File Attachment",
        readonly=True,
        store=False,
    )

    attachment_data = fields.Binary(
        compute='_get_attachment_data',
        string=u"File Attachment",
        readonly=True,
        store=False,
    )

    attachment_fname = fields.Binary(
        compute='_get_attachment_fname',
        string=u"File Attachment",
        readonly=True,
        store=False,
    )

    @api.one
    def _get_attachment_ids(self):
        attachments = self.env['ir.attachment']
        for obj in self.move_id, self.move_id.object_reference:
            if obj:
                attachments |= attachments.search([
                    ('res_model', '=', obj._name), ('res_id', '=', obj.id)
                ])
        self.attachment_ids = attachments

    @api.one
    def _get_attachment_data(self):
        attachments = self.attachment_ids
        if len(attachments) < 1:
            res = False
        elif len(attachments) == 1:
            res = attachments.datas
        else:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                for att in attachments:
                    zip_file.writestr(att.name, base64.b64decode(att.datas))
            res = base64.b64encode(zip_buffer.getvalue())
            zip_buffer.close()
        self.attachment_data = res

    @api.one
    def _get_attachment_fname(self):
        attachments = self.attachment_ids
        if len(attachments) < 1:
            res = ''
        elif len(attachments) == 1:
            res = attachments.name
        else:
            res = '{}.zip'.format(self.move_id.name)
        self.attachment_fname = res

    @api.multi
    def download_attachments(self):
        self.ensure_one()
        params = urllib.urlencode({
            'model': self._name, 'id': self.id, 'field': 'attachment_data',
            'filename_field': 'attachment_fname'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/saveas?{}'.format(params),
            'target': 'self',
        }

    @api.multi
    def unlink(self):
        self.mapped('move_line_id').write({'payment_batch_id': False})
        return super(PaymentBatchMoveLine, self).unlink()
