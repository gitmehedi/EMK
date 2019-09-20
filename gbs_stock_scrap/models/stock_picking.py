from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_see_move_scrap(self):
        self.ensure_one()
        action = self.env.ref('gbs_stock_scrap.action_gbs_stock_scrap').read()[0]
        scraps = self.env['gbs.stock.scrap'].search([('picking_id', '=', self.id)])
        action['domain'] = [('id', 'in', scraps.ids)]
        return action