from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import datetime

class LcRegisterWizard(models.Model):
    _name = 'lc.register.wizard'

    filter_by = fields.Selection([('goods_delivered_doc_not_prepared', 'Goods Delivered but doc. not prepared'),
                                  ('first_acceptance', '1st Acceptance'), ('second_acceptance', '2nd Acceptance'),
                                  ('maturated_but_amount_not_collect', 'Matured but Amount not collected'),
                                  ('goods_delivered_but_lc_not_received', 'Goods Delivered but LC not received'),
                                  ('percentage_of_first_acceptance_collection', 'Percentage of 1st acceptance collection'),
                                  ('lc_history', 'LC History'), ('lc_number', 'LC Number')], required=True)
    lc_number = fields.Many2one('letter.credit', string='LC Number', domain=[('name', '!=', ''), ('state', '!=', 'cancel')])
    acceptance_default_value = fields.Char(string='Default')
    type = fields.Selection([('all', 'All'), ('local', 'Local'), ('foreign', 'Foreign')], default='all', required=True)
    date_from = fields.Date(string='From', default=fields.Datetime.now)
    date_to = fields.Date(string='To', default=fields.Datetime.now)
    is_type_hide = fields.Boolean(string='is type hide', default=False)

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        if self.filter_by == 'first_acceptance':
            self.acceptance_default_value = 20
        elif self.filter_by == 'second_acceptance':
            self.acceptance_default_value = 7
        elif self.filter_by == 'percentage_of_first_acceptance_collection':
            self.acceptance_default_value = 20
        else:
            self.acceptance_default_value = 0

    def report_print(self):
        self.ensure_one()

        if self.filter_by == 'percentage_of_first_acceptance_collection' or self.filter_by == 'lc_history':
            if self.date_from > self.date_to:
                raise UserError('From date can\'t be greater than To date')

            ReportUtility = self.env['report.utility']
            date_to = datetime.strptime(ReportUtility.get_date_from_string(self.date_to), '%d-%m-%Y')
            date_from = datetime.strptime(ReportUtility.get_date_from_string(self.date_from), '%d-%m-%Y')
            diff_days = date_to - date_from
            if diff_days.days > 180:
                raise UserError('You can\'t generate report greater than 6 months')

        return self.env['report'].get_action(self, 'lc_sales_local_report.lc_register_report')