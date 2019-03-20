from odoo import models, fields, api

class DailyProduction(models.Model):
    _name = 'daily.production'


    section_id = fields.Many2one('mrp.section','Section', required=True)
    production_date = fields.Date('Date' ,required=True)
    finish_product_line_ids = fields.One2many('finish.product.line','daily_pro_id','Finish Produts')
    consumed_product_line_ids = fields.One2many('consumed.product.line','daily_pro_id','Consumed Products')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', required=True,
                                        default=lambda self: self.env.user.default_operating_unit_id)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft', track_visibility='onchange')


    @api.multi
    def action_consume(self):

        ############### Delete Existing Records ##########################################
        if self.id:
            self.env["consumed.product.line"].search([('daily_pro_id', '=', self.id)]).unlink()

        consumeProductMap = {}
        if self.finish_product_line_ids:
            for product in self.finish_product_line_ids:
                product.finish_product_date = self.production_date
                self.buildConsumeProducts(product,consumeProductMap)

            consumed_product_list = []
            for i, key in enumerate(consumeProductMap):
                consumeProductValue = consumeProductMap.get(key)
                consumed_product_list.append((0, 0, {'product_id': consumeProductValue['product_id'],
                                   'con_product_qty': consumeProductValue['con_product_qty'],
                                    'consumed_product_date' :  consumeProductValue['consumed_product_date']
                                   }))

            self.consumed_product_line_ids = consumed_product_list

    def buildConsumeProducts(self,product,consumeProductMap):

        bom_pool = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_id.id)])
        for record in bom_pool.bom_line_ids:
            consumeProduct = consumeProductMap.get(record.product_id.id)
            if consumeProduct:
                consumeProduct['con_product_qty'] = consumeProduct[
                                                        'con_product_qty'] + record.product_qty * product.fnsh_product_qty
            else:
                consumeProductMap[record.product_id.id] = {'product_id': record.product_id.id,
                                                           'con_product_qty': record.product_qty * product.fnsh_product_qty,
                                                           'consumed_product_date':self.production_date}

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.production_date
            if record.section_id:
                name = "%s [%s]" % (record.section_id.name_get()[0][1],name)
            result.append((record.id, name))
        return result

    @api.one
    def action_reset(self):
        self.state = 'draft'
        self.finish_product_line_ids.write({'state': 'draft'})
        self.consumed_product_line_ids.write({'state': 'draft'})

    @api.one
    def action_confirm(self):
        self.state = 'confirmed'
        self.finish_product_line_ids.write({'state': 'confirmed'})
        self.consumed_product_line_ids.write({'state': 'confirmed'})

    @api.one
    def action_approved(self):
        self.state = 'approved'
        self.finish_product_line_ids.write({'state': 'approved'})
        self.consumed_product_line_ids.write({'state': 'approved'})