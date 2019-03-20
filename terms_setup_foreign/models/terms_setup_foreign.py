from odoo import fields, models, api,_

class TermsSetupForeign(models.Model):
    _name = "terms.setup.foreign"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Terms Setup'

    days = fields.Integer(string='Days')
    name = fields.Char(string = 'Name',required=True,track_visibility='onchange')
    terms_condition = fields.Text(string='Terms & Conditions', required=True)


    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters = [['name','=ilike',self.name]]
            name = self.search(filters)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    terms_foreign_id = fields.Many2one('terms.setup.foreign', string='Terms', store=True, readonly=True,
                                       states={'draft': [('readonly', False)]})

    @api.onchange('terms_foreign_id')
    def onchange_terms_foreign_id(self):
        if self.terms_foreign_id:
            self.terms_condition = self.terms_foreign_id.terms_condition