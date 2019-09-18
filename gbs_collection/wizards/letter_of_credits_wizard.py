from odoo import api, models, fields


class LetterOfCredits(models.TransientModel):
    _name = 'letter.credit.wizard'
    _description = 'LC Wizard'

    lc_id = fields.Many2one('letter.credit', string='Select LC No.', required=True)


    # @api.multi
    # def compute_lc_no(self):
    #
    #     do_pool = self.env['delivery.authorization'].browse([self._context['active_id']])
    #     if do_pool:
    #         do_pool.write({'lc_id': self.lc_id.id})
    #
    #     """ Update LC field to keep track of 100MT condition"""
    #     ordered_qty_pool = self.env['ordered.qty'].search([('delivery_auth_no', '=', do_pool.id)])
    #     if ordered_qty_pool:
    #         ordered_qty_pool.write({'lc_id': self.lc_id.id})
    #
    #
    #     ## Update LC No & PI No to Sale Order Obj
    #     if do_pool.so_type == 'lc_sales':
    #         do_pool.sale_order_id.write({'lc_id': self.lc_id.id, 'pi_id': do_pool.pi_id.id})
    #
    #         ## Update LC No to Stock Picking Obj
    #         stock_picking_id = do_pool.sale_order_id.picking_ids
    #         stock_picking_id.write({'lc_id':self.lc_id.id})