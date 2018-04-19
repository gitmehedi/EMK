from odoo import models, fields, api

class DailyProduction(models.Model):
    _name = 'daily.production'


    section_id = fields.Many2one('mrp.section','Section', required=True)
    production_date = fields.Date('Date')
    finish_product_line_ids = fields.One2many('finish.product.line','daily_pro_id','Finish Produts')
    consumed_product_line_ids = fields.One2many('consumed.product.line','daily_pro_id','Consumed Products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft', track_visibility='onchange')


    @api.multi
    def action_consume(self):
        if self.finish_product_line_ids:
            for product in self.finish_product_line_ids:
                val = []
                bom_pool = self.env['mrp.bom'].search(
                    [('product_tmpl_id', '=', product.product_id.id)])

                for record in bom_pool.bom_line_ids:
                    if product.fnsh_product_qty:
                        val.append((0, 0, {'product_id': record.product_id.id,
                                           'con_product_qty': record.product_qty + product.fnsh_product_qty,
                                           }))
                    else:
                        val.append((0, 0, {'product_id': record.product_id.id,
                                           'con_product_qty': record.product_qty + product.fnsh_product_qty,
                                           }))

                self.consumed_product_line_ids = val



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