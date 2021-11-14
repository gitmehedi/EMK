from odoo import fields, models, api


class InheritedAccountMove(models.Model):
    _inherit = 'account.move'
    _description = 'Description'

    payslip_run_id = fields.Many2one('hr.payslip.run', readonly=True, string='Payslip Run')
