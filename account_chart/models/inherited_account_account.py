from openerp import models, fields, api, exceptions
from openerp.addons.helper import validator



class InheritedAccountAccount(models.Model):
    _inherit = 'account.account'

    # Many2one relationship
    parent_id = fields.Many2one('account.account', string="Parent")

    child_ids = fields.One2many('account.account', 'parent_id')


    # parent_ids = fields.One2many('account.account', 'parent_id', string="Parent", readonly=True)