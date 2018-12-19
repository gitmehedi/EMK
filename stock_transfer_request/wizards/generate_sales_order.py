from openerp import api, exceptions, fields, models


class GenerateSalesOrderWizard(models.TransientModel):
    _name = 'generate.sales.order.wizard'

    append_sale = fields.Selection([("new", "Create New Sales Order"), ("old", "Add To Existing Sales Order")],
                                   string='Sales Order Type', required=True, default='new')
    sales_order_id = fields.Many2one('sale.order', string='Sales Order', domain=[('state', '=', 'draft')])
    customer_id = fields.Many2one('res.partner', string='Customer', domain=[('customer', '=', True)], required=True)

    @api.multi
    def generate_sales_order(self, data):
        transfer = self.env[data['active_model']].search([('id', '=', data['active_id'])])
        if 'state' in transfer and transfer.state == 'receive':
            sale_order = {
                'partner_id': self.customer_id.id,
                'order_line': []
            }
            order_line = []
            for rec in transfer.product_line_ids:
                line = {'name': transfer.name,
                        'product_id': rec.product_id.id,
                        'product_uom_qty': rec.receive_quantity,
                        'product_uom': rec.product_id.uom_id.id,
                        'price_unit': rec.product_id.uom_id.id,
                        }
                order_line.append((0, 0, line))

                if self.append_sale == 'old':
                    line['order_id'] = self.sales_order_id.id
                    self.sales_order_id.order_line.create(line)

            if self.append_sale == 'new':
                sale_order['order_line'] = order_line
                self.env['sale.order'].create(sale_order)

            transfer.write({'state': 'sold'})
