from odoo import api, fields, models

class StockMove(models.Model):

    _inherit = 'stock.move'

    indent_id = fields.Many2one('indent.indent', 'Indent')
    indentor_id = fields.Many2one('res.users', string='Indentor', related='indent_id.indentor_id', store=True)
    department_id = fields.Many2one('stock.location', string='Department')
    indent_date = fields.Datetime(string='Indent Date', related='indent_id.indent_date', readonly=True, store=True)