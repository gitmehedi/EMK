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
                    CREATE OR REPLACE FUNCTION financial_year_closing(dt_start DATE,dt_end DATE,date DATE,user_id INTEGER,journal_id INTEGER,opu_id INTEGER,company_id INTEGER) 
                        RETURNS INTEGER AS $$
                        DECLARE
                        mrec RECORD;
                        crec RECORD;
                        forward_query TEXT;
                        company_query TEXT;
                        reconcile_query TEXT;
                        move INTEGER;
                        level INTEGER;
                        user_id INTEGER;
                        jrn_date DATE;
                        date_start DATE;
                        date_end DATE;
                        depr_amount FLOAT;
                        retain_earning_id INTEGER;
                        profit_fy_id INTEGER;
                        sum FLOAT;
                        BEGIN
                        jrn_date = date;
                        date_start = dt_start;
                        date_end = dt_end;
                        user_id = user_id;
                        journal_id = journal_id;
                        opu_id = opu_id;
                        company_id = company_id;
                        sum = 0;
                    
                        INSERT INTO account_move (name,ref,journal_id,company_id,date,operating_unit_id,user_id,state,is_cbs,is_sync,is_cr,is_opening,create_uid,write_uid,create_date,write_date) 
                        VALUES ('/','Year Closing between date '|| date_start ||' and '|| date_end,journal_id,company_id,jrn_date,opu_id,user_id,'draft',TRUE,False,TRUE,TRUE,user_id,user_id,NOW(),NOW())
                        RETURNING account_move.id INTO move;
                    
                        forward_query = format('SELECT aml.journal_id,
                                    aml.currency_id,
                                    aml.analytic_account_id,
                                    aml.account_id,
                                    aml.operating_unit_id,
                                    aml.servicing_channel_id,
                                    aml.acquiring_channel_id,
                                    aml.segment_id,
                                    SUM(aml.amount_residual) AS amount_residual,
                                    SUM(aml.debit) AS debit,
                                    SUM(aml.credit) AS credit,
                                    SUM(aml.amount_currency) AS amount_currency
                                FROM account_move am
                                LEFT JOIN account_move_line aml
                                       ON (am.id = aml.move_id)
                                WHERE am.is_cbs=TRUE
                                      AND aml.date BETWEEN $1 AND $2
                                      AND aml.account_id IN (SELECT aa.id
                                    FROM account_account aa
                                    LEFT JOIN account_account_type aat
                                         ON (aa.user_type_id = aat.id)
                                    LEFT JOIN account_account_level aal
                                         ON (aal.id = aa.level_id)
                                    WHERE aat.include_initial_balance = TRUE
                                          AND aa.level_id=6)
                                GROUP BY aml.journal_id,
                                    aml.currency_id,
                                    aml.analytic_account_id,
                                    aml.account_id,
                                    aml.operating_unit_id,
                                    aml.servicing_channel_id,
                                    aml.acquiring_channel_id,
                                    aml.segment_id
                                ORDER BY aml.account_id ASC');
                    
                        --RAISE NOTICE '%-%-%-%', jrn_date,date_start,date_end,forward_query;
                        company_query = format('SELECT eoy_type, 
                                           retain_earning_id, 
                                           profit_fy_id
                                    FROM res_company 
                                    WHERE id=$1');
                    
                        FOR crec IN EXECUTE company_query USING company_id
                        LOOP
                            retain_earning_id = crec.retain_earning_id;
                            profit_fy_id = crec.profit_fy_id;
                        END LOOP;
                        
                        FOR mrec IN EXECUTE forward_query USING date_start,date_end
                        LOOP
                          IF mrec.account_id = profit_fy_id THEN
                                mrec.account_id = retain_earning_id;
                          END IF;
                         
                          IF mrec.debit > 0 or mrec.credit > 0 THEN
                              sum= sum + ABS(mrec.debit);
                              
                              INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_opening)
                              VALUES ('Year Closing between Date '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,mrec.debit,0,user_id,user_id,NOW(),NOW(),TRUE);
                            
                              INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_opening)
                              VALUES ('Year Closing Between Date '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,0,mrec.credit,user_id,user_id,NOW(),NOW(),TRUE);
                          END IF;
                        END LOOP;
                    
                        UPDATE account_move SET amount=sum WHERE id=move;
                    
                    RETURN move;
                    END;
                    $$ LANGUAGE plpgsql;
            """)

        self._cr.execute("""
                    CREATE OR REPLACE FUNCTION profit_loss_calculation(dt_start DATE,dt_end DATE,date DATE,user_id INTEGER,journal_id INTEGER,opu_id INTEGER,company_id INTEGER) 
                        RETURNS INTEGER AS $$
                        DECLARE
                        mrec RECORD;
                        crec RECORD;
                        forward_query TEXT;
                        company_query TEXT;
                        reconcile_query TEXT;
                        move INTEGER;
                        level INTEGER;
                        user_id INTEGER;
                        jrn_date DATE;
                        date_start DATE;
                        date_end DATE;
                        eoy_type TEXT;
                        general_id INTEGER;
                        profit_fy_id INTEGER;
                        credit FLOAT;
                        debit FLOAT;
                        sum FLOAT;
                        BEGIN
                        jrn_date = date;
                        date_start = dt_start;
                        date_end = dt_end;
                        user_id = user_id;
                        journal_id = journal_id;
                        opu_id = opu_id;
                        company_id = company_id;
                        sum = 0;
                
                        INSERT INTO account_move (name,ref,journal_id,company_id,date,operating_unit_id,user_id,state,is_cbs,is_sync,is_cr,is_opening,create_uid,write_uid,create_date,write_date) 
                            VALUES ('/','Profit Between Date '|| date_start ||' and '|| date_end,journal_id,company_id,jrn_date,opu_id,user_id,'draft',TRUE,False,TRUE,TRUE,user_id,user_id,NOW(),NOW())
                            RETURNING account_move.id INTO move;
                
                        forward_query = format('SELECT aml.operating_unit_id,
                                        SUM(aml.credit)- SUM(aml.debit) AS profit
                                    FROM account_move am
                                    LEFT JOIN account_move_line aml
                                           ON (am.id = aml.move_id)
                                    WHERE am.is_cbs=TRUE
                                          AND aml.date BETWEEN $1 AND $2
                                          AND aml.account_id IN (SELECT aa.id
                                        FROM account_account aa
                                        LEFT JOIN account_account_type aat
                                         ON (aa.user_type_id = aat.id)
                                        LEFT JOIN account_account_level aal
                                         ON (aal.id = aa.level_id)
                                        WHERE aat.include_initial_balance = FALSE
                                          AND aa.level_id=6)
                                    GROUP BY aml.operating_unit_id
                                    ORDER BY aml.operating_unit_id');
                        
                    company_query = format('SELECT eoy_type, 
                                       general_account_id, 
                                       profit_fy_id
                                FROM res_company 
                                WHERE id=$1');
                
                    FOR crec IN EXECUTE company_query USING company_id
                    LOOP
                        eoy_type = crec.eoy_type;
                        general_id = crec.general_account_id;
                        profit_fy_id = crec.profit_fy_id;
                    END LOOP;
                
                    --RAISE NOTICE '%-%-%', eoy_type,general_id,retain_earning_id;
                
                    FOR mrec IN EXECUTE forward_query USING date_start,date_end
                    LOOP
                      IF mrec.profit > 0 THEN
                        credit = mrec.profit;
                        debit = 0;
                      ELSE 
                        credit = 0;
                        debit = ABS(mrec.profit);
                      END IF;
                
                      sum= sum + ABS(mrec.profit);
                      
                      INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit)
                      VALUES ('Profit Between Date '||date_start||' and '|| date_end,'Profit and Loss ',company_id,journal_id,move,profit_fy_id,opu_id,jrn_date,jrn_date,debit,credit,user_id,user_id,NOW(),NOW(),TRUE);
                      
                      INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit)
                      VALUES ('Profit Between Date '||date_start||' and '|| date_end,'Profit and Loss ',company_id,journal_id,move,general_id,mrec.operating_unit_id,jrn_date,jrn_date,credit,debit,user_id,user_id,NOW(),NOW(),TRUE);
                          
                    END LOOP;
                
                    UPDATE account_move SET amount=sum WHERE id=move;
                
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
