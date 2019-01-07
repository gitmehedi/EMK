from odoo import fields, models, api,_

class InheritResUsers(models.Model):
    _name = "res.users"
    _inherit = ['res.users', 'mail.thread', 'ir.needaction_mixin']

    @api.model
    def operating_unit_default_get(self, uid2):
        if not uid2:
            uid2 = self._uid
        user = self.env['res.users'].browse(uid2)
        return user.default_operating_unit_id

    @api.model
    def _get_operating_unit(self):
        return self.operating_unit_default_get(self._uid)

    @api.model
    def _get_operating_units(self):
        return self._get_operating_unit()

    operating_unit_ids = fields.Many2many('operating.unit',
                                          'operating_unit_users_rel',
                                          'user_id', 'poid', 'Operating Units', track_visibility='onchange',
                                          default=_get_operating_units)
    default_operating_unit_id = fields.Many2one('operating.unit',
                                                'Default Operating Unit',track_visibility='onchange',
                                                default=_get_operating_unit)

    name = fields.Char(related='partner_id.name', inherited=True,track_visibility='onchange')
    login = fields.Char(required=True, help="Used to log into the system",track_visibility='onchange')

class InheritResUsersRole(models.Model):
    _name = "res.users.role"
    _inherit = ['res.users.role', 'mail.thread', 'ir.needaction_mixin']
    _order = "seq asc"

    seq = fields.Integer(string='Sequence', required=True)
    implied_ids = fields.Many2many('res.groups', 'res_groups_implied_rel', 'gid', 'hid', track_visibility='onchange',
                                   string='Inherits', help='Users of this group automatically inherit those groups')
    group_id = fields.Many2one(
        'res.groups', required=True, ondelete='cascade',track_visibility='onchange',
        readonly=True, string=u"Associated group")
    internal_user_group= fields.Boolean('Internal User Group',default=False,)

    line_ids = fields.One2many(
        'res.users.role.line', 'role_id',track_visibility='onchange', string=u"Users")

