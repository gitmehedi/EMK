from odoo import fields, models, api, _


class InheritedPurchaseConfigSettings(models.TransientModel):
    _inherit = 'purchase.config.settings'

    mrr_bill_automation_date = fields.Date(string='MRR Bill Automation Date')

    @api.multi
    def set_mrr_bill_automation_date(self):
        if self.mrr_bill_automation_date != self.company_id.mrr_bill_automation_date:
            self.company_id.write({'mrr_bill_automation_date': self.mrr_bill_automation_date})
        return self.env['ir.values'].sudo().set_default(
            'purchase.config.settings', 'mrr_bill_automation_date', self.mrr_bill_automation_date)


class ResCompany(models.Model):
    _inherit = "res.company"

    mrr_bill_automation_date = fields.Date(string='MRR Bill Automation Date')
