from odoo import fields, models, api


class InheritedReconciliationModel(models.Model):
    _inherit = "account.reconcile.model"

    second_department_id = fields.Many2one('hr.department', string='Second Department Account', ondelete='set null')

    second_cost_center_id = fields.Many2one('account.cost.center', string='Second Cost Center Account', ondelete='set null')

    second_operating_unit_id = fields.Many2one('operating.unit', string='Second Operating Unit Account', ondelete='set null')
