from odoo import models, fields, api,_


class AgreementWizard(models.TransientModel):
    _name = 'agreement.wizard'
    _order = 'name desc'
    _description = 'Vendor Agreement'

    name = fields.Char('Name',readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 default=lambda self: self.env.context.get('product_id'))
    start_date = fields.Date(string='Start Date', required=True,
                             default=lambda self: self.env.context.get('end_date'))
    end_date = fields.Date(string='End Date', required=True,
                           default=lambda self: self.env.context.get('end_date'))
    advance_amount = fields.Float(string="Advance Amount",
                                  default=lambda self: self.env.context.get('advance_amount'))
    adjusted_amount = fields.Float(string="Adjusted Amount",
                                   default=lambda self: self.env.context.get('adjusted_amount'))
    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True,
        default=lambda self: self.env.context.get('partner_id'))

    @api.multi
    def generate(self):
        agr_obj = self.env['agreement'].browse([self._context['active_id']])
        agr_obj.write({
            'partner_id': self.partner_id.id,
            'product_id': self.product_id.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'advance_amount': self.advance_amount,
            'adjusted_amount': self.adjusted_amount,
            'rel_id': self.id,
        })


