from openerp import models, fields
from openerp import api, fields, models

class res_branch(models.Model):
    
    _name = 'res.branch'
    _description = 'Branches'
    
    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', 'Company', store=True, readonly=True, default=lambda self: self.env['res.company']._company_default_get('res.branch'))
    branch_manager = fields.Many2one("res.users", string='Branch Manager')
    
    
    @api.returns('self')
    def _branch_default_get(self, cr, uid, object=False, field=False, context=None):
        """
        Returns the default branch (the user's branch)
        The 'object' and 'field' arguments are ignored but left here for
        backward compatibility and potential override.
        """
        return self.pool['res.users']._get_branch(cr, uid, context=context)

    