# imports of python library
import datetime

# imports of odoo
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


class VendorGeneralLedgerWizard(models.TransientModel):
    _name = "vendor.general.ledger.wizard"

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
    def _check_date_range(self):
        dt_range = self.env['date.range'].search(
            [('type_id.fiscal_year', '=', True), ('date_start', '<=', self.date_from),
             ('date_end', '>=', self.date_from)])
        dt_from = datetime.datetime.strptime(self.date_from, '%Y-%m-%d')
        dt_to = datetime.datetime.strptime(self.date_to, '%Y-%m-%d')

        if dt_from.year != dt_to.year:
            raise ValidationError(_("Date From and Date To must be the same financial year."))
        if self.date_from > self.date_to:
            raise ValidationError(_("From date must be less then To date."))
        if not dt_range.date_start and not dt_range.date_end:
            raise ValidationError(_("Date range of fiscal year does not exist."))

    @api.multi
    def button_export_xlsx(self):
        self.ensure_one()
        # check whether the partner is a customer or not
        partner_id = self.env.context.get('active_id')
        partner = self.env['res.partner'].search([('id', '=', partner_id)])
        if not partner.supplier and not partner.is_cnf:
            raise UserError(_('You can only print General Ledger (Vendor) report for Vendor'))
        return self.env['report'].get_action(self, report_name='gbs_general_ledger_vendor.vendor_general_ledger_xlsx')

    @api.multi
    def button_print_pdf(self):
        data = dict()
        data['date_from'] = self.date_from
        data['date_to'] = self.date_to
        return self.env['report'].get_action(self, 'gbs_general_ledger_vendor.vendor_general_ledger_pdf', data=data)
