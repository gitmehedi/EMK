from odoo import fields, models, api

class LcRegisterWizard(models.Model):
    _name = 'lc.register.wizard'

    filter_by = fields.Selection([('goods_delivered_doc_not_prepared', 'Goods Delivered but doc. not prepared'),
                                  ('first_acceptance', '1\'st Acceptance'), ('second_acceptance', '2nd Acceptance'),
                                  ('maturated_but_amount_not_collect', 'Matured but Amount not collected'),
                                  ('goods_delivered_but_lc_not_received', 'Goods Delivered but LC not received')])
    acceptance_default_value = fields.Char(string='Default')
    type = fields.Selection([('all', 'All'), ('local', 'Local'), ('foreign', 'Foreign')], default='all', required=True)
    is_type_hide = fields.Boolean(string='is type hide', default=False)

    @api.onchange('filter_by')
    def onchange_filter_by(self):
        if self.filter_by == 'first_acceptance':
            self.acceptance_default_value = 20
        elif self.filter_by == 'second_acceptance':
            self.acceptance_default_value = 7
        else:
            self.acceptance_default_value = 0

    def report_print(self):
        self.ensure_one()
        return self.env['report'].get_action(self, 'lc_sales_local_report.lc_register_report')