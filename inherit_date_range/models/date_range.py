from odoo import api, fields, models, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class DateRange(models.Model):
    _name = "date.range"
    _order = 'name desc'
    _inherit = ['date.range', 'mail.thread']
    _description = 'Account Period'

    @api.model
    def _default_company(self):
        return self.env['res.company']._company_default_get('date.range')

    name = fields.Char('Name', required=True, size=200, track_visibility='onchange', readonly=True,
                       states={'draft': [('readonly', False)]}, translate=True)
    pending = fields.Boolean(string='Pending', default=True, track_visibility='onchange', readonly=True,
                             states={'draft': [('readonly', False)]})
    active = fields.Boolean(string='Active', default=False, track_visibility='onchange', readonly=True,
                            states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('approve', 'Approved'), ('close', 'Close'), ('reject', 'Rejected')],
                             default='draft', string='Status', track_visibility='onchange')
    date_start = fields.Date(string='Start Date', required=True, readonly=True,
                             states={'draft': [('readonly', False)]})
    date_end = fields.Date(string='End Date', required=True, readonly=True,
                           states={'draft': [('readonly', False)]})
    line_ids = fields.One2many('history.date.range', 'line_id', string='Lines', readonly=True,
                               states={'draft': [('readonly', False)]})
    maker_id = fields.Many2one('res.users', 'Maker', default=lambda self: self.env.user.id, track_visibility='onchange')
    approver_id = fields.Many2one('res.users', 'Checker', track_visibility='onchange')

    @api.model_cr
    def init(self):
        self._cr.execute("""
                    CREATE OR REPLACE FUNCTION financial_year_closing(date DATE,user_id INTEGER,journal_id INTEGER,opu_id INTEGER,company_id INTEGER) 
                    RETURNS INTEGER AS $$
                    DECLARE
                    mrec RECORD;
                    forward_query TEXT;
                    reconcile_query TEXT;
                    move INTEGER;
                    level INTEGER;
                    user_id INTEGER;
                    depr_date DATE;
                    depr_amount FLOAT;
                    BEGIN
                    depr_date = date;
                    user_id = user_id;
                    journal_id = journal_id;
                    opu_id = opu_id;
                    company_id =company_id;

                    INSERT INTO account_move (name,ref,journal_id,company_id,date,operating_unit_id,user_id,state,is_cbs,is_sync,is_cr,create_uid,write_uid,create_date,write_date) 
                        VALUES ('/','Financial year closing depreciation date '||CURRENT_DATE ,journal_id,company_id,CURRENT_DATE,opu_id,user_id,'draft',False,False,TRUE,user_id,user_id,NOW(),NOW())
                        RETURNING account_move.id INTO move;

                    forward_query = 'SELECT journal_id,
                           currency_id,
                           analytic_account_id,
                           account_id,
                           operating_unit_id,
                           servicing_channel_id,
                           acquiring_channel_id,
                           segment_id,
                           SUM(amount_residual) AS amount_residual,
                           SUM(debit) AS debit,
                           SUM(credit) AS credit,
                           SUM(amount_currency) AS amount_currency
                     FROM account_move_line
                     WHERE account_id IN (SELECT aa.id
                        FROM account_account aa
                        LEFT JOIN account_account_type as aat
                             ON (aa.user_type_id = aat.id)
                        LEFT JOIN account_account_level aal
                             ON (aal.id = aa.level_id)
                        WHERE aat.include_initial_balance = TRUE
                              AND aa.level_id=6)
                     GROUP BY journal_id,
                          currency_id,
                          analytic_account_id,
                          account_id,
                          operating_unit_id,
                          servicing_channel_id,
                          acquiring_channel_id,
                          segment_id';


                    FOR mrec IN EXECUTE forward_query
                    LOOP
                      IF mrec.debit >0 and mrec.credit >0 THEN
                          -- insert credit amount in account.move.line
                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date)
                          VALUES ('Depreciation in '|| depr_date,'Depreciation',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,depr_date,depr_date,mrec.credit,0,user_id,user_id,NOW(),NOW());
                          -- insert debit amount in account.move.line
                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date)
                          VALUES ('Depreciation in '|| depr_date,'Depreciation',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,depr_date,depr_date,0,mrec.debit,user_id,user_id,NOW(),NOW());
                      END IF;
                    END LOOP;

                    reconcile_query = 'SELECT journal_id,
                           currency_id,
                           analytic_account_id,
                           account_id,
                           operating_unit_id,
                           servicing_channel_id,
                           acquiring_channel_id,
                           segment_id,
                           SUM(amount_residual) AS amount_residual,
                           SUM(debit) AS debit,
                           SUM(credit) AS credit,
                           SUM(amount_currency) AS amount_currency
                     FROM account_move_line
                     WHERE account_id IN (SELECT aa.id
                        FROM account_account aa
                        WHERE aa.reconcile = TRUE
                              AND aa.level_id=6)
                     GROUP BY journal_id,
                          currency_id,
                          analytic_account_id,
                          account_id,
                          operating_unit_id,
                          servicing_channel_id,
                          acquiring_channel_id,
                          segment_id';

                    FOR mrec IN EXECUTE reconcile_query
                    LOOP
                          IF mrec.debit > 0 and mrec.credit > 0 THEN
                              -- insert credit amount in account.move.line
                              INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date)
                              VALUES ('Depreciation in '|| depr_date,'Depreciation',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,depr_date,depr_date,mrec.credit,0,user_id,user_id,NOW(),NOW());
                                  -- insert debit amount in account.move.line
                              INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date)
                              VALUES ('Depreciation in '|| depr_date,'Depreciation',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,depr_date,depr_date,0,mrec.debit,user_id,user_id,NOW(),NOW());
                          END IF;
                    END LOOP;
                RETURN move;
                END;
            $$ LANGUAGE plpgsql;
            """)
    @api.one
    def act_draft(self):
        if self.state == 'reject':
            self.write({
                'state': 'draft',
                'pending': True,
                'active': False,
            })

    @api.one
    def act_approve(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Maker and Approver can't be same person!"))
        if self.state == 'draft':
            self.write({
                'state': 'approve',
                'pending': False,
                'active': True,
                'approver_id': self.env.user.id,
            })

    @api.one
    def act_reject(self):
        if self.state == 'draft':
            self.write({
                'state': 'reject',
                'pending': False,
                'active': False,
            })

    @api.one
    def act_approve_pending(self):
        if self.env.user.id == self.maker_id.id and self.env.user.id != SUPERUSER_ID:
            raise ValidationError(_("[Validation Error] Editor and Approver can't be same person!"))
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.write({
                    'name': self.name if not requested.change_name else requested.change_name,
                    'pending': False,
                    'active': requested.status,
                    'approver_id': self.env.user.id,
                })
                requested.write({
                    'state': 'approve',
                    'change_date': fields.Datetime.now()
                })

    @api.one
    def act_reject_pending(self):
        if self.pending == True:
            requested = self.line_ids.search([('state', '=', 'pending'), ('line_id', '=', self.id)], order='id desc',
                                             limit=1)
            if requested:
                self.write({
                    'pending': False
                })
                requested.write({
                    'state': 'reject',
                    'change_date': fields.Datetime.now()
                })

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state in ('approve', 'reject'):
                raise ValidationError(_('[Warning] Approves and Rejected record cannot be deleted.'))

            try:
                return super(DateRange, rec).unlink()
            except DateRange:
                raise ValidationError(_("The operation cannot be completed, probably due to the following:\n"
                                        "- deletion: you may be trying to delete a record while other records still reference it"))

    @api.constrains('name')
    def _check_unique_constrain(self):
        if self.name:
            name = self.search(
                [('name', '=ilike', self.name.strip()), ('state', '!=', 'reject'), '|', ('active', '=', True),
                 ('active', '=', False)])
            if len(name) > 1:
                raise Warning('[Unique Error] Name must be unique!')

    @api.onchange("name", )
    def onchange_strips(self):
        if self.name:
            self.name = self.name.strip()

    @api.one
    def name_get(self):
        name = self.name
        if self.name and self.date_start and self.date_end:
            name = '[%s - %s] %s' % (self.date_start, self.date_end, self.name)
        return (self.id, name)


class HistoryAccountPeriod(models.Model):
    _name = 'history.date.range'
    _description = 'History Account Period'
    _order = 'id desc'

    change_name = fields.Char('Proposed Name', size=200, readonly=True, states={'draft': [('readonly', False)]})
    status = fields.Boolean('Active', default=True, track_visibility='onchange')
    request_date = fields.Datetime(string='Requested Date')
    change_date = fields.Datetime(string='Approved Date')
    line_id = fields.Many2one('date.range', ondelete='restrict')
    state = fields.Selection([('pending', 'Pending'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             default='pending', string='Status')
