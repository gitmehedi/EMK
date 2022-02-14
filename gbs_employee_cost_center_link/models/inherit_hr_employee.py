from odoo import fields, models, api


class InheritedHrEmployee(models.Model):
    _inherit = 'hr.employee'

    # cost_center required if operating unit cost center configured required true
    @api.multi
    @api.depends('operating_unit_id')
    def compute_cost_center_required(self):
        for rec in self:
            if rec.operating_unit_id:
                if rec.operating_unit_id.cost_center_required:
                    rec.cost_center_required = True
                else:
                    rec.cost_center_required = False
            else:
                rec.cost_center_required = False

    cost_center_required = fields.Boolean(compute='compute_cost_center_required')

    # depends on operating_unit and company
    # cost_center load depending on company
    cost_center_id = fields.Many2one('account.cost.center', string="Cost Center", track_visibility='always')
