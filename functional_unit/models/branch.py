from odoo import api, fields, models, _


class ResBranch(models.Model):
    _name = 'res.branch'
    _description = 'Functional Unit'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company')
    telephone = fields.Char(string='Telephone No')
    address = fields.Text('Address')
    logo = fields.Binary(string="Branch Logo")
    vat = fields.Char(string="Tax ID")
    email = fields.Char(string="Email")
    website = fields.Char(string="Website")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if self._context.get('branch_id'):
            recs = self.search([('id', 'in', self.env.user.branch_ids.ids)] + args, limit=limit)
            return recs.name_get()
        return super(ResBranch, self).name_search(name=name, args=args, operator=operator, limit=limit)
