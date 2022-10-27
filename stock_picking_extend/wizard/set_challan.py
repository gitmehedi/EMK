from odoo import fields, models, api


class SetChallan(models.TransientModel):
    _name = 'set.challan'

    def set_challan(self,move_lines,challan_bill_no,challan_date):
        for move in move_lines:
            if challan_bill_no:
                move.sudo().write({'challan_bill_no': challan_bill_no})
                if move.move_dest_id:
                    move.move_dest_id.sudo().write({'challan_bill_no': challan_bill_no})
                    if move.move_dest_id.move_dest_id:
                        move.move_dest_id.move_dest_id.sudo().write({'challan_bill_no': challan_bill_no})
            if challan_date:
                move.sudo().write({'challan_date': challan_date})
                if move.move_dest_id:
                    move.move_dest_id.sudo().write({'challan_date': challan_date})
                    if move.move_dest_id.move_dest_id:
                        move.move_dest_id.move_dest_id.sudo().write({'challan_date': challan_date})

