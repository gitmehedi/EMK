from odoo import api, fields, models,_

class AmendmentWizard(models.TransientModel):
    _name = 'lc.amendment.wizard'

    amendment_date = fields.Date('Amendment Date', required=True)

    @api.multi
    def save_action(self):

        form_id = self.env.context.get('active_id')
        lc_pool = self.env['letter.credit']
        lc_obj = lc_pool.search([('id', '=', form_id)])
        if lc_obj:
            return lc_obj.action_revision_export(self.amendment_date)
