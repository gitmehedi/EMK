from odoo import fields, models, api


class CustomerGeneralLedgerWizard(models.TransientModel):
    _name = "customer.general.ledger.wizard"

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
                                        ('not_zero', 'With balance is not equal to 0'), ],
                                       string='Display Accounts', required=True, default='movement')
    hide_field = fields.Boolean(string='Hide')

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='gbs_customer_general_ledger.customer_general_ledger_xlsx')

    @api.multi
    def button_print_pdf(self):
        data = dict()
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        return self.env['report'].get_action(self, 'gbs_customer_general_ledger.customer_general_ledger_pdf', data=data)