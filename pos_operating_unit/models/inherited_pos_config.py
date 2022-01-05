from odoo import models, fields, api


class InheritedPOSConfig(models.Model):
    _inherit = 'pos.config'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(comodel_name='operating.unit', string='Operating Unit',
                                        default=_default_operating_unit)


class InheritedPosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(comodel_name='operating.unit', string='Operating Unit',
                                        default=_default_operating_unit)


class InheritedPosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _company_default_get(self):
        if self.env.user.company_id:
            return self.env.user.company_id

    company_id = fields.Many2one('res.company', string='Company', default=_company_default_get)


    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(comodel_name='operating.unit', string='Operating Unit',
                                        default=_default_operating_unit)
