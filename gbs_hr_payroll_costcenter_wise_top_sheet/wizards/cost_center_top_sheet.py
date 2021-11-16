from odoo import api, fields, models, _


class CostCenterTopSheet(models.TransientModel):
    _name = 'cost.center.top.sheet.wizard'
    _description = 'Cost Center Wise Top Sheet'

    @api.multi
    def _get_payslip_run(self):
        for rec in self:
            rec.hr_payslip_run_id = self.env['hr.payslip.run'].browse(self._context.get('active_id'))

    cost_center_ids = fields.Many2many('account.cost.center', string='Cost Center')
    hr_payslip_run_id = fields.Many2one('hr.payslip.run', compute='_get_payslip_run')

    @api.multi
    def button_export_xlsx(self):
        self.hr_payslip_run_id = self.env['hr.payslip.run'].browse(self._context.get('active_id'))
        return self.env['report'].get_action(self,
                                             report_name='gbs_hr_payroll_costcenter_wise_top_sheet.cost_center_wise_top_sheet_xlsx')
