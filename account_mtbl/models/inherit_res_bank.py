from odoo import models, fields, api, _

class Banks(models.Model):
    _name = 'res.bank'
    _order = 'name desc'
    _inherit = ['res.bank','mail.thread']

    name = fields.Char(track_visibility='onchange')
    street = fields.Char(track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    zip = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state = fields.Many2one(track_visibility='onchange')
    country = fields.Many2one(track_visibility='onchange')
    email = fields.Char(track_visibility='onchange')
    phone = fields.Char(track_visibility='onchange')
    fax = fields.Char(track_visibility='onchange')
    active = fields.Boolean(track_visibility='onchange')
    bic = fields.Char(track_visibility='onchange')

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            filters_name = [['name', '=ilike', self.name]]
            name = self.search(filters_name)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

