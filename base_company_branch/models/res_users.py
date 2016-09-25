from openerp import api, models, fields

class res_users(models.Model):
    
    _inherit = 'res.users'
    
    is_branch_user = fields.Boolean(string='Is Branch User?')
    branch_id = fields.Many2one("res.branch", string='Branch',
                                help='The company this user is currently working for.')
    branch_ids = fields.Many2many('res.branch', relation='res_branch_users_rel', 
                                  string='Allowed Branches')
    
    #def _get_branch(self,cr, uid, context=None, uid2=False):
    #    if not uid2:
    #        uid2 = uid
    #    user_data = self.pool['res.users'].read(cr, uid, uid2, ['branch_id'],
    #                                            context=context, load='_classic_write')
    #    comp_id = user_data['branch_id']
    #    return comp_id or False
    
    @api.model
    def get_default_branch(self):
        user = self.search(['id','=',self.id])
        if user.branch_id:
            return user.branch_id.id
        else:
            branch_pool = self.env['res.branch']
            branch_ids = branch_pool.search([('company_id', '=', company_id)])
            #print branch_ids[0]
            return branch_ids[0]