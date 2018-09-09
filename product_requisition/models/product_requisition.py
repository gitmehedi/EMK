from datetime import datetime

from openerp import api, models, fields, _
from openerp.exceptions import ValidationError


class ProductRequisitionModel(models.Model):
    _name = 'product.requisition'
    _description = 'Model stores all requisition data which comes different branch.'

    @api.model
    def get_current_period(self):
        time = fields.Datetime.now()
        next_month = "{0}-{1}-01".format(time.year, time.month, time.day)
        next_period = self.env['account.period'].search(
            [('date_start', '>=', next_month), ('special', '=', False), ('state', '=', 'draft')], order='id ASC',
            limit=2)

        return next_period[1] if len(next_period) > 1 else next_month[0]

    @api.model
    def _default_operating_unit(self):
        if self.env.user.default_operating_unit_id == True:
            return self.env.user.default_operating_unit_id

    quantity = fields.Integer(string='Minumum Stock Level in Day\'s Usage', required=True,
                              related='operating_unit_id.min_stock_days',
                              readonly=True)
    date = fields.Date(string='Requisition Preparation Date', required=True, default=fields.Datetime.now)

    """ Relational Filds """
    period_id = fields.Many2one('account.period', string='Requisition For the Period', required=True,
                                domain="[('special','=',False),('state','=','draft')]",
                                default=get_current_period, readonly=True,
                                states={'draft': [('readonly', False)]})
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True,
                                        default=_default_operating_unit, domain=[('active', '=', True)],
                                        readonly=True, states={'draft': [('readonly', False)]})

    line_ids = fields.One2many('product.requisition.line', 'requisition_id',
                               readonly=True, states={'draft': [('readonly', False)]})

    state = fields.Selection([('draft', 'Draft'), ('submit', 'Submitted')], default='draft')

    @api.one
    def name_get(self):
        name = self.operating_unit_id
        if self.operating_unit_id and self.period_id:
            name = '%s - %s' % (self.operating_unit_id.name, self.period_id.name)
        return (self.id, name)

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_submit(self):
        self.state = 'submit'

    @api.multi
    def act_branch_issue(self):
        transit_location = self.env['stock.location'].search([('name', 'ilike', 'Inter Company Transit')])
        picking = self.get_picking(source_loc=22, dest_loc=transit_location.id)

        for val in self.line_ids:
            if val:
                move = {}
                move['picking_id'] = picking.id
                move['product_id'] = val.product_id.id
                move['product_uom'] = val.product_id.uom_id.id
                move['product_uos_qty'] = val.product_required_qty
                move['avail_qty'] = val.product_required_qty
                move['product_uom_qty'] = val.product_required_qty
                move['name'] = val.product_id.name
                move['price_unit'] = val.product_id.price
                move['invoice_state'] = 'invoiced'
                # move['date_expected'] = '{0}'.format(datetime.date.today())
                move['location_id'] = 22
                move['location_dest_id'] = transit_location.id
                move['procure_method'] = "make_to_stock"
                picking.move_lines.create(move)
        picking.action_confirm()
        picking.force_assign()
        form_view = self.env.ref('product_requisition.branch_issue_form_view')
        tree_view = self.env.ref('product_requisition.branch_issue_tree_view')
        return {
            'name': _('Branch Issue'),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_id': picking.id,
            'views': [
                (form_view.id, 'form'),
                (tree_view.id, 'tree'),
            ],
        }

    def get_picking(self, source_loc, dest_loc):
        picking_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', source_loc),
                                                              ('default_location_dest_id', '=', dest_loc)],
                                                             order='id asc', limit=1)
        if not picking_type:
            raise ValidationError(_('Please Create a Picking Type, Otherwise your operation will not continue.'))

        picking_val = {
            'picking_type_id': picking_type.id,
            'priority': '1',
            'move_type': 'direct',
            'company_id': self.env.user['company_id'].id,
            'dest_operating_unit_id': 7,
            'invoice_state': 'none',
        }
        return self.env['stock.picking'].create(picking_val)
        # picking.action_done()


class ProductRequisitionLineModel(models.Model):
    _name = 'product.requisition.line'
    _description = 'Model stores all requisition data which comes different branch.'

    stock_in_hand_qty = fields.Integer(string='On Hand Stock')
    required_qty = fields.Integer(string='Req. for Remain Period', compute='_compute_required_qty', store=True)
    adjustment_qty = fields.Integer(string='S Adjustment')
    average_qty = fields.Integer(string='Average Usage', compute='_compute_average', store=True)
    minimum_stock_qty = fields.Integer(string='Minimum Stock', compute='_compute_minimum_stock', store=True)
    product_required_qty = fields.Integer(string='Product Required', store=True, compute='compute_product_required_qty')
    excess_qty = fields.Integer(string='Excess Stock', store=True, compute='compute_excess_qty')

    """ Relational Filds """
    product_id = fields.Many2one('product.product', string='Product Name', required=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='UoM', readonly=True, store=True)
    requisition_id = fields.Many2one('product.requisition', ondelete='cascade')

    @api.one
    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            location = self.get_stock_location(self.requisition_id.operating_unit_id.id)
            quant = self.env['stock.quant'].search([('location_id', '=', location),
                                                    ('product_id', '=', self.product_id.id)])
            self.stock_in_hand_qty = sum([rec.qty for rec in quant]) if quant else 0
            self.average_qty = self.average_usage_per_month()
            self.required_qty = self.get_calculated_quantity('min_req')
            self.product_required_qty = self.get_calculated_quantity('req')
            self.excess_qty = self.get_calculated_quantity('avg')
            self.minimum_stock_qty = round(float(self.average_qty * self.requisition_id.quantity) / 30)

    @api.one
    @api.onchange('adjustment_qty')
    def onchange_quantity(self):
        if self.product_id:
            self.product_required_qty = self.get_calculated_quantity('req')
            self.excess_qty = self.get_calculated_quantity('avg')

    @api.depends('product_id')
    def _compute_required_qty(self):
        for rec in self:
            if rec.product_id:
                no_of_days = self.last_day_of_month(rec.requisition_id.date, rec.requisition_id.period_id.date_stop)
                rec.required_qty = round(float(rec.average_qty * no_of_days) / 30)

    @api.depends('product_id')
    def _compute_stock_in_hand(self):
        for rec in self:
            if rec.product_id:
                location = rec.get_stock_location(rec.requisition_id.operating_unit_id.id)
                quant = rec.env['stock.quant'].search(
                    [('location_id', '=', location), ('product_id', '=', rec.product_id.id)])

                rec.stock_in_hand_qty = sum([rec.qty for rec in quant]) if quant else 0

    @api.depends('product_id')
    def _compute_average(self):
        for rec in self:
            if rec.product_id:
                rec.average_qty = rec.average_usage_per_month()

    @api.depends('product_id')
    def _compute_minimum_stock(self):
        for rec in self:
            if rec.product_id:
                rec.minimum_stock_qty = round(float(rec.average_qty * rec.requisition_id.quantity) / 30)

    @api.depends('product_id', 'adjustment_qty')
    def compute_product_required_qty(self):
        for rec in self:
            if rec.product_id:
                cal_qty = rec.required_qty + rec.adjustment_qty + rec.average_qty + rec.minimum_stock_qty - rec.stock_in_hand_qty
                rec.product_required_qty = cal_qty if cal_qty > 0 else 0

    @api.depends('product_id', 'adjustment_qty')
    def compute_excess_qty(self):
        for rec in self:
            if rec.product_id:
                cal_qty = rec.required_qty + rec.adjustment_qty + rec.average_qty + rec.minimum_stock_qty - rec.stock_in_hand_qty
                rec.excess_qty = round(cal_qty) if cal_qty < 0 else 0

    def average_usage_per_month(self):
        summary = self.env['product.usage.history'].search(
            [('product_id', '=', self.product_id.id),
             ('operating_unit_id', '=', self.requisition_id.operating_unit_id.id),
             ('period_id', '<', self.requisition_id.period_id.id)],
            order='period_id DESC', limit=12)
        sum, num = 0, 0
        for record in summary:
            if record.value:
                sum = sum + record.value
                num = num + 1
        return round(float(sum) / num) if num != 0 else 10

    def get_calculated_quantity(self, flag):

        if flag == 'req':
            cal_qty = self.required_qty + self.adjustment_qty + self.average_qty + self.minimum_stock_qty - self.stock_in_hand_qty
            return cal_qty if cal_qty > 0 else 0
        if flag == 'avg':
            cal_qty = self.required_qty + self.adjustment_qty + self.average_qty + self.minimum_stock_qty - self.stock_in_hand_qty
            cal_qty = round(float(cal_qty) / 30)
            return round(cal_qty) if cal_qty < 0 else 0
        if flag == 'min_req':
            no_of_days = self.last_day_of_month(self.requisition_id.date, self.requisition_id.period_id.date_stop)
            return round(float(self.average_qty * no_of_days) / 30)

    @api.model
    def get_stock_location(self, opu_id):
        location = self.env['stock.location'].search([('operating_unit_id', '=', opu_id)])
        return location.id

    def last_day_of_month(self, date, end_date):
        fmt = '%Y-%m-%d'
        date = self.env['account.period'].search([('date_start', '<=', date), ('date_stop', '>=', date)])
        d1 = datetime.strptime(date.date_stop, fmt)
        d2 = datetime.strptime(end_date, fmt)

        return (d2 - d1).days + 1
