from datetime import datetime

from openerp import api, fields, models


class BranchSelectionWizard(models.TransientModel):
    _name = 'branch.selection.wizard'

    @api.model
    def get_current_period(self):
        time = datetime.now()
        next_month = "{0}-{1}-01".format(time.year, time.month, time.day)
        next_period = self.env['account.period'].search(
            [('date_start', '>=', next_month), ('special', '=', False), ('state', '=', 'draft')], order='id ASC',
            limit=2)

        return next_period[1] if len(next_period) > 1 else next_month[0]

    operating_unit_id = fields.Many2one('operating.unit', string='Branch', required=True)
    period_id = fields.Many2one('account.period', string='Requisition For the Period', required=True,
                                domain="[('special','=',False),('state','=','draft')]",
                                default=get_current_period)

    @api.multi
    def select_branch(self, context=None):
        pr = self.env['purchase.requisition'].browse(context['active_id'])

        if pr:
            pr.write({'operating_unit_id': self.operating_unit_id.id,
                      'period_id': self.period_id.id,
                      'state': 'generate'})

        return {
            'view_type': 'form',
            'view_mode': 'form',
            'src_model': 'purchase.requisition',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'res_id': pr.id
        }
