from odoo import fields, models, api
from datetime import datetime


class InheritedStockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def name_get(self):
        display_mrr_no = self.env.context.get('display_mrr_no')
        result = []
        if display_mrr_no:
            for rec in self:
                if rec.check_mrr_button and rec.mrr_no:
                    name = rec.mrr_no
                    result.append((rec.id, name))
                else:
                    result.append((rec.id, ''))
        else:
            for rec in self:
                result.append((rec.id, rec.name))
        return result

    @api.multi
    def button_approve(self):
        for picking in self:
            picking.approval_comment = 'Final Approval'
            picking.check_mrr_button = 'True'
            picking.mrr_status = 'waiting_bills'
            requested_date = datetime.today().date()
            new_seq = self.env['ir.sequence'].next_by_code_new('material.requisition', requested_date)
            if new_seq:
                picking.mrr_no = new_seq
                picking.mrr_date = datetime.today().date()

            # setting available quantity
            for move in picking.move_lines:
                move.sudo().write({'available_qty': move.product_qty})

