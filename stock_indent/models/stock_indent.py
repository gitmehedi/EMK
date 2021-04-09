import time
from odoo import api, fields, models, _
from datetime import datetime, timedelta
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
        return datetime.strftime(datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)

    name = fields.Char('Indent #', size=30, readonly=True, default="/")
    approve_date = fields.Datetime('Approve Date', readonly=True,track_visibility='onchange')
    indent_date = fields.Datetime('Indent Date', required=True, readonly=True,
                                  default = fields.Datetime.now)
    required_date = fields.Date('Required Date', required=True,readonly=True,states={'draft': [('readonly', False)]},
                                default=lambda self: self._get_required_date())
    indentor_id = fields.Many2one('res.users', string='Indentor', required=True, readonly=True,
                                  default=lambda self: self.env.user,
                                  states={'draft': [('readonly', False)]})
    stock_location_id = fields.Many2one('stock.location', string='Department', readonly=True,required=True,
                                        states={'draft': [('readonly', False)]},
                                        help="Default User Location.Which consider as Destination location.",
                                        default=lambda self: self.env.user.default_location_id)
    # manager_id = fields.Many2one('res.users', string='Department Manager', related='department_id.manager_id', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', ondelete="cascade",
                                          readonly=True, states={'draft': [('readonly', False)]})
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'Urgent')], 'Priority', readonly=True,
                                   default="1", required=True, states={'draft': [('readonly', False)]})
    indent_type = fields.Many2one('indent.type',string='Type',readonly=True, required = True, states={'draft': [('readonly', False)]})
    product_lines = fields.One2many('indent.product.lines', 'indent_id', 'Products', readonly=True, required = True,
                                    states={'draft': [('readonly', False)],'waiting_approval': [('readonly', False)]})
    picking_id = fields.Many2one('stock.picking', 'Picking', copy=False)
    in_picking_id = fields.Many2one('stock.picking', 'Picking')
    description = fields.Text('Additional Information', readonly=True, states={'draft': [('readonly', False)]})
    material_required_for = fields.Text('Required For', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},
                                 default=lambda self: self.env.user.company_id,required=True)
    active = fields.Boolean('Active', default=True)
    # amount_total = fields.Float(string='Total', compute=_compute_amount, store=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have approve or reject indent.",track_visibility='onchange')
    closer_id = fields.Many2one('res.users', string='Authority', readonly=True, help="who have close indent.",track_visibility='onchange')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True,required=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="Default Warehouse.Source location.",
                                   states={'draft': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type',string='Picking Type',compute = '_compute_default_picking_type',
                                      readonly=True, store = True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method',
                                 readonly=True, required=True, default='direct',
                                 states={'draft': [('readonly', False)], 'cancel': [('readonly', True)]},
                                 help="It specifies goods to be deliver partially or all at once")

    pr_indent_check = fields.Boolean(string = 'Indent List Check',default = True)

    days_of_backdating_indent = fields.Integer(size=4, compute='_compute_days_of_backdating')

    product_id = fields.Many2one(
        'product.product', 'Products',
        readonly="1", related='product_lines.product_id',
        help="This comes from the product form.")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting for Approval'),
        ('inprogress', 'In Progress'),
        ('received', 'Issued'),
        ('reject', 'Rejected'),
    ], string='State', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    ####################################################
    # Business methods
    ####################################################
    @api.multi
    @api.depends('product_lines.product_id')
    def _compute_days_of_backdating(self):
        for rec in self:
            for line in rec.product_lines:
                if line.product_id.categ_id.is_backdateable:
                    query = """select days_of_backdating_indent from stock_indent_config_settings order by id desc limit 1"""
                    self.env.cr.execute(query)
                    days_value = self.env.cr.fetchone()
                    if days_value:
                        rec.days_of_backdating_indent = days_value[0]
                        break
                    else:
                        rec.days_of_backdating_indent = 0
                        break
                else:
                    rec.days_of_backdating_indent = 0

    @api.one
    @api.constrains('indent_date')
    def _check_indent_date(self):
        days_delay = datetime.strftime((datetime.today() - timedelta(days=self.days_of_backdating_indent)).date(),
                                       DEFAULT_SERVER_DATETIME_FORMAT)
        if self.indent_date < days_delay:
            raise ValidationError(_("As per Indent configuration back date entry can't be less then %s days.") % self.days_of_backdating_indent)


    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        if self.warehouse_id:
            return {'domain': {'stock_location_id': [('id', 'in', self.env.user.location_ids.ids),('can_request','=',True)]}}

    @api.one
    @api.constrains('required_date')
    def _check_required_date(self):
        if self.required_date+' 23:59:59' <= self.indent_date:
            raise UserError('Required Date can not be less then current date!!!')

    @api.multi
    @api.depends('warehouse_id','stock_location_id')
    def _compute_default_picking_type(self):
        for indent in self:
            picking_type_obj = indent.env['stock.picking.type']
            picking_type_ids = picking_type_obj.suspend_security().search([('default_location_src_id', '=', indent.warehouse_id.sudo().lot_stock_id.id),('default_location_dest_id', '=', indent.stock_location_id.id)])
            picking_type_id = picking_type_ids and picking_type_ids[0] or False
            indent.picking_type_id = picking_type_id


    @api.one
    @api.constrains('picking_type_id')
    def _check_picking_type(self):
        if not self.picking_type_id:
            raise ValidationError(_('No Picking Type For this Department.'
                                'Please Create a picking type or contact with system Admin.'))

    @api.onchange('requirement')
    def onchange_requirement(self):
        days_delay = 0
        if self.requirement == '2':
            days_delay = 0
        if self.requirement == '1':
            days_delay = 7
        required_day = datetime.strftime(datetime.today() + timedelta(days=days_delay),
                                                  DEFAULT_SERVER_DATETIME_FORMAT)
        self.required_date= required_day

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
            # followers = []
            # if indent.indentor_id and indent.indentor_id.partner_id and indent.indentor_id.partner_id.id:
            #     followers.append(indent.indentor_id.partner_id.id)
            # if indent.indentor_id.employee_ids[0].parent_id:
            #     followers.append(indent.indentor_id.employee_ids[0].parent_id.user_id.partner_id.id)
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

    @api.one
    def action_picking_create(self,products):
        picking_id = False
        if products:
            picking_id = self.create_picking_and_moves(products)
        self.write({'picking_id': picking_id})
        return picking_id

    @api.multi
    def create_picking_and_moves(self,products):
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        picking_id = False
        for line in products:
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
                    'product_uom_qty': line.product_uom_qty,
                    'product_uom': line.product_uom.id,
                    'location_id': location_id,
                    'location_dest_id': self.stock_location_id.id,
                    'origin': self.name,
                    'state': 'draft',
                    'price_unit': line.product_id.standard_price or 0.0,
                    'company_id' : self.company_id.id
                }

                move_obj.create(moves)
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
    def action_view_picking(self):
        products = self.product_lines.filtered(lambda x: x.qty_available_now > 0)
        if not products:
            raise UserError('Stock not available for any products!!!')
        for product in products:
            # if product.qty_available_now <= 0:
            #     raise UserError('Stock not available!!!')
            if product.qty_available_now < product.product_uom_qty:
                product.issue_qty = product.qty_available_now
            else:
                product.issue_qty = product.product_uom_qty
        if self.picking_id:
            pass
        else:
            self.action_picking_create(products)
            self.picking_id.action_confirm()
            # self.picking_id.force_assign()
            self.picking_id.action_assign()


        action = self.env.ref('stock.action_picking_tree')
        result = action.read()[0]
        # override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        pick_ids = self._get_picking_id()

        for p in self.env['stock.picking'].browse(pick_ids):
            if p.state == 'confirmed':
                p.action_assign()

        # choose the view_mode accordingly
        if len(pick_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = pick_ids and pick_ids[0] or False
        return result

    @api.multi
    def action_print(self):
        data = {}
        # data['picking_id'] = self.id
        return self.env["report"].get_action(self, 'stock_indent.report_stock_indent_view', data)

    ####################################################
    # ORM Overrides methods
    ####################################################
    @api.model
    def _needaction_domain_get(self):
        users_obj = self.env['res.users']
        if users_obj.has_group('stock_indent.group_stock_indent_approver'):
            domain = [
                ('state', 'in', ['waiting_approval'])]
            return domain
        elif users_obj.has_group('stock.group_stock_user'):
            domain = [
                ('state', 'in', ['inprogress'])]
            return domain
        else:
            return False

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
    received_qty = fields.Float('Received', digits=dp.get_precision('Product UoS'),help="Receive Quantity which Update by done quntity.")
    issue_qty = fields.Float('Issue Quantity', digits=dp.get_precision('Product UoS'),help="Issued Quantity which Update by avilable quantity.")
    product_uom = fields.Many2one(related='product_id.uom_id',comodel='product.uom',string='Unit of Measure', required=True,store=True)
    price_unit = fields.Float(related='product_id.standard_price',string='Price', digits=dp.get_precision('Product Price'),store=True,
                              help="Price computed based on the last purchase order approved.")
    price_subtotal = fields.Float(string='Subtotal', compute='_compute_amount_subtotal', digits=dp.get_precision('Account'),
                                  store=True)
    qty_available = fields.Float(string='On Hand',compute = '_compute_product_qty',store=True
                                 ,help = "Quantity on hand when indent issued")
    qty_available_now = fields.Float(string='In Stock Now',compute = '_compute_product_qty'
                                     , help="Always updated Quantity")
    name = fields.Char(related='product_id.name',string='Specification',store=True)
    remarks = fields.Text('Remarks')
    sequence = fields.Integer('Sequence')

    ####################################################
    # Business methods
    ####################################################
    @api.constrains('product_id')
    def check_product_id(self):
        for rec in self:
            duplicate_products = rec.indent_id.product_lines.filtered(lambda r: r.product_id.id == rec.product_id.id)
            if len(duplicate_products)>1:
                raise ValidationError('You can not select same product')

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
            product.qty_available_now = quantity
