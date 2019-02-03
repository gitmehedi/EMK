from odoo import models, fields, api, _

class AcquiringChannel(models.Model):
    _name = 'acquiring.channel'
    _inherit = ['mail.thread']
    _order = 'code asc'
    _description = 'Acquiring Channel'

    name = fields.Char('Name', required=True, track_visibility='onchange')
    code = fields.Char('Code', required=True, size=2, track_visibility='onchange')
    active = fields.Boolean('Active', default=True, track_visibility='onchange')

    @api.constrains('name', 'code')
    def _check_unique_constrain(self):
        if self.name or self.code:
            filters_name = [['name', '=ilike', self.name]]
            filters_code = [['code', '=ilike', self.code]]
            name = self.search(filters_name)
            code = self.search(filters_code)
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')
            elif len(code) > 1:
                raise Warning('[Unique Error] Code must be unique!')
