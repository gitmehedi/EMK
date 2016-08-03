from collections import defaultdict

from openerp import models, fields, api, _, exceptions


class PaymentBatchSelection(models.TransientModel):
    _name = 'account.payment_batch.selection'

    date_maturity = fields.Date(
        string='Due date',
        help=(
            'Date based on which to filter accounting entries (we take '
            'entries with a due date <= the one entered here).'
        ),
        required=True,
    )

    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Payment Method',
        required=True,
        domain=[('type', 'in', ['bank', 'cash'])],
    )

    mode = fields.Selection(
        selection=[
            ('supplier_invoices', 'Supplier invoices'),
            ('client_refunds', 'Client refunds'),
            ('both', 'Both'),
        ],
        string='Mode',
        help='How to filter accounting entries.',
        required=True,
    )

    @api.model
    def get_preferred_bank_account_id(
        self, partner, entry, partner_bank_cache,
    ):
        """Get the preferred bank account of the specified partner, based on
        the specified accounting entry.

        Made to be overridden. The default implementation always returns the
        most recently modified bank of the partner, regardless of the
        accounting entry.

        :type partner: Odoo "res.partner record set.
        :type entry: Odoo "account.move.line" record set.
        :type partner_bank_cache: Dictionary partner ID -> bank ID.
        :return: Odoo "res.partner.bank" record ID.
        """

        partner_banks = partner_bank_cache.get(partner.id)

        if partner_banks is None:
            # First pass on this partner; save into the cache.
            partner_banks = partner_bank_cache[partner.id] = (
                self.env['res.partner.bank'].search(
                    [('partner_id', '=', partner.id)], order='write_date desc',
                    limit=1,
                ).id
            )

        # Use the cached bank.
        return partner_banks

    @api.multi
    def generate_batch(self):
        """Create a payment batch with accounting entries found based on the
        specified parameters.
        """

        self.ensure_one()

        # Gather the accounting entries to include:
        # - Filter by date.
        # - Filter by account type: all supplier lines, and client lines that
        # are for refunds.
        # - Not already included in a batch.
        # - Not marked with specific flags (made to delay payment).

        entry_search_domain = [  # noqa
            '|',
                ('reconcile_id', '=', False),
                ('reconcile_partial_id', '!=', False),
        ]

        if self.mode == 'supplier_invoices':
            entry_search_domain += [
                ('account_id.type', '=', 'payable'),
            ]

        elif self.mode == 'client_refunds':
            entry_search_domain += [
                ('account_id.type', '=', 'receivable'),
                ('move_id.journal_id.type', '=', 'sale_refund'),
            ]

        elif self.mode == 'both':
            entry_search_domain += [  # noqa
                '|',
                    ('account_id.type', '=', 'payable'),
                    '&',
                        ('account_id.type', '=', 'receivable'),
                        ('move_id.journal_id.type', '=', 'sale_refund'),
            ]

        entry_search_domain += [
            ('state', '=', 'valid'),
            ('move_id.state', '=', 'posted'),
            ('date_maturity', '<=', self.date_maturity),
            ('is_not_payment_batchable', '=', False),
            ('payment_batch_id', '=', False),
            ('is_in_voucher', '=', False),
        ]

        lines = self.env['account.move.line'].search(entry_search_domain)

        if not lines:
            raise exceptions.Warning('No lines found.')

        # Split lines by partner and by preferred bank account.
        batch_lines = defaultdict(dict)

        # Prepare a cache to avoid too many partner bank lookups.
        partner_bank_cache = {}

        for line in lines:
            partner = line.partner_id
            bank_id = self.get_preferred_bank_account_id(
                partner, line, partner_bank_cache,
            )
            subdict = batch_lines[(partner.id, bank_id)]
            subdict['bank_id'] = bank_id
            subdict['partner_id'] = partner.id
            subdict.setdefault('line_ids', []).append(line.id)

        # Create a payment batch
        pb = self.env['account.payment_batch'].create({
            'journal_id': self.journal_id.id,
            'line_ids': [
                (0, 0, {
                    'partner_id': line_data['partner_id'],
                    'line_ids': [
                        (0, 0, {'move_line_id': ml})
                        for ml in line_data['line_ids']
                    ],
                    'bank_id': line_data['bank_id'],
                })
                for line_data in batch_lines.itervalues()
            ],
            'date_maturity': self.date_maturity,
        })

        lines.write({'payment_batch_id': pb.id})

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment_batch',
            'name': _("Payment Batch"),
            'view_mode': 'form,tree',
            'view_type': 'form',
            'res_id': pb.id,
        }
