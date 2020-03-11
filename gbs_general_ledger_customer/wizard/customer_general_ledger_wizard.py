from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


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

    @api.constrains('date_from', 'date_to')
    def _check_date_validation(self):
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        else:
            dr_obj = self.env['date.range'].search(
                [('type_id.fiscal_year', '=', True), ('date_start', '<=', self.date_from),
                 ('date_end', '>=', self.date_from)])
            if not dr_obj.date_start and not dr_obj.date_end:
                raise ValidationError(_("Date range of fiscal year does not exist."))

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        return self.env['report'].get_action(self, report_name='gbs_general_ledger_customer.customer_general_ledger_xlsx')

    @api.multi
    def button_print_pdf(self):
        data = dict()
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        return self.env['report'].get_action(self, 'gbs_general_ledger_customer.customer_general_ledger_pdf', data=data)