from odoo import api, fields, models, _



class AccountTax(models.Model):
    _name = 'account.tax'
    _order = 'name desc'
    _inherit = ['account.tax', 'mail.thread']


    mushok_amount = fields.Float(string='Mushok Value',track_visibility='onchange',
                                  help='For Mushok-6.3')
    vds_amount = fields.Float(string='VDS Authority Value', track_visibility='onchange',
                                 help='For VDS Authority ')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit',
                                        readonly=True,states={'draft': [('readonly', False)]})

    @api.constrains('mushok_amount', 'vds_amount')
    def _check_mushok_vds_amount(self):
        if self.mushok_amount and self.amount and self.mushok_amount > self.amount:
            raise Warning('Mushok Amount should be less then Rate Amount!')
        if self.vds_amount and self.amount and self.vds_amount >= self.amount:
            raise Warning('VDS Amount should be less then Rate Amount!')

