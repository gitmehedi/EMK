from odoo import models, fields, api

class DailyProduction(models.Model):
    _name = 'daily.production'

    name = fields.Char('Name',required=True)
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