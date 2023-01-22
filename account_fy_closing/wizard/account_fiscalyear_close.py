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
                                  domain="[('type_id.fiscal_year','=','True')]")
    start_fy_id = fields.Many2one('date.range', string='New Fiscal Year', required=True,
                                  domain="[('type_id.fiscal_year','=','True')]")
    journal_id = fields.Many2one('account.journal', string='Journal Type', readonly=True,
                                 default=default_journal, domain="[('type','=','general')]", required=True)
    period_id = fields.Many2one('date.range', string='Opening Entries Period', required=False)
    report_name = fields.Char(string='Name of new entries', required=False, help="Give name of the new entries")

    @api.model_cr
    def init(self):
        self._cr.execute("""
                    CREATE OR REPLACE FUNCTION profit_loss_calculation(dt_start DATE,dt_end DATE,date DATE,user_id INTEGER,journal_id INTEGER,opu_id INTEGER,company_id INTEGER) 
                        RETURNS INTEGER AS $$
                        DECLARE
                        mrec RECORD;
                        pl RECORD;
                        crec RECORD;
                        forward_query TEXT;
                        pl_query TEXT;
                        company_query TEXT;
                        reconcile_query TEXT;
                        move INTEGER;
                        level INTEGER;
                        user_id INTEGER;
                        branch_id INTEGER;
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
                                        ou.name, ou.obu,
                                        aml.currency_id,
                                        SUM(aml.amount_currency) AS amount_currency,
                                        SUM(aml.credit)- SUM(aml.debit) AS profit
                                    FROM account_move am
                                    LEFT JOIN account_move_line aml
                                           ON (am.id = aml.move_id)
                                    LEFT JOIN operating_unit ou
                                           ON (ou.id = aml.operating_unit_id)
                                    LEFT JOIN res_currency curr
                                           ON (curr.id = aml.currency_id)
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
                                    GROUP BY aml.operating_unit_id,
                                             aml.currency_id,
                                             ou.name, ou.obu                                             
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

                      sum = sum + ABS(mrec.profit);
                      
                      IF mrec.obu = TRUE THEN
                        branch_id = mrec.operating_unit_id;
                      ELSE 
                        branch_id = opu_id;
                        INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit, currency_id, amount_currency)
                        VALUES ('Profit/Loss between '||date_start||' and '|| date_end || ' in ['|| mrec.name || ']','Profit and Loss ',company_id,journal_id,move,general_id,mrec.operating_unit_id,jrn_date,jrn_date,debit,credit,user_id,user_id,NOW(),NOW(),TRUE,mrec.currency_id, mrec.amount_currency);
                        INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit, currency_id, amount_currency)
                        VALUES ('Profit/Loss between '||date_start||' and '|| date_end || ' in ['|| mrec.name || ']','Profit and Loss ',company_id,journal_id,move,general_id,opu_id,jrn_date,jrn_date,credit,debit,user_id,user_id,NOW(),NOW(),TRUE,mrec.currency_id, mrec.amount_currency);
                      END IF;

                      INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit, currency_id, amount_currency)
                      VALUES ('Profit/Loss between '||date_start||' and '|| date_end || ' in ['|| mrec.name || ']','Profit and Loss ',company_id,journal_id,move,profit_fy_id,branch_id,jrn_date,jrn_date,debit,credit,user_id,user_id,NOW(),NOW(),TRUE,mrec.currency_id, mrec.amount_currency);

                      pl_query = format('SELECT aml.operating_unit_id,
                                        ou.name,
                                        aml.currency_id,
                                        SUM(aml.amount_currency) AS amount_currency,
                                        aml.account_id,
                                        SUM(aml.credit)- SUM(aml.debit) AS profit
                                    FROM account_move am
                                    LEFT JOIN account_move_line aml
                                           ON (am.id = aml.move_id)
                                    LEFT JOIN operating_unit ou
                                           ON (ou.id = aml.operating_unit_id)
                                    WHERE am.is_cbs=TRUE
                                          AND aml.date BETWEEN $1 AND $2
                                          AND aml.operating_unit_id = $3
                                          AND aml.account_id IN (SELECT aa.id
                                        FROM account_account aa
                                        LEFT JOIN account_account_type aat
                                         ON (aa.user_type_id = aat.id)
                                        LEFT JOIN account_account_level aal
                                         ON (aal.id = aa.level_id)
                                        WHERE aat.include_initial_balance = FALSE
                                          AND aa.level_id=6)
                                    GROUP BY aml.operating_unit_id,
                                             aml.account_id,
                                             aml.currency_id,
                                             ou.name
                                    ORDER BY aml.operating_unit_id');
                      FOR pl IN EXECUTE pl_query USING date_start,date_end,mrec.operating_unit_id
                        LOOP  
                            IF pl.profit > 0 THEN
                                INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit,currency_id,amount_currency)
                                VALUES ('Profit/Loss between '||date_start||' and '|| date_end || ' in ['|| pl.name || ']','Profit and Loss ',company_id,journal_id,move,pl.account_id,pl.operating_unit_id,jrn_date,jrn_date,ABS(pl.profit),0,user_id,user_id,NOW(),NOW(),TRUE,pl.currency_id, (-1 * pl.amount_currency));
                            ELSIF  pl.profit < 0 THEN
                                INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,date_maturity,date,debit,credit,create_uid,write_uid,create_date,write_date,is_profit,currency_id,amount_currency)
                                VALUES ('Profit/Loss between '||date_start||' and '|| date_end || ' in ['|| pl.name || ']','Profit and Loss ',company_id,journal_id,move,pl.account_id,pl.operating_unit_id,jrn_date,jrn_date,0,ABS(pl.profit),user_id,user_id,NOW(),NOW(),TRUE,pl.currency_id, (-1 * pl.amount_currency));
                            END IF;
                        END LOOP;
                    END LOOP;

                    UPDATE account_move SET amount=sum WHERE id=move;

                    RETURN move;
                    END;
                    $$ LANGUAGE plpgsql;
                    """)

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
                                                  AND aa.level_id=6
                                                  AND aml.amount_currency >= 0)
                                        GROUP BY aml.journal_id,
                                            aml.currency_id,
                                            aml.account_id,
                                            aml.operating_unit_id,
                                            aml.analytic_account_id,
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

                                      IF mrec.debit > 0 THEN
                                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,currency_id,amount_currency,create_uid,write_uid,create_date,write_date,is_opening)
                                          VALUES ('Year Closing between '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,mrec.debit,0,mrec.currency_id,0,user_id,user_id,NOW(),NOW(),TRUE);
                                      END IF;
                                      IF mrec.credit > 0 THEN
                                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,currency_id,amount_currency,create_uid,write_uid,create_date,write_date,is_opening)
                                          VALUES ('Year Closing between '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,0,mrec.credit,mrec.currency_id,mrec.amount_currency,user_id,user_id,NOW(),NOW(),TRUE);
                                      END IF;
                                  END IF;
                                END LOOP;
                                
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
                                                  AND aa.level_id=6
                                                  AND aml.amount_currency < 0)
                                        GROUP BY aml.journal_id,
                                            aml.currency_id,
                                            aml.account_id,
                                            aml.operating_unit_id,
                                            aml.analytic_account_id,
                                            aml.servicing_channel_id,
                                            aml.acquiring_channel_id,
                                            aml.segment_id
                                        ORDER BY aml.account_id ASC');                                
                                
                                FOR mrec IN EXECUTE forward_query USING date_start,date_end
                                LOOP
                                  IF mrec.account_id = profit_fy_id THEN
                                        mrec.account_id = retain_earning_id;
                                  END IF;

                                  IF mrec.debit > 0 or mrec.credit > 0 THEN
                                      sum= sum + ABS(mrec.debit);

                                      IF mrec.debit > 0 THEN
                                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,currency_id,amount_currency,create_uid,write_uid,create_date,write_date,is_opening)
                                          VALUES ('Year Closing between '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,mrec.debit,0,mrec.currency_id,mrec.amount_currency,user_id,user_id,NOW(),NOW(),TRUE);
                                      END IF;
                                      IF mrec.credit > 0 THEN
                                          INSERT INTO account_move_line (name,ref,company_id,journal_id,move_id,account_id,operating_unit_id,analytic_account_id,servicing_channel_id,acquiring_channel_id,segment_id,date_maturity,date,debit,credit,currency_id,amount_currency,create_uid,write_uid,create_date,write_date,is_opening)
                                          VALUES ('Year Closing between '||date_start||' and '|| date_end,'Financial Year Closing',company_id,journal_id,move,mrec.account_id,mrec.operating_unit_id,mrec.analytic_account_id,mrec.servicing_channel_id,mrec.acquiring_channel_id,mrec.segment_id,jrn_date,jrn_date,0,mrec.credit,mrec.currency_id,0,user_id,user_id,NOW(),NOW(),TRUE);
                                      END IF;
                                  END IF;
                                END LOOP;

                                UPDATE account_move SET amount=sum WHERE id=move;

                            RETURN move;
                            END;
                            $$ LANGUAGE plpgsql;
                    """)

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
