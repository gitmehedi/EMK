from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ItemLedgerReportWizard(models.TransientModel):
    _name = 'item.ledger.report.wizard'
    _description = 'Item Ledger Report'

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    def _get_operating_unit(self):
        domain = [("id", "in", self.env.user.operating_unit_ids.ids)]
        return domain

    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', required=True,
                                        domain=_get_operating_unit)
    category_id = fields.Many2one('product.category', string='Category', required=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)

    @api.multi
    def export_excel(self):
        return self.env['report'].get_action(self,
                                             report_name='item_ledger_report.item_ledger_report_xlsx')
