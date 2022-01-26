from odoo import api, fields, models, _


class UpdateLCNumberConfirmation(models.TransientModel):
    _name = 'update.import.lc.number.confirmation'

    lc_number = fields.Char(string='New LC Number')
    current_lc_number = fields.Char(string='Current LC Number', readonly=True)

    def action_yes(self):
        for rec in self:
            letter_of_credit_id = self._context['lc_id']
            letter_of_credit_obj = self.env['letter.credit'].browse(letter_of_credit_id)

            new_modified_lc_number = 'LC : ' + self.lc_number + '-' + letter_of_credit_obj.title + '-' + letter_of_credit_obj.operating_unit_id.name

            # search analytic account by this lc_number
            letter_of_credit_obj.write({'name': self.lc_number, 'unrevisioned_name': self.lc_number})
            analytic_account_name = 'LC : ' + self.current_lc_number + '-' + letter_of_credit_obj.title + '-' + letter_of_credit_obj.operating_unit_id.name

            analytic_account = self.env['account.analytic.account'].search([('name', '=', analytic_account_name)])

            if analytic_account:
                analytic_account.write({'name': new_modified_lc_number})
                letter_of_credit_obj.message_post(
                    body="LC number updated %s to %s" % (self.current_lc_number, self.lc_number))

            else:
                if letter_of_credit_obj.analytic_account_id:
                    letter_of_credit_obj.analytic_account_id.write({'name': new_modified_lc_number})
                    letter_of_credit_obj.message_post(
                        body="LC number updated %s to %s" % (self.current_lc_number, self.lc_number))
                else:
                    letter_of_credit_obj.message_post(
                        body="LC number updated %s to %s but Analytic Account not Found" % (
                            self.current_lc_number, self.lc_number))

        return {'type': 'ir.actions.act_window_close'}

    def action_no(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}
