# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])]
            , limit=1).id

    code = fields.Char(readonly=True, states={'draft': [('readonly', False)]})
    type = fields.Selection(readonly=True, states={'draft': [('readonly', False)]})
    product_tmpl_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]})
    bom_line_ids = fields.One2many(readonly=True, states={'draft': [('readonly', False)]})
    product_qty = fields.Float(readonly=True, states={'draft': [('readonly', False)]})
    product_uom_id = fields.Many2one(readonly=True)
    sequence = fields.Integer(readonly=True, states={'draft': [('readonly', False)]})
    routing_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]})
    ready_to_produce = fields.Selection(readonly=True, states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one(default=_get_default_picking_type, readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one(readonly=True, states={'draft': [('readonly', False)]})

    name = fields.Char(string='BOM Number', readonly=True, default='/')
    active = fields.Boolean(string='Active', default=True, copy=True, readonly=True, track_visibility='onchange')
    historical_date = fields.Date(string='Historical Date', readonly=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('historical', 'Historical')
    ], string='State', readonly=True, default='draft', track_visibility='onchange')

    version = fields.Integer(readonly=True, copy=False, default=0)
    base_name = fields.Char(string='BOM Reference', readonly=True)
    parent_bom_id = fields.Many2one('mrp.bom', string='Parent BoM', copy=True, ondelete='cascade')
    old_version_ids = fields.One2many('mrp.bom', 'parent_bom_id', string='Old Versions', readonly=True, context={'active_test': False})

    @api.multi
    def action_confirm(self):
        if self.version > 0:
            self.write({'state': 'confirmed'})
        else:
            name = self.env['ir.sequence'].next_by_code('mrp.bom') or _('New')
            self.write({
                'name': name,
                'base_name': name,
                'state': 'confirmed'
            })

    @api.multi
    def action_new_version(self):
        self.ensure_one()
        view = self.env.ref('mrp_bom_version.mrp_bom_version_form_view')
        bom = self.with_context(new_bom_version=True).copy()

        if self.old_version_ids.ids:
            for old in self.old_version_ids:
                old.write({'parent_bom_id': bom.id})

        self.write({
            'parent_bom_id': bom.id,
            'active': False,
            'state': 'historical',
            'historical_date': fields.Date.today()
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('BOM'),
            'res_model': 'mrp.bom',
            'res_id': bom.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'target': 'current',
            'nodestroy': True,
            'flags': {'initial_mode': 'edit'},
        }

    @api.multi
    def copy(self, defaults=None):
        if self.env.context.get('new_bom_version'):
            defaults = {}
            version = self.version
            defaults.update({
                'name': '%s-%02d' % (self.base_name, version + 1),
                'version': version + 1,
            })

        return super(MrpBom, self).copy(defaults)

    @api.model
    def create(self, vals):
        if self.has_duplicate_products(vals):
            raise ValidationError(_("Contains duplicate products in Raw material(s) list."))

        if 'product_tmpl_id' in vals:
            product_template = self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])])
            vals['product_uom_id'] = product_template.uom_id.id

        return super(MrpBom, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.has_duplicate_products(vals):
            raise ValidationError(_("Contains duplicate products in Raw material(s) list."))

        if 'product_tmpl_id' in vals:
            product_template = self.env['product.template'].search([('id', '=', vals['product_tmpl_id'])])
            vals['product_uom_id'] = product_template.uom_id.id

        return super(MrpBom, self).write(vals)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise Warning(_('You cannot delete a record which is not in draft state!'))

            manufacturing_orders = self.env['mrp.production'].search([('bom_id', 'in', rec.old_version_ids.ids)])
            if len(manufacturing_orders) > 0:
                raise Warning(_('You cannot delete a record which is used in Manufacturing Orders!'))

        return super(MrpBom, self).unlink()

    def has_duplicate_products(self, vals):
        contains_duplicate_products = False
        if 'bom_line_ids' in vals:
            product_ids = [rec[2]['product_id'] for rec in vals['bom_line_ids'] if rec[2] and 'product_id' in rec[2]]
            if not self.env.context.get('new_bom_version'):
                product_ids += self.bom_line_ids.mapped('product_id').ids
            if len(product_ids) != len(set(product_ids)):
                contains_duplicate_products = True

        return contains_duplicate_products


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    @api.model
    def create(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product.product_tmpl_id.uom_id.id

        return super(MrpBomLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'product_id' in vals:
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product.product_tmpl_id.uom_id.id

        return super(MrpBomLine, self).write(vals)
