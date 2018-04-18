from odoo import models, fields, api

class DailyProduction(models.Model):
    _name = 'daily.production'


    product_id = fields.Many2one('product.template', 'Product Name')
    section_id = fields.Many2one('mrp.section','Section', required=True)
    date = fields.Date('Date')
    finish_product_line_ids = fields.One2many('finish.product.line','daily_pro_id','Finish Produts')
    consumed_product_line_ids = fields.One2many('consumed.product.line','daily_pro_id','Consumed Products')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('reset', 'Reset To Draft'),
    ], string='Status', default='draft', track_visibility='onchange')

    @api.onchange('date')
    def default_date(self):
        if self.date:
            for finish_date in self.finish_product_line_ids:
                finish_date.date = self.date

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.date
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