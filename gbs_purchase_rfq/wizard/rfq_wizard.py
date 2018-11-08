from odoo import api, fields, models, _



class RFQWizard(models.TransientModel):
    _name = 'rfq.wizard'

    product_lines = fields.One2many('rfq.product.line.wizard', 'rfq_id', string='Product(s)')

    pr_ids = fields.Many2many('purchase.requisition', string='PR',
                                  default=lambda self: self.env.context.get('active_ids'))

    @api.onchange('pr_ids')
    def _onchange_pr_ids(self):
        if self.pr_ids:
            vals = []
            # form_ids = self.env.context.get('active_ids')
            line_pool = self.env['purchase.requisition.line'].search([('requisition_id', 'in', self.pr_ids.ids)])
            for obj in line_pool:
                # product_qty = obj.product_qty - obj.product_received_qty
                # if product_qty > 0:
                vals.append((0, 0, {'product_id': obj.product_id,
                                    'product_qty': obj.product_ordered_qty,
                                    'product_uom_id': obj.product_uom_id.id,
                                    'price_unit': obj.price_unit,
                                    }))
            self.product_lines = vals
        else:
            self.product_lines = []

    @api.multi
    def confirm_for_mail(self):
        res = self.env.ref('gbs_purchase_rfq.rfq_email_template_wizard')

        vals = []
        for obj in self.product_lines:
            vals.append(({'product_id': obj.product_id.name,
                          'product_qty': obj.product_qty,
                          'product_uom_id': obj.product_uom_id.name,
                          }))

        result = {
            'name': _('Send RFQ'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res and res.id or False,
            'res_model': 'rfq.email.template.wizard',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'context': {
                        'vals': vals,
                        },
        }

        return result

    @api.multi
    def print_rfq(self):
        data = {}
        vals = []
        for obj in self.product_lines:
            vals.append(({  'product_id': obj.product_id.name,
                            'product_qty': obj.product_qty,
                            'product_uom_id': obj.product_uom_id.name,
                        }))
        data['vals'] = vals

        return self.env['report'].get_action(self, 'gbs_purchase_rfq.rfq_report', data=data)


class RFQProductLineWizard(models.TransientModel):
    _name = 'rfq.product.line.wizard'

    rfq_id = fields.Many2one('rfq.wizard', string='RFQ', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True, ondelete='cascade')
    product_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')
    product_uom_id = fields.Many2one('product.uom', string='Unit of Measure')
