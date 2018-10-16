from odoo import api,models,fields

class ReportEventMonthlyReport(models.AbstractModel):
    _name = "report.event_management.report_event_monthly"

    @api.multi
    def render_html(self, docids, data=None):

        date_from = data['date_from']
        date_to = data['date_to']

        sql_dept = '''SELECT event.name as event_name, 
                            session.name as session_name,
                            event.date_begin as start_date, 
                            event.date_end as end_date, 
                            event.seats_used as total_participant 
                      FROM event_event as event
                      LEFT JOIN
                            event_session as session
                        ON
                            session.event_id = event.id
                      WHERE 
                            Date_trunc('day', event.date_begin) BETWEEN DATE '%s' and DATE '%s'
                           
                   ''' % ( date_from, date_to)


        self.env.cr.execute(sql_dept)
        data_list = self.env.cr.dictfetchall()
        event_list = {vals['event_name']: {'item': [], } for vals in data_list}
        for vals in data_list:
            if vals:
                event_list[vals['event_name']]['item'].append(vals)
        # checklist = []
        # for vals in data_list:
        #     if vals:
        #         checklist.append(vals)

        docargs = {
            'date_from': date_from,
            'date_to': date_to,
            'lists': event_list,
        }

        return self.env['report'].render('event_management.report_event_monthly',docargs)