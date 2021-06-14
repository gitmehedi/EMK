# imports of odoo
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    production_continue = fields.Boolean('Continue Production', default=True)
    create_delete_move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_production_id', 'Raw Materials', oldname='move_lines',
        copy=False, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        domain=[('scrapped', '=', False)])

    @api.multi
    @api.depends('workorder_ids.state', 'move_finished_ids')
    def _get_produced_qty(self):
        """Override _get_produced_qty to update the value of check_to_done field"""
        res = super(MrpProduction, self)._get_produced_qty()
        for production in self:
            if not production.production_continue and (production.state not in ('done', 'cancel')):
                production.check_to_done = True

        return res

    @api.multi
    def _update_raw_move(self, bom_line, line_data):
        """Override _update_raw_move to insert the value of standard_qty field"""
        quantity = line_data['qty']
        self.ensure_one()
        move = self.move_raw_ids.filtered(
            lambda x: x.bom_line_id.id == bom_line.id and x.state not in ('done', 'cancel'))
        if move:
            if quantity > 0:
                move[0].write({'standard_qty': quantity, 'product_uom_qty': quantity})
            else:
                if move[0].quantity_done > 0:
                    raise UserError(_(
                        'Lines need to be deleted, but can not as you still have some quantities to consume in them. '))
                move[0].action_cancel()
                move[0].unlink()
            return move
        else:
            self._generate_raw_move(bom_line, line_data)

    @api.multi
    def button_mark_done(self):
        self.ensure_one()
        self.validate_actual_consumed()
        self.check_available_quantity()
        res = super(MrpProduction, self).button_mark_done()

        return res

    @api.model
    def create(self, vals):
        """Override to set the value of product_uom_id field"""
        if 'product_id' in vals:
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product.uom_id.id

        return super(MrpProduction, self).create(vals)

    @api.multi
    def write(self, vals):
        """Override to set the value of product_uom_id field"""
        if self.has_duplicate_products(vals):
            raise ValidationError(_("Contains duplicate products in Raw material(s) list."))

        # parent
        if 'product_id' in vals:
            product = self.env['product.product'].search([('id', '=', vals['product_id'])])
            vals['product_uom_id'] = product.uom_id.id

        # lines
        if 'create_delete_move_raw_ids' in vals:
            new_create_delete_move_raw_ids = []
            for raw_item in vals['create_delete_move_raw_ids']:
                # check for creation
                if raw_item[0] == 0:
                    self._create_raw_move(raw_item[2])

                # check for edit
                elif raw_item[0] == 1 and 'product_id' in raw_item[2]:
                    move = self.env['stock.move'].search([('id', '=', raw_item[1])])

                    if self.availability == 'assigned':
                        raise UserError(_("You cannot change the product of Raw Material(s) "
                                          "after performing 'Check availability'"))
                    if move.bom_line_id:
                        raise UserError(_("You cannot change the product of Raw Material(s) which are coming from BOM"))
                    else:
                        if 'product_uom' not in raw_item[2]:
                            product = self.env['product.product'].search([('id', '=', raw_item[2]['product_id'])])
                            raw_item[2].update({'product_uom': product.uom_id.id, 'price_unit': product.standard_price})

                        new_create_delete_move_raw_ids.append(raw_item)

                else:
                    new_create_delete_move_raw_ids.append(raw_item)

            vals['move_raw_ids'] = new_create_delete_move_raw_ids
            del vals['create_delete_move_raw_ids']

        return super(MrpProduction, self).write(vals)

    @api.multi
    def check_available_quantity(self):
        """check whether the quantity of raw material is available or not"""
        has_qty = True
        message = ""
        for move in self.move_raw_ids:
            stock_qty = move.availability + move.reserved_availability
            if stock_qty < move.product_qty:
                has_qty = False
                message += _('- Product Name: "%s" , Qty: %s \n') % (
                str(move.product_id.product_tmpl_id.name), (move.product_qty - stock_qty))

        if not has_qty:
            message += _('\nPlease contact with Inventory Department for that. '
                         'After that you can perform the production.')
            raise ValidationError(_('Unable to perform production.\n\n'
                                    'The mentioned product(s) qty are not available in current stock: \n') + message)

    @api.multi
    def validate_actual_consumed(self):
        if not any(move.quantity_done for move in self.move_raw_ids):
            raise ValidationError(_("The value of Actual Consumed of all Raw Material(s) cannot be 0 !!!"))

    def _generate_raw_move(self, bom_line, line_data):
        """Override _generate_raw_move to insert the value of standard_qty field"""
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom
        # and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']
        if self.routing_id:
            routing = self.routing_id
        else:
            routing = self.bom_id.routing_id
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.location_src_id
        original_quantity = (self.product_qty - self.qty_produced) or 1.0
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'product_id': bom_line.product_id.id,
            'standard_qty': quantity,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
        }
        return self.env['stock.move'].create(data)

    def _create_raw_move(self, vals):
        product = self.env['product.product'].search([('id', '=', vals['product_id'])])

        if self.routing_id and self.routing_id.location_id:
            source_location = self.routing_id.location_id
        else:
            source_location = self.location_src_id
        original_quantity = (self.product_qty - self.qty_produced) or 1.0
        data = {
            'sequence': vals['sequence'],
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'product_id': vals['product_id'],
            'standard_qty': 0,
            'product_uom_qty': vals['product_uom_qty'],
            'product_uom': product.uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'price_unit': product.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': vals['product_uom_qty'] / original_quantity,
        }

        move = self.env['stock.move'].create(data)
        move.action_confirm()

        return move

    def has_duplicate_products(self, vals):
        contains_duplicate_products = False
        if 'create_delete_move_raw_ids' in vals:
            product_ids = self.create_delete_move_raw_ids.mapped('product_id').ids
            product_ids += [rec[2]['product_id'] for rec in vals['create_delete_move_raw_ids'] if rec[2] and 'product_id' in rec[2]]
            if len(product_ids) != len(set(product_ids)):
                contains_duplicate_products = True

        return contains_duplicate_products
