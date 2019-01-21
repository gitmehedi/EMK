from odoo import models, fields, api
import time
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class creditlimit_partners(models.TransientModel):
    _name ='creditlimit.partners'
    _description = 'Generate creditlimit for all selected partners'
    _order = 'id'

    partner_ids = fields.Many2many('res.partner', 'partner_limit_group_rel', 'limit_id', 'partner_id')

    @api.multi
    def compute_sheet(self):
        partner_pool = self.env['res.partner']
        limit_pool = self.env['res.partner.credit.limit']
        run_pool = self.env['customer.creditlimit.assign']

        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            run_data = run_pool.browse(active_id)
        limit_data = run_data.credit_limit or 0
        day_data = run_data.days or 0
        assign_id = run_data.id or False
        assign_date = time.strftime('%Y-%m-%d')
        # i = 1
        if not data['partner_ids']:
             raise UserError(_("You must select customer(s) to generate limit(s)."))
        for partner in partner_pool.browse((data['partner_ids'])):
            res = {
                # 'sl_num': i,
                'partner_id': partner.id,
                'assign_date': assign_date,
                'value': limit_data,
                'day_num': day_data,
                'assign_id':assign_id,
                'state': 'draft',
            }
            # i+=1

            limit_pool.create(res)

        return {'type': 'ir.actions.act_window_close'}



