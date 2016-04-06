from openerp import models, fields, api, exceptions,modules

def _set_default_currency(name):
        # res = self.env['res.currency'].search([('name', '=like', name)])
        # return res and res[0] or False
        r = modules.registry.RegistryManager.get('demo9-test-2')
        cr = r.cursor()
        env = api.Environment(cr, 1, {})
        res =  env['res.currency'].search([('name', '=like', name)])
        return res and res[0] or False
