from odoo import models, fields, api, _


class StockDateOfTransfer(models.TransientModel):
    _name = 'stock.date.transfer'

    pick_id = fields.Many2one('stock.picking')
    date_done = fields.Datetime('Date of Transfer', default=fields.Datetime.now, help="Completion Date of Transfer")

    @api.model
    def default_get(self, fields):
        res = super(StockDateOfTransfer, self).default_get(fields)
        if not res.get('pick_id') and self._context.get('active_id'):
            res['pick_id'] = self._context['active_id']
        return res

    @api.multi
    def save(self):
        self.ensure_one()
        self.pick_id.write({'date_done': self.date_done})
        return self.pick_id.with_context(set_date_of_transfer=True).do_new_transfer()
