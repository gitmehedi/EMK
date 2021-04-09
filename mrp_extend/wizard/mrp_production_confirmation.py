from odoo import api, fields, models, _


class MrpProductionConfirmation(models.TransientModel):
    _name = 'mrp.production.confirmation'
    _description = 'Production Confirmation'

    production_id = fields.Many2one('mrp.production')

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionConfirmation, self).default_get(fields)
        if 'production_id' in fields and self._context.get('active_id') and not res.get('production_id'):
            res = {'production_id': self._context['active_id']}
        return res

    @api.multi
    def _process(self, cancel_production=False):
        if cancel_production:
            self.production_id.write({'production_continue': False})

    @api.multi
    def process(self):
        self._process()

    @api.multi
    def process_cancel_production(self):
        self._process(cancel_production=True)
