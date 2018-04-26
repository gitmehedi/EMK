from odoo import api, fields, models, _
import time
import datetime
from datetime import timedelta
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class IndentIndent(models.Model):
    _name = 'indent.indent'
    _description = "Indent"
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = "approve_date desc"


    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env.user.company_id.id
        warehouse_ids = warehouse_obj.sudo().search([('company_id', '=', company_id),('operating_unit_id', 'in', self.env.user.operating_unit_ids.ids)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    @api.model
    def _get_required_date(self):
        return datetime.datetime.strftime(datetime.datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)

    @api.multi
    def _default_department(self):
        emp_pool_obj = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return emp_pool_obj.department_id.id

    name = fields.Char('Indent #', size=30, readonly=True, default="/")
    approve_date = fields.Datetime('Approve Date', readonly=True)
    indent_date = fields.Datetime('Indent Date', required=True, readonly=True,
                                  default=datetime.datetime.today())
    required_date = fields.Date('Required Date', required=True,readonly=True,states={'draft': [('readonly', False)]},
                                default=lambda self: self._get_required_date())
    indentor_id = fields.Many2one('res.users', string='Indentor', required=True, readonly=True,
                                  default=lambda self: self.env.user,
                                  states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', string='Department', readonly=True,default=_default_department)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', readonly=True,required=True,
                                        states={'draft': [('readonly', False)]},
                                        help="Default User Location.Destination location.",
                                        default=lambda self: self.env.user.default_location_id)
    # manager_id = fields.Many2one('res.users', string='Department Manager', related='department_id.manager_id', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]})
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'Urgent')], 'Priority', readonly=True,
                                   default="1", required=True, states={'draft': [('readonly', False)]})
    indent_type = fields.Many2one('indent.type',string='Type',readonly=True, required = True, states={'draft': [('readonly', False)]})
    product_lines = fields.One2many('indent.product.lines', 'indent_id', 'Products', readonly=True, required = True,
                                    states={'draft': [('readonly', False)],
                                            'waiting_approval': [('readonly', False)]})
    picking_id = fields.Many2one('stock.picking', 'Picking')
    in_picking_id = fields.Many2one('stock.picking', 'Picking')
    description = fields.Text('Additional Information', readonly=True, states={'draft': [('readonly', False)]})
    material_required_for = fields.Text('Required For', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id,required=True)
    active = fields.Boolean('Active', default=True)
    # amount_total = fields.Float(string='Total', compute=_compute_amount, store=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have approve or reject indent.")
    closer_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have close indent.")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True,required=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="Default Warehouse.Source location.",
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type',string='Picking Type',compute = '_compute_default_picking_type',
                                      readonly=True, store = True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method',
                                 readonly=True, required=True, default='direct',
                                 states={'draft': [('readonly', False)], 'cancel': [('readonly', True)]},
                                 help="It specifies goods to be deliver partially or all at once")

    pr_indent_check = fields.Boolean(string = 'Indent List Check',default = True)

    product_id = fields.Many2one(
        'product.product', 'Products',
        readonly="1", related='product_lines.product_id',
        help="This comes from the product form.")

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
        # if self.warehouse_id:
        #     self.stock_location_id = []
        return {'domain': {'stock_location_id': [('id', 'in', self.env.user.location_ids.ids)]}}

    @api.multi
    @api.depends('warehouse_id','stock_location_id')
    def _compute_default_picking_type(self):
        for indent in self:
            picking_type_obj = indent.env['stock.picking.type']
            picking_type_ids = picking_type_obj.search([('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),('default_location_dest_id', '=', indent.stock_location_id.id)])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False
            indent.picking_type_id = picking_type_id

    @api.onchange('requirement')
    def onchange_requirement(self):
        vals = {}
        days_delay = 0
        if self.requirement == '2':
            days_delay = 0
        if self.requirement == '1':
            days_delay = 7
        # TODO: for the moment it will count the next days based on the system time
        # and not based on the indent_date available on the indent.
        required_day = datetime.datetime.strftime(datetime.datetime.today() + timedelta(days=days_delay),
                                                  DEFAULT_SERVER_DATETIME_FORMAT)
        vals.update({'value': {'required_date': required_day}})
        return vals

    @api.multi
    def approve_indent(self):
        res = {
            'state': 'inprogress',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

    @api.multi
    def reject_indent(self):
        res = {
            'state': 'reject',
            'approver_id': self.env.user.id,
            'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)

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
            # Add all authorities of the indent as followers
            followers = []
            if indent.indentor_id and indent.indentor_id.partner_id and indent.indentor_id.partner_id.id:
                followers.append(indent.indentor_id.partner_id.id)
            # if indent.manager_id and indent.manager_id.partner_id and indent.manager_id.partner_id.id:
            #    followers.append(indent.manager_id.partner_id.id)

            # for follower in followers:
            #    indent.write({'message_follower_ids': [(4, follower)]})
            res = {
                'state': 'waiting_approval'
            }
            requested_date = self.required_date
            new_seq = self.env['ir.sequence'].next_by_code_new('stock.indent',requested_date)
            if new_seq:
                res['name'] = new_seq

            indent.write(res)

    def _prepare_indent_line_move(self, line, picking_id, date_planned):
        location_id = self.warehouse_id.sudo().lot_stock_id.id

        res = {
            'name': line.name,
            'indent_id': self.id,
            'picking_id': picking_id,
            'picking_type_id': self.picking_type_id.id or False,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'location_id': location_id,
            'location_dest_id': self.stock_location_id.id,
            'origin': self.name,
            'state': 'draft',
            'price_unit': line.product_id.standard_price or 0.0
        }

        if line.product_id.type in ('service'):
            if not line.original_product_id:
                raise models.except_osv(_("Warning !"),
                                        _("You must define material or parts that you are going to repair !"))

            upd_res = {
                'product_id': line.original_product_id.id,
                'product_uom': line.original_product_id.uom_id.id,
                'product_uos': line.original_product_id.uom_id.id
            }
            res.update(upd_res)

        # if self.company_id:
        #     res = dict(res, company_id = .company_id.id)
        return res

    def _prepare_indent_picking(self):
        pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
        location_id = self.warehouse_id.sudo().lot_stock_id.id
        res = {
            'invoice_state': 'none',
            'picking_type_id': self.picking_type_id.id,
            'priority': self.requirement,
            'name': pick_name,
            'origin': self.name,
            'date': self.indent_date,
            # 'type': 'internal',
            'state':'draft',
            'move_type': self.move_type,
            'partner_id': self.indentor_id.partner_id.id or False,
            'location_id': location_id,
            'location_dest_id': self.stock_location_id.id,
        }
        if self.company_id:
            res = dict(res, company_id=self.company_id.id)
        return res


    @api.model
    def _create_pickings_and_procurements(self):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in self.product_lines:
            date_planned = datetime.datetime.strptime(self.indent_date, DEFAULT_SERVER_DATETIME_FORMAT)

            if line.product_id:
                if not picking_id:
                    vals = self._prepare_indent_picking()
                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id

                move_obj.create(self._prepare_indent_line_move(line, picking_id, date_planned))
        return picking_id


    @api.one
    def action_picking_create(self):
        picking_id = False
        if self.product_lines:
            picking_id = self._create_pickings_and_procurements()
        self.write({'picking_id': picking_id})

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
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        for product in self.product_lines:
            if product.qty_available < product.product_uom_qty:
                raise UserError('Stock not available!!!')

        if self.picking_id:
            pass
        else:
            self.action_picking_create()

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

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def _needaction_domain_get(self):
        return [('state', 'in', ['waiting_approval'])]

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this indent'))

        return super(IndentIndent, self).unlink()


class IndentProductLines(models.Model):
    _name = 'indent.product.lines'
    _description = 'Indent Product Lines'

    indent_id = fields.Many2one('indent.indent', string='Indent', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_uom_qty = fields.Float('Quantity', digits=dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one(related='product_id.uom_id',string='Unit of Measure', required=True)
    price_unit = fields.Float(related='product_id.standard_price',string='Price', digits=dp.get_precision('Product Price'),
                              help="Price computed based on the last purchase order approved.")
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount_subtotal', digits=dp.get_precision('Account'),
                                  store=True)
    qty_available = fields.Float(string='In Stock',compute = '_compute_product_qty')
    name = fields.Char(related='product_id.name',string='Specification',store=True)
    remarks = fields.Text('Remarks')
    sequence = fields.Integer('Sequence')

    @api.one
    @api.constrains('product_uom_qty')
    def _check_product_uom_qty(self):
        if self.product_uom_qty < 0:
            raise UserError('You can\'t give negative value!!!')

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount_subtotal(self):
        for line in self:
            line.price_subtotal = (line.product_uom_qty * line.price_unit)

    @api.depends('product_id')
    @api.multi
    def _compute_product_qty(self):
        for product in self:
            location_id = product.indent_id.warehouse_id.sudo().lot_stock_id.id
            product_quant = self.env['stock.quant'].search([('product_id', '=', product.product_id.id),
                                                        ('location_id', '=', location_id)])
            quantity = sum([val.qty for val in product_quant])
            product.qty_available = quantity
