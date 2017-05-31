from openerp import api, models, fields


class StockTransferRequest(models.Model):
    _name = 'stock.transfer.request'

    barcode = fields.Char(string='Product Barcode', size=20, required=True)

    """ Relational Fields """
    product_line_ids = fields.One2many('stock.transfer.request.line', 'stock_transfer_id')
    to_shop_id = fields.Many2one('stock.location', string="To Shop", required=True, ondelete="cascade")
    requested_id = fields.Many2one('res.partner', string="Requested By", required=True, ondelete="cascade")

    """ States Fields """
    state = fields.Selection([('draft', "Draft"),('submit', "Submit"), ('approve', "Approve"),
                              ('confirm', "Confirm"), ('reject', "Reject")], default='draft')


    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_submit(self):
        self.state = 'submit'

    @api.one
    def action_approve(self):
        self.state = 'approve'

    @api.one
    def action_confirm(self):
        self.state = 'confirm'

    @api.one
    def action_reject(self):
        self.state = 'reject'



