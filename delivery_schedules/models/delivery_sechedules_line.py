import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError



class DeliveryScheduleLine(models.Model):
    _name = 'delivery.schedules.line'
    _inherit = ['mail.thread']
    _description = 'Delivery Schedule line'

    partner_id = fields.Many2one('res.partner', 'Customer', domain=[('customer', '=', True),('parent_id', '=', False)],
                                 readonly=True, states={'draft': [('readonly', False)]})
    # pending_picking = fields.Many2one('stock.picking', string='Pending Picking')
    pending_do = fields.Many2one('delivery.order', ondelete='cascade',
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 string='Pending D.O',track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product',
                                 readonly=True, states={'draft': [('readonly', False)]},
                                 track_visibility='onchange')
    do_qty = fields.Float(string='Ordered Qty', readonly=True ,store=True,compute='onchange_product_id')
    undelivered_qty = fields.Float(string='Undelivered Qty', readonly=True)
    uom_id = fields.Many2one('product.uom', string="Unit of Measure", readonly=True)
    scheduled_qty = fields.Float(string='Scheduled Qty.', readonly=True,
                                 states={'draft': [('readonly', False)],'revision': [('readonly', False)]},
                                 track_visibility='onchange')
    remarks = fields.Text('Special Instructions', readonly=True,
                          states={'draft': [('readonly', False)],'revision': [('readonly', False)]},
                          track_visibility='onchange')
    requested_date = fields.Date('Date', default=datetime.date.today(), readonly=True)
    # Relational Fields
    parent_id = fields.Many2one('delivery.schedules', ondelete='cascade')
    state = fields.Selection([
        ('draft', "Draft"),
        ('revision', "Revision"),
        ('approve', "Confirm"),
        ('done', "Done"),
    ], default='draft', track_visibility='onchange')

    @api.model
    def _default_operating_unit(self):
        team = self.env['crm.team']._get_default_team_id()
        if team.operating_unit_id:
            return team.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit',
                                        string='Operating Unit',
                                        required=True,
                                        default=_default_operating_unit)

    schedule_line_date = fields.Date('Date', default=datetime.date.today(),)

    @api.model
    def create(self, vals):
        line_obj = self.env['delivery.order.line'].search(
            [('parent_id', '=', vals['pending_do']), ('product_id', '=', vals['product_id'])])
        vals['do_qty'] = line_obj.quantity
        vals['undelivered_qty'] = line_obj.quantity - line_obj.qty_delivered
        vals['uom_id'] = line_obj.uom_id.id
        return super(DeliveryScheduleLine, self).create(vals)


    @api.multi
    def write(self, vals):
        line_obj = self.env['delivery.order.line'].search(
            [('parent_id', '=', self.pending_do.id), ('product_id', '=', self.product_id.id)])
        vals['do_qty'] = line_obj.quantity
        vals['undelivered_qty'] = line_obj.quantity - line_obj.qty_delivered
        vals['uom_id'] = line_obj.uom_id.id
        return super(DeliveryScheduleLine, self).write(vals)

    @api.multi
    def unlink(self):
        for entry in self:
            if entry.state != 'draft':
                raise UserError(_('After confirmation You can not delete this.'))
        return super(DeliveryScheduleLine, self).unlink()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        for ds in self:
            ds.pending_do = []
            ds.product_id = []
            do_id_list = []
            if ds.partner_id:
                do_objs = self.env['delivery.order'].sudo().search([('parent_id','=',ds.partner_id.id),
                                                                    ('operating_unit_id','=',self.operating_unit_id.id),
                                                                    ('state','=','approved')])
                if do_objs:
                    for do_obj in do_objs:
                        do_line_list =  do_obj.line_ids.filtered(lambda x: x.quantity > x.qty_delivered)
                        if do_line_list:
                            do_id_list.append(do_obj.id)
                return {'domain': {'pending_do': [('id', 'in', do_id_list)]}}

    @api.onchange('pending_do')
    def onchange_pending_do(self):
        if self.pending_do:
            # For the time being no loop, test purpose
            if len(self.pending_do.line_ids) == 1:
                self.product_id = self.pending_do.line_ids[0].product_id
                self.do_qty = self.pending_do.line_ids[0].quantity
                self.undelivered_qty = self.pending_do.line_ids[0].quantity - self.pending_do.line_ids[0].qty_delivered
                self.uom_id = self.pending_do.line_ids[0].uom_id

                return {'domain': {'product_id': [('id', '=', self.product_id.id)]}}
            else:
                product_list = []
                for line in self.pending_do.line_ids:
                    product_list.append(line.product_id.id)
                return {'domain': {'product_id': [('id', 'in', product_list)]}}

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.do_qty = False
        self.undelivered_qty = False
        self.uom_id = False
        self.scheduled_qty = False
        self.remarks = False
        if self.product_id:
            line_obj = self.env['delivery.order.line'].search(
                [('parent_id', '=', self.pending_do.id), ('product_id', '=', self.product_id.id)])[0]
            self.do_qty = line_obj.quantity
            self.undelivered_qty = line_obj.quantity - line_obj.qty_delivered
            self.uom_id = line_obj.uom_id

    @api.multi
    def action_approve(self):
        self.write({'state': 'done',})

    @api.constrains('scheduled_qty')
    def _check_scheduled_qty(self):
        if self.scheduled_qty > self.do_qty:
            raise Warning('Schedule date can not bigger then Delivery Quantity!')