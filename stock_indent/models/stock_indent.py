from odoo import api, fields, models, _

import time
import datetime
from datetime import timedelta
from odoo.addons import decimal_precision as dp

from odoo.exceptions import UserError, ValidationError

from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class IndentIndent(models.Model):
    _name = 'indent.indent'
    _description = "Indent"
    _inherit = ['mail.thread']
    _order = "approve_date desc"
    
    @api.depends('product_lines')
    def _compute_amount(self):
        for indent in self:
            total = 0.0
            for line in indent.product_lines:
                total += line.price_subtotal
            indent.amount_total = total
    
    @api.model
    def _get_product_line(self):
        result = {}
        line_obj = self.env['indent.product.lines']
        for line in line_obj:
            result[line.indent_id.id] = True
        return result.keys()

    @api.model
    def _get_default_warehouse(self):
        warehouse_obj = self.env['stock.warehouse']
        company_id = self.env.user.company_id.id
        warehouse_ids = warehouse_obj.search([('company_id', '=', company_id)])
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id

    @api.model
    def _get_required_date(self):
        return datetime.datetime.strftime(datetime.datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)

    name = fields.Char('Indent #', size=30, readonly=True, default="/")
    approve_date = fields.Datetime('Approve Date', readonly=True)
    indent_date = fields.Datetime('Indent Date', required=True, readonly=True,
                                  default=datetime.datetime.today())
    required_date = fields.Date('Required Date', required=True,
                                     default=lambda self: self._get_required_date())
    indentor_id = fields.Many2one('res.users', string='Indentor', required=True, readonly=True, 
                                  default=lambda self: self.env.user,
                                  states={'draft': [('readonly', False)]})
    #department_id = fields.Many2one('stock.location', string='Department', readonly=True,  states={'draft': [('readonly', False)]}, domain=[('can_request','=', True)])
    #manager_id = fields.Many2one('res.users', string='Department Manager', related='department_id.manager_id', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Project', ondelete="cascade",readonly=True,  states={'draft': [('readonly', False)]})
    requirement = fields.Selection([('1', 'Ordinary'), ('2', 'Urgent')], 'Priority', readonly=True,
                                   default="1", required=True,  states={'draft': [('readonly', False)]})
    # type = fields.Selection([('new', 'Purchase Indent'), ('existing', 'Repairing Indent')], 'Type', required=True,
    #              readonly=True, states={'draft': [('readonly', False)]}),
    product_lines = fields.One2many('indent.product.lines', 'indent_id', 'Products', readonly=True, 
                                    states={'draft': [('readonly', False)], 
                                            'waiting_approval': [('readonly', False)]})
    picking_id = fields.Many2one('stock.picking','Picking')
    in_picking_id = fields.Many2one('stock.picking','Picking')
    description = fields.Text('Additional Information', readonly=True, states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', readonly=True, states={'draft': [('readonly', False)]},default=lambda self: self.env.user.company_id)
    active = fields.Boolean('Active', default=True)
    amount_total = fields.Float(string='Total', compute=_compute_amount, store=True)
    approver_id = fields.Many2one('res.users', string='Authority', readonly=True, states={'draft': [('readonly', False)]}, help="who have approve or reject indent.")
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', readonly=True,
                                   default=lambda self: self._get_default_warehouse(),
                                   help="default warehose where inward will be taken", 
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, required=True)
    move_type = fields.Selection([('direct', 'Partial'), ('one', 'All at once')], 'Receive Method',
                                 readonly=True, required=True, default='direct',
                                 states={'draft':[('readonly', False)], 'cancel':[('readonly',True)]}, 
                                 help="It specifies goods to be deliver partially or all at once")
    
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
        ], string='State', readonly=True , copy=False, index=True, track_visibility='onchange', default='draft')
    
    @api.model
    def _default_stock_location(self):
        #TODO: need to improve this try except with some better option
        try:
            stock_location = self.pool.get('ir.model.data').get_object(cr, uid, 'stock_indent', 'location_production1').id
        except:
            stock_location = False
        return stock_location

    def _get_default_picking_type(self):
        picking_type_obj = self.pool.get('stock.picking.type')
        picking_type_ids = picking_type_obj.search(cr, uid, [], context=context)
        picking_type_id = picking_type_ids and picking_type_ids[0] or False
        return picking_type_id
    
    def _check_purchase_limit(self):
        return True
    
    _constraints = [
        (_check_purchase_limit, 'You have exided your purchase limit for the current period !.', ['amount_total']),
    ]
    
    def onchange_requirement(self, indent_date, requirement='urgent'):
        vals = {}
        days_delay = 0
        if requirement == '2':
            days_delay = 0
        if requirement == '1':
            days_delay = 7
        #TODO: for the moment it will count the next days based on the system time 
        #and not based on the indent_date available on the indent. 
        required_day = datetime.datetime.strftime(datetime.datetime.today() + timedelta(days=days_delay), DEFAULT_SERVER_DATETIME_FORMAT)
        vals.update({'value':{'required_date':required_day}})
        return vals
    
    def _needaction_domain_get(self):
        return [('state', '=', 'waiting_approval')]

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if default is None:
            default = {}
        required_date = datetime.datetime.strftime(datetime.datetime.today() + timedelta(days=7), DEFAULT_SERVER_DATETIME_FORMAT)
        default.update({
            'name': "/",
            'indent_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'requirement': '1',
            'picking_id': False,
            'indent_authority_ids': [],
            'state': 'draft',
            'approver_id':False,
            'approve_date':False,
            'required_date':required_date
        })
        
        return super(IndentIndent, self).copy(default)
    
    def onchange_item(self, item_for=False):
        result = {}
        if not item_for or item_for == 'store':
            result['analytic_account_id'] = False
        return {'value': result}
    
    @api.multi
    def approve_indent(self):
        self.check_approval()
        self.state = 'inprogress'
        for indent in self:
            indent.action_picking_create()

            
    @api.multi
    def check_approval(self):
        res = {
            'state': 'inprogress',
            'approver_id':self.env.user.id,
            'approve_date':time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)
    
    @api.multi
    def reject_indent(self):
        res = {
            'state': 'reject',
            'approver_id':self.env.user.id,
            'approve_date':time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.write(res)
    
    @api.multi
    def indent_confirm(self):
        for indent in self:
            if not indent.product_lines:
                raise UserError(_('You cannot confirm an indent %s which has no line.' % (indent.name)))
                #raise osv.except_osv(_('Warning!'),_('You cannot confirm an indent %s which has no line.' % (indent.name)))

            # Add all authorities of the indent as followers
            followers = []
            if indent.indentor_id and indent.indentor_id.partner_id and indent.indentor_id.partner_id.id:
                followers.append(indent.indentor_id.partner_id.id)
            #if indent.manager_id and indent.manager_id.partner_id and indent.manager_id.partner_id.id:
            #    followers.append(indent.manager_id.partner_id.id)

            #for follower in followers:
            #    indent.write({'message_follower_ids': [(4, follower)]})
            
            res = {
               'state': 'waiting_approval'
            }
            
            new_seq = self.env['ir.sequence'].next_by_code('stock.indent')
            if new_seq:
                res['name'] = new_seq
                
            indent.write(res)

    
    def _prepare_indent_line_move(self, line, picking_id, date_planned):
        location_id = self.warehouse_id.lot_stock_id.id

        res = {
            'name': line.name,
            'indent_id':self.id,
            'picking_id': picking_id,
            'picking_type_id': self.picking_type_id.id or False,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'location_id': location_id,
            'location_dest_id': self.department_id.id,
            'origin': self.name,
            'state': 'draft',
            'price_unit': line.product_id.standard_price or 0.0
        }

        if line.product_id.type in ('service'):
            if not line.original_product_id:
                raise models.except_osv(_("Warning !"), _("You must define material or parts that you are going to repair !"))

            upd_res = {
                'product_id':line.original_product_id.id,
                'product_uom': line.original_product_id.uom_id.id,
                'product_uos':line.original_product_id.uom_id.id
            }
            res.update(upd_res)

        # if self.company_id:
        #     res = dict(res, company_id = .company_id.id)
        return res
    
    def _prepare_indent_picking(self):
        pick_name = self.env['ir.sequence'].next_by_code('stock.picking')
        res = {
            'invoice_state': 'none',
            'picking_type_id': self.picking_type_id.id,
            'priority': self.requirement,
            'name': pick_name,
            'origin': self.name,
            'date': self.indent_date,
            #'type': 'internal',
            'move_type':self.move_type,
            'partner_id': self.indentor_id.partner_id.id or False,
            'location_id': self.warehouse_id.lot_stock_id.id,
            #'location_dest_id': self.department_id.id
        }
        if self.company_id:
            res = dict(res, company_id = self.company_id.id)
        return res
    
    @api.one
    def _create_purchase_req(self, indent_name):
        pur_req_obj = self.env['purchase.requisition']
        
        values = {
            #'name': line.name,
            'origin':'Indent : ' + indent_name,
            'user_id': self.env.user.id,
            'exclusive': 'exclusive',
        }
        
        return pur_req_obj.create(values)
        
    def _create_purchase_req_line(self, line, req_id):
        pur_line_obj = self.env['purchase.requisition.line']
        
        values = {
            'requisition_id': req_id,
            'product_id': line.product_id.id,
            'product_qty':line.product_uom_qty,
            'product_uom_id': line.product_uom.id,
            'schedule_date': line.indent_id.required_date or False,
        }
        
        return pur_line_obj.create(values)        
    
    @api.model
    def _create_pickings_and_procurements(self):
        print "============_create_pickings_and_procurements=============="
        move_obj = self.env['stock.move']
        picking_obj = self.env['stock.picking']
        
        #Check if the indent is for purchase indent
        #A purchase requisition will create
        need_purchase_req = False
        picking_id = False
        for line in self.product_lines:
            if line.type == 'make_to_order':
                need_purchase_req = True
            
            if need_purchase_req:
                purchase_req = self._create_purchase_req(self.name)
                need_purchase_req = False
                
            if purchase_req:
                self._create_purchase_req_line(line, purchase_req[0].id or False)

            date_planned = datetime.datetime.strptime(self.indent_date, DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(days=line.delay or 0.0)
            
            if line.product_id:
                if not picking_id:
                    vals = self._prepare_indent_picking()
                    picking = picking_obj.create(vals)
                    if picking:
                        picking_id = picking.id
                
                move_obj.create(self._prepare_indent_line_move(line, picking_id, date_planned))

        return picking_id
    
    def _check_gatepass_flow(self, indent):
        if indent.type == 'existing':
            return True
        else:
            return False
        
#     def create_transfer_move(self, indent, internal=None):
#         move_obj = self.pool.get('stock.move')
#         picking_obj = self.pool.get('stock.picking')
#         product_pool = self.pool.get('product.product')
#         
#         location_id = indent.warehouse_id.lot_stock_id.id
#         
#         picking_id = False
#         for line in indent.product_lines:
#             date_planned = self._get_date_planned(cr, uid, indent, line, indent.indent_date, context=context)
# 
#             if line.product_id:
#                 move_id = False
#                 if not picking_id:
#                     picking_id = picking_obj.create(cr, uid, self._prepare_indent_picking(cr, uid, indent, context=context))
#                 
#                 res = self._prepare_indent_line_move(cr, uid, indent, line, picking_id, date_planned, context=context)
#                 res.update({
#                     'location_id': indent.department_id.id,
#                     'location_dest_id': location_id
#                 })
#                 if internal:
#                     move_id = move_obj.create(cr, uid, res, context=context)
#                 elif not internal and not product_pool.browse(cr, uid, res.get('product_id')).repair_ok:
#                     move_id = move_obj.create(cr, uid, res, context=context)
# 
#         wf_service = netsvc.LocalService("workflow")
#         if picking_id:
#             wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)
#         
#         self.write(cr, uid, [indent.id], {'in_picking_id': picking_id})
#         return True
   
    def create_repairing_gatepass(self, indent):
        pass
    
    @api.one
    def action_picking_create(self):
        print "================action_picking_create==================="
        move_obj = self.env['stock.move']
        picking_id = False

        if self.product_lines:
            picking_id = self._create_pickings_and_procurements()
            print picking_id

        move_ids = move_obj.search([('picking_id','=',picking_id)])

        self.write({'picking_id': picking_id, 
                    'state' : 'inprogress', 
                    # 'message_follower_ids': [(4, self.approver_id and
                    #                           self.approver_id.partner_id and
                    #                           self.approver_id.partner_id.id)]
                    }
                   )


    @api.multi
    def _get_picking_id(self):
        #indent = self.browse(cr, uid, ids[0], context=context)
        if self.picking_id:
            picking_id = self.picking_id.id
            picking_obj = self.env['stock.picking']
            picking = picking_obj.browse(picking_id)
            if picking.state not in ('done'):
                return [picking.id]
            elif picking.state in ('done') and self.state == 'inprogress':
                picking_ids = picking_obj.search([('origin','=', self.name)])
                return picking_ids.ids
        return False

    @api.multi
    def action_view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
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

    def unlink(self):
        for indent in self:
            if indent.state != 'draft':
                raise ValidationError(_('You cannot delete this indent'))
                
        return super(IndentIndent, self).unlink()
    
    
class IndentProductLines(models.Model):
    _name = 'indent.product.lines'
    _description = 'Indent Product Lines'
    
    @api.depends('product_uom_qty', 'price_unit')
    def _amount_subtotal(self):
        for line in self:
            line.price_subtotal = (line.product_uom_qty * line.price_unit)
    
    indent_id = fields.Many2one('indent.indent', string='Indent', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)  
    original_product_id = fields.Many2one('product.product', string='Product to be Repaired')
    type = fields.Selection([('make_to_stock', 'Stock'), 
                             ('make_to_order', 'Purchase')], 
                            'Procure', required=True,
                            default="make_to_order",
                            help="From stock: When needed, the product is taken from the stock or we wait for replenishment.\nOn order: When needed, the product is purchased or produced.")
    product_uom_qty = fields.Float('Quantity', digits= dp.get_precision('Product UoS'),
                                   required=True, default=1)
    product_uom = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    product_uos_qty = fields.Float('Quantity (UoS)' ,digits= dp.get_precision('Product UoS'),
                                   default=1)
    product_uos = fields.Many2one('product.uom', 'Product UoS')
    price_unit = fields.Float('Price', required=True, digits= dp.get_precision('Product Price'), help="Price computed based on the last purchase order approved.")
    product_id = fields.Many2one('product.product', string='Product', required=True)    
    price_subtotal = fields.Float(string='Subtotal', compute='_amount_subtotal', digits= dp.get_precision('Account'), store=True) 
    qty_available = fields.Float('In Stock')
    virtual_available = fields.Float('Forecasted Qty')
    delay = fields.Float('Lead Time', required=True, default=0.0)
    name = fields.Text('Purpose', required=True)
    specification = fields.Text('Specification')
    sequence = fields.Integer('Sequence')
    
    
    def _get_uom_id(self):
        result = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'product_uom_unit')
        return result and result[1] or False
    
    def _get_default_type(self):
        context = args[0]
        return context.get('indent_type')
    
    def _check_stock_available(self):
#         for move in self.browse(cr, uid, ids, context):
#             if move.type == 'make_to_stock' and move.product_uom_qty > move.qty_available:
#                 return False
        return True
    
    _constraints = [
        (_check_stock_available, 'You can not procure more quantity form stock then the available !.', ['Quantity Required']),
    ]
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        product_obj = self.env['product.product']
        if not self.product_id:
            return {'value': {'product_uom_qty': 1.0, 
                              'product_uom': False, 
                              'price_unit': 0.0, 
                              'qty_available': 0.0, 
                              'virtual_available': 0.0, 
                              'name': '', 
                              'delay': 0.0
                              }
                    }

        #product = product_obj.browse(cr, uid, product_id, context=context)
        product = self.product_id        
        
        if product.qty_available > 0:
            #result['type'] = 'make_to_stock'
            self.type = 'make_to_stock'
        else:
            #result['type'] = 'make_to_order'
            self.type = 'make_to_order'
            
        prodduct_name = product.name_get()[0][1]
        self.name = prodduct_name
        self.product_uom = product.uom_id.id
        self.price_unit = product.standard_price
        self.qty_available = product.qty_available
        self.virtual_available = product.virtual_available
        self.specification = prodduct_name
        
        if product.type == 'service':
            #result['original_product_id'] = product.repair_id.id
            self.type = 'make_to_order'
        else:
            self.original_product_id = False
            
        #You must define at least one supplier for this product
        if not product.seller_ids:
            #user = self.pool.get('res.users').browse(cr, uid, uid)
            self.delay = self.env.user.company_id.po_lead or 0
            #raise osv.except_osv(_("Warning !"), _("You must define at least one supplier for this product"))
        else:
            self.delay = product.seller_ids[0].delay
        

    
