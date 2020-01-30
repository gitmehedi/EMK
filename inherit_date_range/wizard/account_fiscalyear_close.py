from odoo import models, fields, api, _
from odoo.exceptions import Warning


class AccountFiscalyearClose(models.TransientModel):
    _name = "account.fiscalyear.close"
    _description = "Fiscal Year Close"

    @api.multi
    def default_journal(self):
        journal = self.env['account.journal'].search([('code', '=', 'FYC')])
        if not journal:
            raise Warning(_('Create a journal type with code [FYC]'))
        return journal

    close_fy_id = fields.Many2one('date.range', string='Current Fiscal Year', required=True,
                                  domain="[('state','=','approve'),('type_id.fiscal_year','=','True')]")
    start_fy_id = fields.Many2one('date.range', string='New Fiscal Year', required=True,
                                  domain="[('state','=','approve'),('type_id.fiscal_year','=','True')]")
    journal_id = fields.Many2one('account.journal', string='Journal Type', readonly=True,
                                 default=default_journal, domain="[('type','=','general')]", required=True)
    period_id = fields.Many2one('date.range', string='Opening Entries Period', required=False)
    report_name = fields.Char(string='Name of new entries', required=False, help="Give name of the new entries")

    @api.multi
    def data_save(self):
        curr_date = fields.Date.today()
        start_fy_dst = self.start_fy_id.date_start
        start_fy_ded = self.start_fy_id.date_end
        end_fy_dst = self.close_fy_id.date_start
        end_fy_ded = self.close_fy_id.date_end
        company_id = self.env.user.company_id.id
        journal_id = self.journal_id.id
        user_id = self.env.user.id
        opu_id = self.env.user.default_operating_unit_id.id

        if self.start_fy_id.id == self.close_fy_id.id:
            raise Warning(_("Close Fiscal Year and Start Fiscal Year shouldn\'t be same."))

        # if (curr_date < end_fy_dst) or (curr_date > end_fy_ded):
        #     raise Warning(_("Closing Fiscal Year should be current year."))

        opening_bal = self.env['account.move'].search([('journal_id.code', '=', 'FYC'), ('state', '=', 'draft')])
        if opening_bal:
            raise Warning(_("A closing balace journal exist. Please remove it first."))

        if self.env.user.company_id.eoy_type == 'banking':
            self.env.cr.execute("""SELECT * FROM profit_loss_calculation('%s','%s','%s',%s,%s,%s,%s)""" % (
                end_fy_dst, end_fy_ded, end_fy_ded, user_id, journal_id, opu_id, company_id));
            move_id = self.env.cr.fetchall()
            move_ins = self.env['account.move'].search([('id', '=', move_id)])
            if move_ins:
                move_ins.post()
                if move_ins.state == 'posted':
                    self.env.cr.execute("""SELECT * FROM financial_year_closing('%s','%s','%s',%s,%s,%s,%s)""" % (
                        end_fy_dst, end_fy_ded, start_fy_dst, user_id, journal_id, opu_id, company_id));
        else:
            move_id = self.env.cr.execute("""SELECT * FROM financial_year_closing('%s','%s','%s',%s,%s,%s,%s)""" % (
                end_fy_dst, end_fy_ded, start_fy_dst, user_id, journal_id, opu_id, company_id));
            self.env.cr.execute("""SELECT * FROM profit_loss_calculation('%s','%s','%s',%s,%s,%s,%s)""" % (
                end_fy_dst, end_fy_ded, start_fy_ded, user_id, journal_id, opu_id, company_id));

        return {'type': 'ir.actions.act_window_close'}
