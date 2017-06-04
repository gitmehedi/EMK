from openerp import api, models, fields


class StockTransferRequest(models.Model):
    """
    Send product to other shop
    """
    _name = 'stock.transfer.request'
    _rec_name = "to_shop_id"

    barcode = fields.Char(string='Product Barcode', size=20)

    """ Relational Fields """
    product_line_ids = fields.One2many('stock.transfer.request.line', 'stock_transfer_id')
    to_shop_id = fields.Many2one('stock.location', string="To Shop", required=True, ondelete="cascade")
    requested_id = fields.Many2one('stock.location', string="Requested By", required=True, ondelete="cascade")

    """ States Fields """
    state = fields.Selection([('draft', "Draft"), ('submit', "Submit"), ('approve', "Approve"),
                              ('transfer', "Transfer"), ('receive', "Receive"), ('reject', "Reject")], default='draft')


    @api.onchange('barcode')
    def _onchange_barcode(self):
        if self.barcode:
            product = self.env['product.product'].search([('default_code', '=', self.barcode)])
            product_line_ids = self.product_line_ids
            if product:
                list = [p.product_id.id for p in product_line_ids]

                if product.id in list:
                    for k in product_line_ids:
                        quantity = k.quantity + 1 if product.id == k.product_id.id else k.quantity
                        k.update({'quantity': quantity})
                else:
                    product_line_ids += product_line_ids.new({
                        'product_id': product.id,
                        'quantity': 1
                    })
                    self.product_line_ids = product_line_ids
            self.barcode = None

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
    def action_transfer(self):

        move_obj = self.env['stock.move']

        pic_val = {
            'picking_type_id': 1,
            'priority': '1',
            'move_type': 'direct',
            'company_id': self.env.user['company_id'].id,
            'state': 'done',
            'invoice_state': 'none',
        }
        picking = self.env['stock.picking'].create(pic_val)

        for val in self.product_line_ids:
            if val:
                move = {}
                move['product_id'] =  val.product_id.id
                move['product_uom'] =  val.product_id.uom_id.id
                move['product_uos_qty'] =  val.quantity
                # move['product_qty'] =  val.quantity
                move['product_uom_qty'] =  val.quantity
                move['name'] =  val.product_id.name
                move['price_unit'] =  val.product_id.price
                move['invoice_state'] =  'invoiced'
                move['date_expected'] =  '2017/02/02'
                move['location_id'] =  self.to_shop_id.id
                move['location_dest_id'] =  self.requested_id.id
                move['procure_method'] =  "make_to_stock"
                move['state'] =  'done'
                move_obj.create(move)

        self.state = 'transfer'

    @api.one
    def action_receive(self):
        self.state = 'receive'

    @api.one
    def action_reject(self):
        self.state = 'reject'
