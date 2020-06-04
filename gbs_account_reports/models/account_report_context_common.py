from odoo import models, fields, api, _


class AccountFinancialReportContext(models.TransientModel):
    _inherit = "account.financial.html.report.context"

    @api.model
    def _default_operating_unit_ids(self):
        unit_ids = self.env['operating.unit'].search([])
        return unit_ids

    operating_unit_ids = fields.Many2many('operating.unit', default=lambda s: s._default_operating_unit_ids())
    available_operating_unit_ids = fields.Many2many('operating.unit', compute='_compute_available_operating_unit_ids')

    @api.multi
    def _compute_available_operating_unit_ids(self):
        self.available_operating_unit_ids = self.env['operating.unit'].search([])

    @api.multi
    def get_available_operating_unit_ids_and_names(self):
        return [[c.id, c.name] for c in self.available_operating_unit_ids]


class AccountReportContextCommon(models.TransientModel):
    _inherit = 'account.report.context.common'

    @api.multi
    def get_html_and_data(self, given_context=None):
        result = super(AccountReportContextCommon, self).get_html_and_data(given_context)
        select = ['operating_unit_ids']
        result['report_context'].update(self.read(select)[0])
        result['report_context']['available_operating_units'] = self.get_available_operating_unit_ids_and_names() if hasattr(self, 'get_available_operating_unit_ids_and_names') else False
        return result
