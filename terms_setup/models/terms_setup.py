from odoo import fields, models, api,_

class TermsSetup(models.Model):
    _name = "terms.setup"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

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