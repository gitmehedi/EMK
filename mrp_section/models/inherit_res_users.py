from odoo import fields, models, api,_

class InheritUsers(models.Model):
    _inherit = "res.users"

    section_ids = fields.Many2many( 'mrp.section','mrp_section_users_rel',
                                    'user_id', 'section_id', 'Allow Sections')

