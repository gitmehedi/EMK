from odoo import api, models, fields

class LetterOfCredits(models.TransientModel):
    _name ='letter.credit.wizard'
    _description = 'LC Wizard'

    lc_no = fields.Many2one('letter.credit', string='Select LC No.', required=True)

    @api.multi
    def compute_lc_no(self):
        do_pool = self.env['delivery.order'].browse([self._context['active_id']])
        if do_pool:
            do_pool.write({'lc_no':self.lc_no.id})

        """ Update LC field to keep track of 100MT condition"""
        ordered_qty_pool = self.env['ordered.qty'].search([('product_id','=', do_pool.id)])
        if ordered_qty_pool:
            ordered_qty_pool.write({'lc_no': self.lc_no.id})


