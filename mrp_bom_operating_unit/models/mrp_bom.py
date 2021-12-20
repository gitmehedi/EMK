# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='BOM Number', readonly=True, default='/')
    operating_unit_id = fields.Many2one('operating.unit', string='Operating Unit', readonly=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    @api.multi
    def action_confirm(self):
        bom = self.env['mrp.bom'].search([('product_id', '=', self.product_id.id),
                                          ('operating_unit_id', '=', self.operating_unit_id.id),
                                          ('state', '=', 'confirmed'),
                                          ('active', '=', True)])
        if bom.ids:
            raise Warning(_('Already BOM of "%s" exists for "%s".\n'
                            'You are only allowed to create new version of "%s".')
                          % (self.product_id.name, self.operating_unit_id.name, self.product_id.name))

        if self.version > 0:
            self.write({'state': 'confirmed'})
        else:
            new_name = self.env['ir.sequence'].next_by_code_new('mrp.bom', None, self.operating_unit_id)
            self.write({
                'name': new_name,
                'base_name': new_name,
                'state': 'confirmed'
            })

    @api.model
    def _bom_find(self, product_tmpl=None, product=None, picking_type=None, company_id=False, operating_unit_id=None):
        """ Finds BoM for particular product, picking and company """
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = ['&', ('state', '=', 'confirmed'), '|', ('product_id', '=', product.id), '&',
                      ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + [('company_id', '=', company_id or self.env.context.get('company_id'))]
        if operating_unit_id:
            domain = domain + [('operating_unit_id', '=', operating_unit_id)]
        # order to prioritize bom with product_id over the one without
        return self.search(domain, order='sequence, product_id', limit=1)
