import time
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
import dateutil.parser
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class IndentIndent(models.Model):
    _name = 'indent.indent'
    _description = "Indent"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "id desc"

    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env.user.company_id.id
        warehouse_ids = warehouse_obj.sudo().search(
            [('company_id', '=', company_id), ('operating_unit_id', 'in', self.env.user.operating_unit_ids.ids)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    @api.model
    def _get_required_date(self):
        return datetime.strftime(datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    @api.multi
    def _default_department(self):
        emp_ins = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

        if not emp_ins.department_id:
            raise ValidationError(
                _("Please configure employee for user [{0}] from employee directory.".format(
                    self.env.user.display_name)))
        return emp_ins.department_id

    name = fields.Char('Reference #', size=30, readonly=True, track_visibility="onchange")
    approve_date = fields.Datetime('Approve Date', readonly=True, track_visibility="onchange")
    indent_date = fields.Datetime('Indent Date', required=True, readonly=True,
                                  default=fields.Datetime.now, track_visibility="onchange")
    required_date = fields.Date('Required Date', required=True, readonly=True, states={'draft': [('readonly', False)]},
                                default=lambda self: self._get_required_date(), track_visibility="onchange")
    indentor_id = fields.Many2one('res.users', string='Indentor', required=True, readonly=True,
                                  default=lambda self: self.env.user,
                                  states={'draft': [('readonly', False)]}, track_visibility="onchange")
    department_id = fields.Many2one('hr.department', string='Department', readonly=True, default=_default_department,
                                    track_visibility="onchange")
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', readonly=True, required=True,
                                        states={'draft': [('readonly', False)]},
                                        help="Default User Location.Destination location.",
                                        default=lambda self: self.env.user.default_location_id,
                                        track_visibility="onchange")

    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]},
                                          track_visibility="onchange")
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'Urgent')], 'Priority', readonly=True,
                                   default="1", required=True, states={'draft': [('readonly', False)]},
                                   track_visibility="onchange")
    indent_type = fields.Many2one('indent.type', string='Type', readonly=True, required=True,
                                  states={'draft': [('readonly', False)]}, track_visibility="onchange")
    product_lines = fields.One2many('indent.product.lines', 'indent_id', 'Products', readonly=True, required=True,
                                    states={'draft': [('readonly', False)],
                                            'waiting_approval': [('readonly', False)],
                                            'inprogress': [('readonly', False)]}, track_visibility="onchange")
    picking_id = fields.Many2one('stock.picking', 'Picking', track_visibility="onchange")
    in_picking_id = fields.Many2one('stock.picking', 'Picking', track_visibility="onchange")
    description = fields.Text('Additional Information', readonly=True, states={'draft': [('readonly', False)]},
                              track_visibility="onchange")
    material_required_for = fields.Text('Required For', readonly=True, states={'draft': [('readonly', False)]},
                                        track_visibility="onchange")
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id, required=True,
                                 track_visibility="onchange")
    active = fields.Boolean('Active', default=True, track_visibility="onchange")
    # amount_total = fields.Float(string='Total', compute=_compute_amount, store=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True,
                                  help="who have approve or reject indent.", track_visibility="onchange")
    closer_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have close indent.")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True, required=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="Default Warehouse.Source location.",
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                   track_visibility="onchange")
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type',
                                      compute='_compute_default_picking_type',
                                      readonly=True, store=True, track_visibility="onchange")
    move_type = fields.Selection([('one', 'All at once'),('direct', 'Partial')], 'Receive Method',
                                 readonly=True, required=True, default='one',
                                 states={'cancel': [('readonly', True)]},
                                 help="It specifies goods to be deliver partially or all at once",
                                 track_visibility="onchange")

    pr_indent_check = fields.Boolean(string='Indent List Check', default=True, track_visibility="onchange")


    product_id = fields.Many2one(
        'product.product', 'Products',
        readonly="False", related='product_lines.product_id',
        help="This comes from the product form.", track_visibility="onchange")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('received', 'Received'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    ####################################################
    # Business methods
    ####################################################

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            self.stock_location_id = self.warehouse_id.view_location_id.id

    @api.one
    @api.constrains('required_date')
    def _check_required_date(self):
        indent_date = dateutil.parser.parse(self.indent_date).date()
        required_date = dateutil.parser.parse(self.required_date).date()
        if required_date < indent_date:
            raise UserError('Required Date can not be less then indent date!!!')

    @api.multi
    @api.depends('warehouse_id', 'stock_location_id')
    def _compute_default_picking_type(self):
        for indent in self:
            picking_type_obj = indent.env['stock.picking.type']
            picking_type_ids = picking_type_obj.search(
                [('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),
                 ('default_location_dest_id', '=', indent.stock_location_id.id)])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False
            indent.picking_type_id = picking_type_id
            if picking_type_id:
                indent.picking_type_id = picking_type_id


    @api.onchange('requirement')
    def onchange_requirement(self):
        days_delay = 0
        if self.requirement == '2':
            days_delay = 0
        if self.requirement == '1':
            days_delay = 7
        required_day = datetime.strftime(datetime.today() + timedelta(days=days_delay),
                                         DEFAULT_SERVER_DATETIME_FORMAT)
        self.required_date = required_day

    @api.multi
    def approve_indent(self):
        res = {
            'state': 'inprogress',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        resproducts={
            'state':'inprogress'
        }
        self.write(res)
        for indent in self:
            indent.product_lines.write(resproducts)

    @api.multi
    def reject_indent(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        resproducts = {
            'state': 'reject'
        }
        self.write(res)
        for indent in self:
            indent.product_lines.write(resproducts)

    @api.multi
    def action_close_indent(self):
        res = {
            'state': 'received',
            'closer_id': self.env.user.id,
        }
        self.write(res)



    @api.multi
    def indent_confirm(self):
        for indent in self:
            if not indent.product_lines:
                raise UserError(_('Unable to confirm an indent without product. Please add product(s).'))


            res = {
                'state': 'waiting_approval'
            }

            requested_date = self.required_date
            new_seq = self.env['ir.sequence'].next_by_code_new('stock.indent', requested_date)
            if new_seq:
                res['name'] = new_seq

            indent.write(res)
            indent.product_lines.write({'state': 'waiting_approval'})

    # -------------------------------------------------------------------------------

    @api.model
    def _create_picking_and_moves(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.product_lines:
            date_planned = datetime.strptime(self.indent_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    pick_name = self.env['stock.picking.type'].browse(self.picking_type_id.id).sequence_id.next_by_id()
                    location_id = self.warehouse_id.sudo().lot_stock_id.id
                    vals = {
                        'invoice_state': 'none',
                        'picking_type_id': self.picking_type_id.id,
                        'priority': self.requirement,
                        'name': pick_name,
                        'origin': self.name,
                        'date': self.indent_date,
                        'state': 'draft',
                        'move_type': self.move_type,
                        'partner_id': self.indentor_id.partner_id.id or False,
                        'location_id': location_id,
                        'location_dest_id': self.stock_location_id.id,
                        'company_id': self.company_id.id
                    }

                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id

                moves = {
                    'name': line.name,
                    'indent_id': self.id,
                    'picking_id': picking_id,
                    'picking_type_id': self.picking_type_id.id or False,
                    'product_id': line.product_id.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'product_uom_qty': line.issue_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': location_id,
                    'location_dest_id': self.stock_location_id.id,
                    'origin': self.name,
                    'state': 'draft',
                    'price_unit': line.product_id.standard_price or 0.0,
                    'company_id': self.company_id.id
                }

                move_obj.create(moves)
        return picking_id

    @api.one
    def action_picking_create(self):
        picking_id = False
        if self.product_lines:
            picking_id = self._create_picking_and_moves()
        self.write({'picking_id': picking_id})
        return picking_id

    @api.multi
    def _get_picking_id(self):
        picking_id = self.picking_id.id
        picking_obj = self.env['stock.picking']
        picking = picking_obj.browse(picking_id)
        if picking.state != 'done':
            return [picking.id]
        elif picking.state == 'done' and self.state == 'inprogress':
            picking_ids = picking_obj.search([('origin', '=', self.name)])
            return picking_ids.ids
        return False

    @api.multi
    def action_issue_product(self):

        '''
                This function returns an action that display existing picking orders of given purchase order ids.
                When only one found, show the picking immediately.
                '''
        self.product_validate()

        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        count = 0
        for line in self.product_lines:
            date_planned = datetime.strptime(self.indent_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    pick_name = self.env['stock.picking.type'].browse(self.picking_type_id.id).sequence_id.next_by_id()
                    location_id = self.warehouse_id.sudo().lot_stock_id.id

                    vals = {
                        'invoice_state': 'none',
                        'picking_type_id': self.picking_type_id.id,
                        'priority': self.requirement,
                        'name': pick_name,
                        'origin': self.name,
                        'date': self.indent_date,
                        'state': 'draft',
                        'move_type': self.move_type,
                        'partner_id': self.indentor_id.partner_id.id or False,
                        'location_id': location_id,
                        'location_dest_id': self.stock_location_id.id,
                        'company_id': self.company_id.id,
                        # 'operating_unit_id': self.operating_unit_id.id
                    }
                    picking = picking_obj.create(vals)
                    picking.action_done()

                    if picking:
                        picking_id = picking.id

                moves = {
                    'name': line.name,
                    'indent_id': self.id,
                    'picking_id': picking_id,
                    'picking_type_id': self.picking_type_id.id or False,
                    'product_id': line.product_id.id,
                    'date': date_planned,
                    'date_expected': date_planned,
                    'product_uom_qty': line.received_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': location_id,
                    'location_dest_id': self.stock_location_id.id,
                    'origin': self.name,
                    'state': 'draft',
                    'price_unit': line.product_id.standard_price or 0.0,
                    'company_id': self.company_id.id
                }
                move_id = move_obj.create(moves)
                move_id.action_done()

                self.ensure_one()
                # If still in draft => confirm and assign
                if picking.state == 'draft':
                    picking.action_confirm()
                    if picking.state != 'assigned':
                        picking.action_assign()
                        if picking.state != 'assigned':
                               raise UserError(
                                   _("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
                for pack in picking.pack_operation_ids:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                    else:
                        pack.unlink()
                picking.do_transfer()

                res = {
                    'state': 'received',
                    'picking_id': picking_id
                }

                self.write(res)
                line.write({'state': 'received'})

                picking.write({'state': 'done'})
                move_id.write({'state': 'done'})
                # for indent in self:
                #     indent.product_lines.write(res_products)

    def product_validate(self):
        for product in self.product_lines:
            if product.qty_available <= 0:
                raise UserError('Stock not available!!!')
            elif product.qty_available < product.product_uom_qty:
                product.issue_qty = product.qty_available
            else:
                product.issue_qty = product.product_uom_qty

        for product in self.product_lines:
            if product.received_qty <= 0:
                raise UserError('Issue Quantity can not 0')
        for product in self.product_lines:
            if product.received_qty != product.product_uom_qty:
                raise UserError('Issue Quantity and Indent Quantity Must Be Same')

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        for product in self.product_lines:
            if product.qty_available <= 0:
                raise UserError('Stock not available!!!')
            elif product.qty_available < product.product_uom_qty:
                product.issue_qty = product.qty_available
            else:
                product.issue_qty = product.product_uom_qty

        if self.picking_id:
            pass
        else:
            self.action_picking_create()
            self.picking_id.action_confirm()
            self.picking_id.force_assign()

        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]
        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_ids = self._get_picking_id()
        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False

        return result

    def action_scrap_product(self):

        self.ensure_one()
        return {
            'name': _('Scrap'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_picking_id': self.id,
                        'product_ids': self.pack_operation_product_ids.mapped('product_id').ids},
            'target': 'new',
        }
        for product in self.product_lines:
            if product.qty_available <= 0:
                raise UserError('Stock not available!!!')
            elif product.qty_available < product.product_uom_qty:
                product.issue_qty = product.qty_available
            else:
                product.issue_qty = product.product_uom_qty

        for product in self.product_lines:
            if product.received_qty <= 0:
                raise UserError('Scrap Quantity can not 0')
        # for product in self.product_lines:
        #     if product.received_qty != product.product_uom_qty:
        #         raise UserError('Issue Quantity and Indent Quantity Must Be Same')

        scarp_obj = self.env['stock.scrap']
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False

        for line in self.product_lines:
            if line.product_id:
                location_id = self.warehouse_id.sudo().lot_stock_id.id
                scraps = {
                    'scrap_location_id': location_id,
                    'scrap_qty': line.issue_qty,
                    'state': 'done',
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom.id,
                    'picking_id': picking_id
                }
                scrap_id = scarp_obj.create(scraps)
                # print(scrap_id)

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['draft','confirm','received','waiting_approval','reject'])]


    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this indent'))

        return super(IndentIndent, self).unlink()


class IndentProductLines(models.Model):
    _name = 'indent.product.lines'
    _description = 'Indent Product Lines'

    indent_id = fields.Many2one('indent.indent', string='Indent', required=True, ondelete='cascade',track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', required=True,track_visibility='onchange')
    product_uom_qty = fields.Float('Indent Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1,track_visibility='onchange')
    received_qty = fields.Float('Issue Quantity', digits=dp.get_precision('Product UoS'),
                                help="Receive Quantity which Update by done quantity.",track_visibility='onchange')
    issue_qty = fields.Float('Issue Quantity', digits=dp.get_precision('Product UoS'),
                             help="Issued Quantity which Update by available quantity.",track_visibility='onchange')

    product_uom = fields.Many2one(related='product_id.uom_id', comodel='product.uom', string='Unit of Measure',
                                  required=True, store=True, track_visibility='onchange')
    price_unit = fields.Float(related='product_id.standard_price', string='Price',
                              digits=dp.get_precision('Product Price'), store=True,
                              help="Price computed based on the last purchase order approved.",
                              track_visibility='onchange')
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount_subtotal',
                                  digits=dp.get_precision('Account'),
                                  store=True, track_visibility='onchange')
    qty_available = fields.Float(string='In Stock', compute='_compute_product_qty', track_visibility='onchange')
    name = fields.Char(related='product_id.name', string='Specification', store=True, track_visibility='onchange')
    remarks = fields.Char(related='product_id.name', string='Narration', store=True, track_visibility='onchange')
    sequence = fields.Integer('Sequence')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('received', 'Received'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    ####################################################
    # Business methods
    ####################################################


    @api.depends('product_id')
    @api.multi
    def _compute_product_qty(self):
        for product in self:
            location_id = product.indent_id.warehouse_id.sudo().lot_stock_id.id
            product_quant = self.env['stock.quant'].search([('product_id', '=', product.product_id.id), ('location_id', '=', location_id)])
            quantity = sum([val.qty for val in product_quant])
            product.qty_available = quantity

