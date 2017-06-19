from openerp import models, fields, api


class InheritedPointOfSale(models.Model):
    _inherit = 'pos.order'

    """ Relational Fields"""

    @api.model
    def _default_operating_unit(self):
        team = self.env['res.user']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id
        else:
            return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=_default_operating_unit
    )


class InheritedPosOrder(models.Model):
    _inherit = 'pos.order'


    """ Relational Fields"""

    @api.model
    def _default_operating_unit(self):
        user = self.env['res.user']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id
        else:
            return self.env.user.default_operating_unit_id

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=_default_operating_unit
    )



