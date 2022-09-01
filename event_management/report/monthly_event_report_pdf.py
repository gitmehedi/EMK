from odoo import api, models, fields


class ReportEventMonthlyReport(models.AbstractModel):
    _name = "report.event_management.report_event_monthly"

    def _get_events(self, data):
        start = data['date_from']
        end = data['date_to']
        events = self.env['event.event'].search([('date_begin', '>=', start),
                                                 ('date_begin', '<=', end)], order='date_begin asc')

        event_list = []
        for event in events:
            room = [ev.room_id.name for ev in event.event_book_ids]
            session = [ev.name for ev in event.session_ids]

            val = {
                'event_name': event.name,
                'program_date': event.date_begin[:10],
                'program_time': event.date_begin[10:],
                'event_type': event.event_type_id.name,
                'event_pillar': event.pillar_id.name,
                'event_category': event.event_category_id.name,
                'event_theme': event.theme_id.name,
                'event_room': ', '.join(room),
                'event_organizer': event.user_id.name,
                'poc_name': event.organizer_id.name,
                'poc_type': event.poc_type_id.name,
                'event_session': ', '.join(session),
                'start_time': event.date_begin[10:],
                'end_time': event.date_end[10:],
                'activity_duration': event.activity_duration,
                'off_total_participant': event.off_total_participant,
                'off_male': event.off_male,
                'off_female': event.off_female,
                'off_transgender': event.off_transgender,
                'off_not_say': event.off_not_say,
                'on_total_participant': event.on_total_participant,
                'on_male': event.on_male,
                'on_female': event.on_female,
                'on_transgender': event.on_transgender,
                'on_not_say': event.on_not_say,
                'live_total_participant': event.live_total_participant,
                'live_male': event.live_male,
                'live_female': event.live_female,
                'live_transgender': event.live_transgender,
                'live_not_say': event.live_not_say,
                'view_total_participant': event.view_total_participant,
                'view_male': event.view_male,
                'view_female': event.view_female,
                'view_transgender': event.view_transgender,
                'view_not_say': event.view_not_say,
                'target_audience_group': event.target_audience_group,
                'target_age': event.target_age,
            }
            event_list.append(val)

        return event_list

    @api.multi
    def render_html(self, docids, data=None):
        events = self._get_events(data)
        start = data['date_from']
        end = data['date_to']

        docargs = {
            'date_from': start,
            'date_to': end,
            'lists': events,
        }

        return self.env['report'].render('event_management.report_event_monthly', docargs)
