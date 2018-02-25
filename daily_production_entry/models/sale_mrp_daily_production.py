from odoo import api, fields, models, exceptions, _

class MrpDailyProduction(models.Model):
    _name = 'mrp.daily.production'
    _description = 'MRP daily production'

    name = fields.Char(size=100, string="Production Details", required=True,readonly=True,states={'draft': [('readonly', False)]})
    production_date = fields.Date('Production Date', readonly=True,required=True,states={'draft': [('readonly', False)]})

    """ All relations fields """
    line_ids = fields.One2many('mrp.daily.production.line', 'parent_id', string="Products", readonly=True,
                               states={'draft': [('readonly', False)]})

    """ All Selection fields """
    state = fields.Selection([
        ('draft', "Draft"),
        ('applied',"Applied"),
        ('refused',"Refused"),
        ('approved', "Approved"),
    ], default='draft')

    """All function which process data and operation"""

    @api.multi
    def action_refuse(self):
        self.state = 'refused'

    @api.multi
    def action_confirm(self):
        self.state = 'applied'

    @api.multi
    def action_done(self):
        self.state = 'approved'
