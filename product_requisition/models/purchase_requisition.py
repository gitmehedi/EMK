from datetime import datetime
from openerp import api, models, fields


class PurchaseRequisitionModel(models.Model):
    _name = 'purchase.requisition'
    _description = 'Model stores all requisition data which comes different branch.'

    @api.model
    def _default_operating_unit(self):
        return self.env.user.default_operating_unit_id

    quantity = fields.Integer(string='Minumum Stock Leve in Day\'s Usage',
                              related='operating_unit_id.min_stock_days',
                              readonly=True, states={'generate': [('readonly', False)]})
    date = fields.Date(string='Requisition Preparation Date', required=True, default=datetime.now())

    """ Relational Filds """

    period_id = fields.Many2one('account.period', string='Requisition For the Period', readonly=True)
    operating_unit_id = fields.Many2one('operating.unit', string='Branch', readonly=True)

    line_ids = fields.One2many('purchase.requisition.line', 'requisition_id',
                               readonly=True, states={'generate': [('readonly', False)]})

    state = fields.Selection([('draft', 'Draft'), ('generate', 'Generate'), ('submit', 'Submitted')], default='draft')

    @api.one
    def generate_action(self):
        if self.period_id and self.state == 'generate':
            self.line_ids.unlink()
            self.env.cr.execute("""
                    SELECT 
                         prl.product_id,
                         sum(prl.product_required_qty)
                    FROM product_requisition pr
                    INNER JOIN product_requisition_line prl
                        ON(prl.requisition_id=pr.id)
                    WHERE pr.period_id= %s AND pr.state='submit'
                    GROUP BY prl.product_id
                    ORDER BY prl.product_id ASC
                    """, (self.period_id.id,))
            for rec in self.env.cr.dictfetchall():
                record = {}
                record['product_id'] = rec['product_id']

                product = self.env['product.product'].search([('id', '=', rec['product_id'])])
                record['unit_price'] = product.uom_id.id
                record['supplier_id'] = product.seller_ids[0].name.id if len(product.seller_ids)>0 else None
                record['requisition_id'] = self.id

                self.line_ids.create(record)

    @api.one
    def name_get(self):
        name = self.operating_unit_id
        if self.operating_unit_id and self.period_id:
            name = '%s - %s' % (self.period_id.name, self.operating_unit_id.name)
        return (self.id, name)

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_submit(self):
        if self.state == 'generate':
            self.state = 'submit'


class PurchaseRequisitionLineModel(models.Model):
    _name = 'purchase.requisition.line'
    _description = 'Model stores all requisition data which comes different branch.'

    stock_in_hand_qty = fields.Integer(string='On Hand Qty')
    required_qty = fields.Integer(string='Remaining Period Qty')
    adjustment_qty = fields.Integer(string='Seasonal Adjustment')
    average_qty = fields.Integer(string='Average Usage per Month', compute='_compute_average', store=True)
    minimum_stock_qty = fields.Integer(string='Minimum Stock Qty', compute='_compute_minimum_stock', store=True)
    total_branch_qty = fields.Integer(string='Branch Requisition', compute='_compute_total_branch_qty',
                                      store=True)
    product_required_qty = fields.Integer(string='Product Required', store=True, compute='compute_product_required_qty')
    excess_qty = fields.Integer(string='Excess Qty', store=True, compute='compute_excess_qty')
    purchase_qty = fields.Integer(string='Purchase Qty')

    """ Relational Filds """
    product_id = fields.Many2one('product.product', string='Product-Description', required=True)
    uom_id = fields.Many2one(related='product_id.uom_id', string='UoM', default="compute_uom")
    unit_price = fields.Float('Unit Price')
    sub_total = fields.Float('Sub Total', compute='_compute_sub_total')

    supplier_id = fields.Many2one('res.partner', domain=[('is_supplier', '=', '1')])
    requisition_id = fields.Many2one('purchase.requisition', ondelete='cascade')

    @api.onchange('product_id')
    @api.one
    def onchange_product(self):
        if self.product_id:
            self.minimum_stock_qty = self.get_minimum_stock()

            quant = self.env['stock.quant'].search(
                [('location_id', '=', self.get_stock_location()),
                 ('product_id', '=', self.product_id.id)])

            self.stock_in_hand_qty = quant.qty if quant else 0
            self.minimum_stock_qty = self.get_minimum_stock()
            self.product_required_qty = self.get_calculated_quantity('req')
            self.excess_qty = self.get_calculated_quantity('avg')
            self.total_branch_qty = self.get_product_sum(self.requisition_id.period_id.id, self.product_id)
            self.unit_price = self.product_id.list_price
            self.sub_total = self.product_id.list_price * self.purchase_qty

            self.supplier_id = self.product_id.id

    @api.one
    @api.onchange('required_qty', 'adjustment_qty')
    def onchange_quantity(self):
        if self.product_id:
            self.product_required_qty = self.get_calculated_quantity('req')
            self.excess_qty = self.get_calculated_quantity('avg')

    @api.depends('product_id')
    def _compute_stock_in_hand(self):
        for rec in self:
            quant = rec.env['stock.quant'].search(
                [('location_id', '=', rec.get_stock_location()),
                 ('product_id', '=', rec.product_id.id)])

            rec.stock_in_hand_qty = quant.qty if quant else 0

    @api.depends('product_id')
    def _compute_minimum_stock(self):
        for rec in self:
            rec.minimum_stock_qty = rec.get_minimum_stock()

    @api.depends('product_id')
    def _compute_average(self):
        for rec in self:
            rec.average_qty = rec.average_usage()

    @api.depends('product_id')
    def _compute_total_branch_qty(self):
        for rec in self:
            if rec.requisition_id and rec.product_id:
                rec.total_branch_qty = self.get_product_sum(rec.requisition_id.period_id.id, rec.product_id.id)

    @api.depends('product_id', 'required_qty', 'adjustment_qty')
    def compute_product_required_qty(self):
        for rec in self:
            rec.product_required_qty = rec.get_calculated_quantity('req')

    @api.depends('product_id')
    def _compute_sub_total(self):
        for rec in self:
            rec.sub_total = rec.product_id.list_price * rec.purchase_qty

    @api.depends('product_id', 'required_qty', 'adjustment_qty')
    def compute_excess_qty(self):
        for rec in self:
            rec.excess_qty = rec.get_calculated_quantity('avg')


    def get_minimum_stock(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.requisition_id.operating_unit_id.id)])
        if location:
            min_qty = self.env['stock.warehouse.orderpoint'].search(
                [('location_id', '=', location.id), ('product_id', '=', self.product_id.id)])
            return min_qty.product_min_qty if min_qty else 0

    def average_usage(self):
        periods = self.env['account.period'].search([('date_start', '<', self.requisition_id.period_id.date_start),
                                                     ('special', '=', False), ('state', '=', 'draft')],
                                                    order='id desc', limit=12)
        period = [val.code for val in periods]
        summary = self.env['product.usage.history'].search(
            [('product_id', '=', self.product_id.id), ('period_id', 'in', period)],
            order='period_id DESC')
        sum, num = 0, 0
        for record in summary:
            if record.value:
                sum = sum + record.value
                num = num + 1
        return round(float(sum) / len(periods)) if num != 0 else 10

    def get_calculated_quantity(self, flag):
        cal_qty = self.required_qty + self.adjustment_qty + self.average_qty + self.minimum_stock_qty + self.total_branch_qty - self.stock_in_hand_qty
        if flag == 'req':
            return cal_qty if cal_qty > 0 else 0
        if flag == 'avg':
            return round(cal_qty) if cal_qty < 0 else 0

    @api.model
    def get_stock_location(self):
        location = self.env['stock.location'].search(
            [('operating_unit_id', '=', self.requisition_id.operating_unit_id.id)])
        return location.id

    @api.model
    def get_product_sum(self, period, product):
        self.env.cr.execute("""
                    SELECT 
                    prl.product_id,
                    sum(prl.product_required_qty) AS total
                    FROM product_requisition pr
                        INNER JOIN product_requisition_line prl
                            ON(prl.requisition_id=pr.id)
                    WHERE pr.period_id= %s AND pr.state='submit' AND prl.product_id = %s
                    GROUP BY prl.product_id
                    ORDER BY prl.product_id ASC
                    """, (period, product,))
        for rec in self.env.cr.dictfetchall():
            return rec['total']
