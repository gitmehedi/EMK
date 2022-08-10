from odoo.report import report_sxw
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx


class EventReportXLSX(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, obj):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        data['date_from'] = docs['start_date']
        data['date_to'] = docs['end_date']
        events = self.env['report.event_management.report_event_monthly']._get_events(data)

        header_left = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True, 'size': 12})
        header_right = workbook.add_format({'align': 'right', 'valign': 'vcenter', 'bold': True, 'size': 12})
        format = workbook.add_format({'align': 'left', 'valign': 'top'})
        bold = workbook.add_format({'align': 'left', 'bold': True})
        no_format = workbook.add_format({'num_format': '#,###0.000'})
        total_format = workbook.add_format({'bold': True, 'num_format': '#,###0.000'})

        worksheet = workbook.add_worksheet('Monthly Events')
        worksheet.merge_range('A1:H2', 'Monthly Events', header_left)
        worksheet.set_column(0, 50, 20)

        if data['date_from']:
            worksheet.write('D5', 'Date From:', bold)
            worksheet.write('E5', data['date_from'])
        if data['date_to']:
            worksheet.write('D6', 'Date To:', bold)
            worksheet.write('E6', data['date_to'])

        row, col = 11, 0

        worksheet.merge_range(row, col, row + 1, col, 'Event Name', header_left)
        worksheet.merge_range(row, col + 1, row + 1, col + 1, 'Program Date', header_left)
        worksheet.merge_range(row, col + 2, row + 1, col + 2, 'Program Time', header_left)
        worksheet.merge_range(row, col + 3, row + 1, col + 3, 'Event Type', header_left)
        worksheet.merge_range(row, col + 4, row + 1, col + 4, 'Event Pillar', header_left)
        worksheet.merge_range(row, col + 5, row + 1, col + 5, 'Event Category', header_left)
        worksheet.merge_range(row, col + 6, row + 1, col + 6, 'Event Theme', header_left)
        worksheet.merge_range(row, col + 7, row + 1, col + 7, 'Event Room', header_left)
        worksheet.merge_range(row, col + 8, row + 1, col + 8, 'Organizer Name', header_left)
        worksheet.merge_range(row, col + 9, row + 1, col + 9, 'PoC Name', header_left)
        worksheet.merge_range(row, col + 10, row + 1, col + 10, 'PoC Type', header_left)
        worksheet.merge_range(row, col + 11, row + 1, col + 11, 'Session', header_left)
        worksheet.merge_range(row, col + 12, row + 1, col + 12, 'Start Time', header_left)
        worksheet.merge_range(row, col + 13, row + 1, col + 13, 'End Time', header_left)
        worksheet.merge_range(row, col + 14, row + 1, col + 14, 'Activity Duration', header_left)
        worksheet.merge_range(row, col + 15, row + 1, col + 15, 'Target Audience Group', header_left)
        worksheet.merge_range(row, col + 16, row + 1, col + 16, 'Target Age', header_left)
        worksheet.merge_range(row, col + 17, row, col + 21, 'Offline Participants', header_left)
        worksheet.merge_range(row, col + 22, row, col + 26, 'Online Engagement', header_left)
        worksheet.merge_range(row, col + 27, row, col + 31, 'Live Audience', header_left)
        worksheet.merge_range(row, col + 32, row, col + 36, 'Online View', header_left)
        row += 1
        col = 17
        worksheet.write(row, col, 'Total Participants', header_left)
        worksheet.write(row, col + 1, 'Male', header_left)
        worksheet.write(row, col + 2, 'Female', header_left)
        worksheet.write(row, col + 3, 'Transgender', header_left)
        worksheet.write(row, col + 4, 'Prefer Not to Say', header_left)
        worksheet.write(row, col + 5, 'Total Participants', header_left)
        worksheet.write(row, col + 6, 'Male', header_left)
        worksheet.write(row, col + 7, 'Female', header_left)
        worksheet.write(row, col + 8, 'Transgender', header_left)
        worksheet.write(row, col + 9, 'Prefer Not to Say', header_left)
        worksheet.write(row, col + 10, 'Total Participants', header_left)
        worksheet.write(row, col + 11, 'Male', header_left)
        worksheet.write(row, col + 12, 'Female', header_left)
        worksheet.write(row, col + 13, 'Transgender', header_left)
        worksheet.write(row, col + 14, 'Prefer Not to Say', header_left)
        worksheet.write(row, col + 15, 'Total Participants', header_left)
        worksheet.write(row, col + 16, 'Male', header_left)
        worksheet.write(row, col + 17, 'Female', header_left)
        worksheet.write(row, col + 18, 'Transgender', header_left)
        worksheet.write(row, col + 19, 'Prefer Not to Say', header_left)

        row += 1
        col = 0

        for rec in events:
            worksheet.write(row, col, rec['event_name'])
            worksheet.write(row, col + 1, rec['program_date'])
            worksheet.write(row, col + 2, rec['program_time'])
            worksheet.write(row, col + 3, rec['event_type'])
            worksheet.write(row, col + 4, rec['event_pillar'])
            worksheet.write(row, col + 5, rec['event_category'])
            worksheet.write(row, col + 6, rec['event_theme'])
            worksheet.write(row, col + 7, rec['event_room'])
            worksheet.write(row, col + 8, rec['event_organizer'])
            worksheet.write(row, col + 9, rec['poc_name'])
            worksheet.write(row, col + 10, rec['poc_type'])
            worksheet.write(row, col + 11, rec['event_session'])
            worksheet.write(row, col + 12, rec['start_time'])
            worksheet.write(row, col + 13, rec['end_time'])
            worksheet.write(row, col + 14, rec['activity_duration'])
            worksheet.write(row, col + 15, rec['target_audience_group'])
            worksheet.write(row, col + 16, (rec['target_age']))
            worksheet.write(row, col + 17, rec['off_total_participant'])
            worksheet.write(row, col + 18, rec['off_male'])
            worksheet.write(row, col + 19, rec['off_female'])
            worksheet.write(row, col + 20, rec['off_transgender'])
            worksheet.write(row, col + 21, rec['off_not_say'])
            worksheet.write(row, col + 22, rec['on_total_participant'])
            worksheet.write(row, col + 23, rec['on_male'])
            worksheet.write(row, col + 24, rec['on_female'])
            worksheet.write(row, col + 25, rec['on_transgender'])
            worksheet.write(row, col + 26, rec['on_not_say'])
            worksheet.write(row, col + 27, rec['live_total_participant'])
            worksheet.write(row, col + 28, rec['live_male'])
            worksheet.write(row, col + 29, rec['live_female'])
            worksheet.write(row, col + 30, rec['live_transgender'])
            worksheet.write(row, col + 31, rec['live_not_say'])
            worksheet.write(row, col + 32, rec['view_total_participant'])
            worksheet.write(row, col + 33, rec['view_male'])
            worksheet.write(row, col + 34, rec['view_female'])
            worksheet.write(row, col + 35, rec['view_transgender'])
            worksheet.write(row, col + 36, rec['view_not_say'])


            row += 1

        # worksheet.write(row, col + 3, 'Total', total_format)
        # worksheet.write(row, col + 4, sum['init_bal'], total_format)
        # worksheet.write(row, col + 5, sum['debit'], total_format)
        # worksheet.write(row, col + 6, sum['credit'], total_format)
        # worksheet.write(row, col + 7, sum['balance'], total_format)


EventReportXLSX('report.event_management.monthly_event_xlsx', 'wizard.monthly.report', parser=report_sxw.rml_parse)
