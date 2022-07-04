from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class PickingImportWizard(models.TransientModel):
    _inherit = "picking.import.wizard"

    @api.model
    def default_get(self, field_list):
        """Get pickings previously imported."""
        res = super(PickingImportWizard, self).default_get(field_list)
        exclude_used_mrr = self.env['ir.values'].get_default('account.config.settings', 'exclude_used_mrr')

        if self.env.context.get('active_id') and 'prev_pickings' in field_list:
            distribution = self.env['purchase.cost.distribution'].browse(
                self.env.context['active_id'])
            pickings = self.env['stock.picking']
            moves = distribution.mapped('cost_lines.move_id')
            for line in distribution.cost_lines:
                if line.picking_id in pickings:
                    continue
                if all(x in moves for x in line.picking_id.move_lines):
                    pickings |= line.picking_id
            res['prev_pickings'] = [(6, 0, pickings.ids)]

            if not exclude_used_mrr:
                res['prev_pickings'] = False

        return res

    def _get_default_operating_unit_id(self):
        if self.env.context.get('active_id'):
            distribution = self.env['purchase.cost.distribution'].browse(self.env.context['active_id'])
            return distribution.operating_unit_id.id

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=_get_default_operating_unit_id)

    @api.depends('lc_id')
    def _journal_entry_created(self):
        for rec in self:
            if rec.lc_id:
                rec.journal_entry_created = True
                purchase_cost_dist_obj = self.env['purchase.cost.distribution'].sudo().search(
                    [('lc_id', '=', rec.lc_id.id)])
                if purchase_cost_dist_obj:
                    for cost_dist in purchase_cost_dist_obj:
                        if cost_dist.id != self.env.context['active_id']:
                            if cost_dist.account_move_id:
                                rec.journal_entry_created = True
                            else:
                                rec.journal_entry_created = False
                        else:
                            rec.journal_entry_created = True

    journal_entry_created = fields.Boolean(compute='_journal_entry_created')

    @api.depends('lc_id')
    def _prev_pickings_from_landed_cost(self):
        for rec in self:
            other_distribution = self.env['purchase.cost.distribution'].search(
                [('lc_id', '=', rec.lc_id.id)])
            moves = other_distribution.mapped('cost_lines.move_id')
            _pickings = self.env['stock.picking']
            for dis in other_distribution:
                for _line in dis.cost_lines:
                    if _line.picking_id in _pickings:
                        continue
                    if all(x in moves for x in _line.picking_id.move_lines):
                        _pickings |= _line.picking_id
            rec.prev_pickings_from_landed_cost = _pickings.ids
            exclude_used_mrr = self.env['ir.values'].get_default('account.config.settings', 'exclude_used_mrr')

            if not exclude_used_mrr:
                rec.prev_pickings_from_landed_cost = False

    prev_pickings_from_landed_cost = fields.Many2many(comodel_name='stock.picking',
                                                      compute='_prev_pickings_from_landed_cost')

    def _prepare_distribution_line(self, move):
        return {
            'distribution': self.env.context['active_id'],
            'move_id': move.id,
            'prev_product_price_unit': move.price_unit
        }

    @api.multi
    @api.onchange('lc_id')
    def onchange_lc_pickings(self):
        exclude_used_mrr = self.env['ir.values'].get_default('account.config.settings', 'exclude_used_mrr')

        if self.env.context.get('active_id'):
            distribution = self.env['purchase.cost.distribution'].browse(
                self.env.context['active_id'])
            pickings = self.env['stock.picking']
            moves = distribution.mapped('cost_lines.move_id')
            for line in distribution.cost_lines:
                if line.picking_id in pickings:
                    continue
                if all(x in moves for x in line.picking_id.move_lines):
                    pickings |= line.picking_id
            prev_pickings = pickings.ids

            other_distribution = self.env['purchase.cost.distribution'].search(
                [('lc_id', '=', self.lc_id.id), ('id', '!=', distribution.id)])
            _moves = []
            for dist in other_distribution:
                if dist.cost_lines:
                    for cost_line in dist.cost_lines:
                        _moves.append(cost_line.move_id)
            _pickings = self.env['stock.picking']
            for dis in other_distribution:
                for _line in dis.cost_lines:
                    if _line.picking_id in _pickings:
                        continue
                    if all(x in _moves for x in _line.picking_id.move_lines):
                        _pickings |= _line.picking_id
            prev_pickings_from_landed_cost = _pickings.ids
            if not exclude_used_mrr:
                prev_pickings = []
                prev_pickings_from_landed_cost = []
            stock_picking_obj = self.env['stock.picking'].search([('check_mrr_button', '=', True),
                                                                  ('state', '=', 'done'),
                                                                  ('origin', '=', self.lc_name),
                                                                  ('id', 'not in', prev_pickings),
                                                                  ('id', 'not in', prev_pickings_from_landed_cost)
                                                                  ])

        if stock_picking_obj:
            self.pickings = stock_picking_obj.ids
        else:
            self.pickings = False

    pickings = fields.Many2many(
        comodel_name='stock.picking',
        relation='distribution_import_picking_rel', column1='wizard_id',
        column2='picking_id', string='Incoming shipments', required=True)

    @api.multi
    def action_import_picking(self):
        exclude_used_mrr = self.env['ir.values'].get_default('account.config.settings', 'exclude_used_mrr')

        self.ensure_one()
        distribution = self.env['purchase.cost.distribution'].browse(
            self.env.context['active_id'])
        previous_moves = distribution.mapped('cost_lines.move_id')

        if distribution:
            distribution.write({'lc_id': self.lc_id.id})

        if self.env.context.get('active_id'):
            distribution = self.env['purchase.cost.distribution'].browse(
                self.env.context['active_id'])
            pickings = self.env['stock.picking']
            moves = distribution.mapped('cost_lines.move_id')
            for line in distribution.cost_lines:
                if line.picking_id in pickings:
                    continue
                if all(x in moves for x in line.picking_id.move_lines):
                    pickings |= line.picking_id
            prev_pickings = pickings.ids

            other_distribution = self.env['purchase.cost.distribution'].search(
                [('lc_id', '=', self.lc_id.id), ('id', '!=', distribution.id)])
            _moves = []
            for dist in other_distribution:
                if dist.cost_lines:
                    for cost_line in dist.cost_lines:
                        _moves.append(cost_line.move_id)

            _pickings = self.env['stock.picking']
            for dis in other_distribution:
                for _line in dis.cost_lines:
                    if _line.picking_id in _pickings:
                        continue
                    if all(x in _moves for x in _line.picking_id.move_lines):
                        _pickings |= _line.picking_id
            prev_pickings_from_landed_cost = _pickings.ids

            if not exclude_used_mrr:
                prev_pickings = []
                prev_pickings_from_landed_cost = []
        stock_picking_obj = self.env['stock.picking'].search([('check_mrr_button', '=', True),
                                                              ('state', '=', 'done'),
                                                              ('origin', '=', self.lc_name),
                                                              ('id', 'not in', prev_pickings),
                                                              ('id', 'not in', prev_pickings_from_landed_cost)
                                                              ])

        if not stock_picking_obj:
            raise UserError("Stock not found for this LC")
        else:
            for pickin in stock_picking_obj:
                for move in pickin.move_lines:
                    if move not in previous_moves:
                        self.env['purchase.cost.distribution.line'].create(
                            self._prepare_distribution_line(move))
