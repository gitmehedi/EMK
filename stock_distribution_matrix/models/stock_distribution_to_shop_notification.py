from openerp import api, fields, models
from openerp.osv import osv
class stock_distribution_to_shop_notification(models.TransientModel):
    _name = 'stock.distribution.to.shop.notification'
    notification_date = fields.Date(string='Notification Date', default=fields.Date.today, required=True)
    @api.multi
    def action_set_notification(self):
        active_ids = self.env.context.get('active_ids', []) or []
        proxy = self.env['stock.distribution.to.shop']
        for record in proxy.search([('id', 'in', active_ids)]):
            if record.state not in ('draft'):
                raise osv.except_osv(_('Warning!'), _("Selected Data cannot be accessible as they are not in 'Draft' state."))
            record.notification_date=self.notification_date
        return {'type': 'ir.actions.act_window_close'}