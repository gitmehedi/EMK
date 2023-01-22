# -*- coding: utf-8 -*-

import os, shutil, base64, traceback, logging, re
import numpy as np

from datetime import datetime
from datetime import datetime as dt
from random import randint
from contextlib import contextmanager
from odoo import exceptions, models, fields, api, _, tools
from odoo.exceptions import ValidationError

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

_logger = logging.getLogger(__name__)
try:
    import pysftp
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import pysftp')


class ServerFileProcess(models.Model):
    _name = "server.file.process"
    _description = "Configuration of SFTP File Processing"
    _inherit = ["mail.thread", "ir.needaction_mixin"]

    _sql_constraints = [
        ("name_unique", "UNIQUE(name)", "Cannot duplicate a configuration."),
        ("days_to_keep_positive", "CHECK(days_to_keep >= 0)",
         "I cannot remove backups from the future. Ask Doc for that."),
    ]

    name = fields.Char(string="Name", required=True, track_visibility='onchange')
    folder = fields.Char(default=lambda self: self._default_path(), string="Local Folder Path",
                         track_visibility='onchange')
    days_to_keep = fields.Integer(required=True, default=0, )

    source_path = fields.Char(string="Source Path", required=True, track_visibility='onchange')
    source_sftp_host = fields.Char(string='Middleware IP', track_visibility='onchange')
    source_sftp_port = fields.Integer(string="Middleware Port", default=22, track_visibility='onchange')
    source_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    source_sftp_password = fields.Char(string="Password")
    source_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')

    dest_path = fields.Char(string="Destination Path", required=True, track_visibility='onchange')
    dest_arc_path = fields.Char(string="Destination Arch Path", track_visibility='onchange')
    dest_sftp_host = fields.Char(string='Middleware IP', track_visibility='onchange')
    dest_sftp_port = fields.Integer(string="Middleware Port", default=22, track_visibility='onchange')
    dest_sftp_user = fields.Char(string='Username', track_visibility='onchange')
    dest_sftp_password = fields.Char(string="Password")
    dest_sftp_private_key = fields.Char(string="Primary Key Location", track_visibility='onchange')
    type = fields.Selection([('glif', 'GLIF Process'),
                             ('sys_dt', 'Date Process'),
                             ('mdc', 'MDC Process'),
                             ('mdc_report', 'MDC Report Process')],
                            string='Type', required=True)
    method = fields.Selection(selection=[("local", "Local Location"),
                                         ("dest_sftp", "Single Middleware Location"),
                                         ("sftp", "Double Middleware Location")],
                              default="sftp", required=True, track_visibility='onchange')
    sys_file_name = fields.Char(string='Filename', track_visibility='onchange')
    status = fields.Boolean(default=True, string='Status')

    @api.constrains('source_path', 'dest_path', 'folder')
    def onchange_path(self):
        if self.method == 'local':
            if self.source_path:
                if not os.path.exists(self.source_path):
                    raise ValidationError(_('Source Path [{0}] doesn\'t exists.'.format(self.source_path)))
            if self.dest_path:
                if not os.path.exists(self.dest_path):
                    raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

        if self.method == 'sftp':
            with self.sftp_connection('source') as source:
                if self.source_path:
                    if not source.exists(self.source_path):
                        raise ValidationError(_('Source Path [{0}] doesn\'t exists.'.format(self.source_path)))

            with self.sftp_connection('destination') as destination:
                if self.dest_path:
                    if not destination.exists(self.dest_path):
                        raise ValidationError(_('Destination Path [{0}] doesn\'t exists.'.format(self.dest_path)))

            if self.folder:
                if not os.path.exists(self.folder):
                    raise ValidationError(_('Local Path [{0}] doesn\'t exists.'.format(self.folder)))

    @api.onchange('method')
    def onchange_name(self):
        if self.method == 'local':
            self.source_path = None
            self.source_sftp_host = None
            self.source_sftp_port = None
            self.source_sftp_user = None
            self.source_sftp_password = None
            self.source_sftp_private_key = None
            self.dest_path = None
            self.dest_sftp_host = None
            self.dest_sftp_port = None
            self.dest_sftp_user = None
            self.dest_sftp_password = None
            self.dest_sftp_private_key = None

    @api.model
    def _default_path(self):
        """Default to ``backups`` folder inside current server datadir."""
        return os.path.expanduser('~')

    @api.multi
    @api.depends("folder", "method", "source_sftp_host", "source_sftp_port", "source_sftp_user")
    def _compute_name(self):
        for rec in self:
            if rec.method == "local":
                rec.name = "%s @ localhost" % rec.folder
            elif rec.method == "sftp":
                rec.name = "sftp://%s@%s:%d%s" % (
                    rec.source_sftp_user, rec.source_sftp_host, rec.source_sftp_port, rec.folder)

    @api.multi
    @api.constrains("folder", "method")
    def _check_folder(self):
        """Do not use the filestore or you will backup your backups."""
        for s in self:
            if (s.method == "local" and
                    s.folder.startswith(
                        tools.config.filestore(self.env.cr.dbname))):
                raise exceptions.ValidationError(
                    _("Do not save backups on your filestore, or you will "
                      "backup your backups too!"))

    @api.model
    def glif_process(self):
        """Run all scheduled backups."""
        integration = self.search([('type', '=', 'glif'), ('method', '=', 'sftp'), ('status', '=', True)], limit=1)
        if not integration:
            raise ValidationError(_("Record is not available with proper configuration"))
        return integration.glif_generate_process()

    @api.model
    def sysdt_process(self):
        integration = self.search([('type', '=', 'sys_dt'), ('method', '=', 'dest_sftp'), ('status', '=', True)],
                                  limit=1)
        if not integration:
            raise ValidationError(_("Record is not available with proper configuration"))
        return integration.sysdt_import_process(integration)

    @api.model
    def mdc_process(self):
        integration = self.search([('type', '=', 'mdc'), ('method', '=', 'dest_sftp'), ('status', '=', True)],
                                  limit=1)
        if not integration:
            raise ValidationError(_("Record is not available with proper configuration"))
        return integration.mdc_generate_process()

    @api.model
    def mdc_report_process(self):
        integration = self.search([('type', '=', 'mdc_report'), ('method', '=', 'sftp'), ('status', '=', True)],
                                  limit=1)
        if not integration:
            raise ValidationError(_("Record is not available with proper configuration"))
        return integration.mdc_report_generate_process()

    """Function Defination of CRON JOB"""

    @api.multi
    def glif_generate_process(self):

        for rec in self.filtered(lambda r: r.method == "local"):
            dirs = [rec.source_path, rec.dest_path]
            self.directory_check(dirs)

            files = filter(lambda x: x.endswith('.txt'), os.listdir(rec.source_path))
            for file in files:

                if os.path.splitext(file)[1] in ['.txt']:
                    source_path = os.path.join(rec.source_path, file)
                    dest_path = os.path.join(rec.dest_path, file)
                    start_date = fields.Datetime.now()
                    journal = rec.create_journal(file)
                    stop_date = fields.Datetime.now()
                    if journal:
                        if shutil.move(source_path, dest_path):
                            raise ValidationError(_('Please check path configuration.'))
                        else:
                            self.env['server.file.success'].create({'name': file,
                                                                    'start_date': start_date,
                                                                    'stop_date': stop_date,
                                                                    'file_name': file,
                                                                    'move_id': journal.id})

        for rec in self.filtered(lambda r: r.method == "sftp"):
            with self.sftp_connection('source') as source:
                with self.sftp_connection('destination') as destination:
                    dirs = [rec.folder, rec.source_path, rec.dest_path]
                    self.directory_check(dirs)
                    files = filter(lambda x: x.endswith('.txt'), source.listdir(rec.source_path))
                    for file in files:
                        source_path = os.path.join(rec.source_path, file)
                        dest_path = os.path.join(rec.dest_path, file)
                        local_path = os.path.join(rec.folder, file)

                        source.get(source_path, localpath=local_path, preserve_mtime=True)
                        start_date = fields.Datetime.now()
                        journal = rec.create_journal(file, {'source': source, 'dest': destination})
                        stop_date = fields.Datetime.now()
                        if journal:
                            if destination.put(local_path, dest_path):
                                self.env['server.file.success'].create({'name': file,
                                                                        'start_date': start_date,
                                                                        'stop_date': stop_date,
                                                                        'file_name': file,
                                                                        'move_id': journal.id})
                                if not source.unlink(source_path):
                                    os.remove(local_path)
                                else:
                                    continue
                            else:
                                continue
                        else:
                            os.remove(local_path)

    @api.multi
    def mdc_report_generate_process(self):

        for rec in self.filtered(lambda r: r.method == "local"):
            dirs = [rec.source_path, rec.dest_path]
            self.directory_check(dirs)

            files = filter(lambda x: x.endswith('.txt'), os.listdir(rec.source_path))
            for file in files:
                if os.path.splitext(file)[1] in ['.txt']:
                    source_path = os.path.join(rec.source_path, file)
                    dest_path = os.path.join(rec.dest_path, file)
                    start_date = fields.Datetime.now()
                    journal = rec.create_journal(file)
                    stop_date = fields.Datetime.now()
                    if journal:
                        if shutil.move(source_path, dest_path):
                            raise ValidationError(_('Please check path configuration.'))
                        else:
                            self.env['server.file.success'].create({'name': file,
                                                                    'start_date': start_date,
                                                                    'stop_date': stop_date,
                                                                    'file_name': file,
                                                                    'move_id': journal.id})

        for rec in self.filtered(lambda r: r.method == "sftp"):
            report_gen = self.env['generate.cbs.journal.success'].search(
                [('has_report', '=', False), ('state', '=', 'mdc')])
            mdc_rec = {rec.name: rec for rec in report_gen}
            with self.sftp_connection('source') as source:
                with self.sftp_connection('destination') as destination:
                    dirs = [rec.folder, rec.source_path, rec.dest_path]
                    self.directory_check(dirs)
                    files = filter(lambda x: x.endswith('.txt'), source.listdir(rec.source_path))
                    for file in files:
                        source_path = os.path.join(rec.source_path, file)
                        dest_path = os.path.join(rec.dest_path, file)
                        local_path = os.path.join(rec.folder, file)

                        source.get(source_path, localpath=local_path, preserve_mtime=True)
                        process_time = fields.Datetime.now()
                        with open(local_path) as f:
                            content = base64.b64encode(f.read())
                            encode = content if len(content) > 0 else ' '
                        if file in mdc_rec:
                            report = mdc_rec[file].write({'mdc_report_file': encode,
                                                          'mdc_report_process_time': process_time,
                                                          'has_report': True,
                                                          'state': 'report',
                                                          })
                            if report:
                                if destination.put(local_path, dest_path):
                                    os.remove(local_path)
                                    source.unlink(source_path)
                                    for move in mdc_rec[file].line_ids:
                                        move.move_id.write({'report_process': True})

                        else:
                            os.remove(local_path)

    @api.multi
    def mdc_generate_process(self):
        mdc = self.env['generate.cbs.journal.success'].search([('state', '=', 'mdc'), ('state', '!=', 'mdc_report')])
        if len(mdc) > 0:
            return False
        filename = self.generate_filename()

        def contain_fixed_length_of_line_in_file(file_path):
            fixed_length = 117 + 2
            with open(file_path, "r") as reader:
                for line in reader:
                    if len(line) != fixed_length:
                        return False

            return True
        # END of contain_fixed_length_of_line_in_file

        def generate_file(record):
            move_ids = []
            # for doing write operation
            move_id_list = []

            file_path = os.path.join(record.source_path, filename)
            journals = self.env['account.move'].search([('is_cbs', '=', False),
                                                        ('is_sync', '=', False),
                                                        ('is_opening', '=', False),
                                                        ('line_ids.is_bgl', '=', 'pass'),
                                                        ('state', '=', 'posted')], order='id ASC')

            with open(file_path, "w+") as file:
                for vals in journals:
                    for val in vals.line_ids:
                        trn_type = '54' if val.debit > 0 else '04'
                        amount = format(val.debit, '.2f') if val.debit > 0 else format(val.credit, '.2f')
                        amount = ''.join(amount.split('.')).zfill(16)
                        narration = re.sub(r'[|\n||\r|?|$|.|!]', r' ', val.name[:50])
                        trn_ref_no = val.reconcile_ref if val.reconcile_ref else ''
                        date_array = val.date.split("-")
                        date = date_array[2] + date_array[1] + date_array[0]
                        cost_centre = str(
                            "0" + val.analytic_account_id.code) if val.analytic_account_id.code else '0000'
                        account_no = str(val.account_id.code)
                        sub_opu = str(val.sub_operating_unit_id.code) if val.sub_operating_unit_id.code else '001'
                        branch_code = str("00" + val.operating_unit_id.code) if val.operating_unit_id.code else '00001'
                        bgl = "0{0}{1}{2}".format(account_no, sub_opu, branch_code)

                        journal = "{:2s}{:17s}{:16s}{:50s}{:20s}{:8s}{:4s}\r\n".format(trn_type, bgl, amount, narration,
                                                                                       trn_ref_no, date, cost_centre)
                        file.write(journal)

                    move_ids.append((0, 0, {'move_id': vals.id}))
                    move_id_list.append(vals.id)

            # check for fixed length of the line in a file
            if not contain_fixed_length_of_line_in_file(file_path):
                os.remove(file_path)
                return False

            if os.stat(file_path).st_size == 0:
                os.remove(file_path)

            if os.path.exists(file_path):
                moves = self.env['account.move'].browse(move_id_list)
                moves.write({'is_sync': True})
                return move_ids
            else:
                return False
        # END of generate_file

        record = self.env['server.file.process'].search([('method', '=', 'dest_sftp'),
                                                         ('type', '=', 'mdc'),
                                                         ('status', '=', True)], limit=1)
        for rec in record:
            with rec.sftp_connection('destination') as destination:
                dirs = [rec.folder, rec.source_path, rec.dest_path]
                self.directory_check(dirs)
                start_date = fields.Datetime.now()
                file = generate_file(rec)

                dest_path = os.path.join(rec.dest_path, filename)
                dest_arc_path = os.path.join(rec.dest_arc_path, filename)
                local_path = os.path.join(rec.source_path, filename)

                if file:
                    if destination.put(local_path, dest_path) and destination.put(local_path, dest_arc_path):
                        with open(local_path, "rb") as cbs_file:
                            encoded_file = base64.b64encode(cbs_file.read())
                        stop_date = fields.Datetime.now()
                        success = self.env['generate.cbs.journal.success'].create({'name': filename,
                                                                                   'start_date': start_date,
                                                                                   'stop_date': stop_date,
                                                                                   'upload_file': encoded_file,
                                                                                   'file_name': filename,
                                                                                   'line_ids': file,
                                                                                   })
                        if success:
                            os.remove(local_path)
                        else:
                            continue
                    else:
                        continue

    @api.multi
    def sysdt_import_process(self, record):
        for rec in record:
            with rec.sftp_connection('destination') as destination:
                dirs = [rec.source_path, rec.dest_path]
                rec.directory_check(dirs)
                files = filter(lambda x: x.endswith(self.sys_file_name), destination.listdir(rec.dest_path))
                if not files:
                    raise exceptions.Warning(_("[{0}] is not available in middleware.".format(self.sys_file_name)))

                for file in files:
                    source_path = os.path.join(rec.dest_path, file)
                    local_path = os.path.join(rec.source_path, file)
                    destination.get(source_path, localpath=local_path, preserve_mtime=True)

                    with open(local_path, 'r') as ins:
                        for date in ins:
                            year, month, day = date[:4], date[4:6], date[6:8]
                            batch_date = "{0}-{1}-{2}".format(year, month, day)
                            company = self.env['res.company'].search([])
                            previous_date = company.batch_date

                            try:
                                if previous_date != batch_date:
                                    company.sudo().write({'batch_date': batch_date})
                                    self.env['ir.values'].sudo().set_default('account.config.settings', 'batch_date',
                                                                             batch_date)
                                    self.env['system.date.status'].create({'current_date': batch_date,
                                                                           'previous_date': previous_date,
                                                                           'state': 'success',
                                                                           })

                            except Exception:
                                self.env['system.date.status'].create({'current_date': batch_date,
                                                                       'previous_date': previous_date,
                                                                       'state': 'fail',
                                                                       })

                    os.remove(local_path)

    def generate_filename(self):
        rec_date = self.env.user.company_id.batch_date.split('-')
        record_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0]) + datetime.strftime(datetime.now(),
                                                                                                     "%H%M%S_")
        process_date = "{0}{1}{2}_".format(rec_date[2], rec_date[1], rec_date[0])
        unique = str(randint(100, 999))
        return "MDC_00001_" + record_date + process_date + unique + ".txt"

    def get_file_path(self, file):
        path = {}
        if self.method == 'local':
            path['folder'] = os.path.join(self.folder, file)
            path['source'] = os.path.join(self.source_path, file)
            path['destination'] = os.path.join(self.dest_path, file)
        else:
            path['folder'] = os.path.join(self.folder, file)
            path['source'] = os.path.join(self.source_path, file)
            path['destination'] = os.path.join(self.dest_path, file)

        return path

    def preprocess(self, data):
        filter = data.split('.')
        return filter[0].strip() if len(filter) > 0 else None

    def data_mapping(self, vals):
        data = vals.split('|')
        glcc_struc = [3, 3, 1, 5, 3, 2, 2, 3]
        date_struc = [2, 2, 4, 2, 2, 2]
        glcc_name = ['BRANCH', 'CURRENCY', 'SEGMENT', 'COMP_1', 'COMP_2', 'AC', 'SC', 'COST_CENTRE']
        keys = ['POSTING-DATE',
                'SYSTEM-DATE',
                'POSTING-TIME',
                'SOURCE',
                'JOURNAL-NBR',
                'JOURNAL-SEQ',
                'SOC',
                'BRCH',
                'FCY-CODE',
                'GL-CLASS-CODE',
                'DESC-TRCODE-6',
                'DESC-TEXT-24',
                'POSTING-IND',
                'TRANS-DATE',
                'LCY-AMT',
                'FCY-AMT',
                'REVERSAL-CODE',
                'REVERSAL-DATE',
                'REFERENCE',
                'SOURCE-APPLN',
                'PS-JOURNAL-ID',
                'PS-JOURNAL-NBR',
                'CNTL-CENTRE']

        if len(data) > 15:
            data[9] = dict(zip(glcc_name, self.strslice(data[9], glcc_struc)))
            data[0] = self.format_data(self.strslice(data[0] + '000000', date_struc))
            data[1] = self.format_data(self.strslice(data[1] + '000000', date_struc))
            data[13] = self.format_data(self.strslice(data[13] + '000000', date_struc))
            if data[14][-1:] == '+':
                data[14] = data[14][:-1]
                data[15] = data[15]
                data[5] = '01'
            else:
                data[14] = data[14][:-1]
                data[15] = data[15]
                data[5] = '02'

            return dict(zip(keys, data[:len(data)]))
        else:
            return vals

    @api.multi
    def format_data(self, date):
        if len(date) == 6:
            try:
                data = "{0}-{1}-{2} {3}:{4}:{5}".format(date[1], date[0], date[2], date[3], date[4], date[5])
                date_con = datetime.strptime(data, '%m-%d-%Y %H:%M:%S')
            except Exception:
                date_con = False

            if date_con:
                return date_con
        return None

    @api.multi
    def strslice(self, pattern, lists):
        first, last = 0, 0
        values = []
        for val in lists:
            last += val
            values.append(pattern[first:last])
            first += val
        return values

    @api.multi
    def create_journal(self, file, conn={}):
        errors, response = [], False
        path = self.get_file_path(file)
        source_path = path['source'] if self.method == 'local' else path['folder']

        def format_error(id, index, text):
            return "({0},{1},'{2}','{3}'),".format(id, index, text, fields.Datetime.now())

        def format_journal(line):
            return "({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},{8},{9},{10},{11},{12},{13},{14},{15},{16}),".format(
                line['move_id'],
                line['date'],
                line['date_maturity'],
                line['operating_unit_id'],
                line['account_id'],
                line['name'],
                line['name'],
                line['currency_id'],
                line['journal_id'],
                line['analytic_account_id'],
                line['segment_id'],
                line['acquiring_channel_id'],
                line['servicing_channel_id'],
                line['credit'],
                line['debit'],
                line['amount_currency'],
                line['company_id'])

        with open(source_path, 'r') as file_ins:
            index = 0
            debit, credit = 0.0, 0.0
            coa = {val.code: val.id for val in
                   self.env['account.account'].search([('level_id.name', '=', 'Layer 5'), ('active', '=', True)])}
            jrnl = {val.code: val.id for val in self.env['account.journal'].search([('active', '=', True)])}
            branch = {val.code: val.id for val in self.env['operating.unit'].search([('active', '=', True)])}
            currency = {val.code: val.id for val in self.env['res.currency'].search([('active', '=', True)])}
            ac = {val.code: val.id for val in self.env['acquiring.channel'].search([('active', '=', True)])}
            sc = {val.code: val.id for val in self.env['servicing.channel'].search([('active', '=', True)])}
            sg = {val.code: val.id for val in self.env['segment'].search([('active', '=', True)])}
            cc = {val.code: val.id for val in
                  self.env['account.analytic.account'].search([('active', '=', True)])}

            errObj = self.env['server.file.error'].search([('name', '=', file), ('state', '=', 'issued')])
            if not errObj:
                errObj = self.env['server.file.error'].create({'name': file,
                                                               'file_path': source_path,
                                                               'ftp_ip': self.source_sftp_host,
                                                               })
            else:
                errObj.line_ids.unlink()

            errors, journal_entry, move_date = "", "", ""
            journal_type = 'CBS'
            if journal_type not in jrnl.keys():
                raise Warning(_('[Wanring] Journal type [{0}]is not available.'.format(journal_type)))

            move_id = self.env['account.move'].search([('ref', '=', file), ('state', '=', 'draft')], limit=1)
            if not move_id:
                move_id = self.env['account.move'].create({
                    'journal_id': jrnl['CBS'],
                    'date': fields.Datetime.now(),
                    'is_cbs': True,
                    'ref': file,
                    'line_ids': [],
                    'amount': 0
                })
            else:
                move_id.line_ids.unlink()

            for worksheet_index in file_ins:
                index += 1
                if len(worksheet_index) > 2:
                    rec = self.data_mapping(worksheet_index)
                    if rec == worksheet_index:
                        errors += format_error(errObj.id, index, '{0} has invalid value'.format(rec))
                        continue

                    name = rec['DESC-TEXT-24'].strip() if rec['DESC-TEXT-24'].strip() else '/'

                    posting_date = rec['POSTING-DATE']
                    if not posting_date:
                        errors += format_error(errObj.id, index,
                                               'POSTING-DATE or POSTING-TIME [{0}]has invalid value'.format(
                                                   posting_date))
                    if not move_date:
                        move_date = rec['POSTING-DATE']

                    system_date = rec['SYSTEM-DATE']
                    if not system_date:
                        errors += format_error(errObj.id, index,
                                               'SYSTEM-DATE [{0}] has invalid value'.format(system_date))

                    trans_date = rec['TRANS-DATE']
                    if not trans_date:
                        errors += format_error(errObj.id, index,
                                               'TRANS-DATE [{0}] has invalid value'.format(trans_date))

                    branch_code = rec['GL-CLASS-CODE']['BRANCH']
                    if branch_code not in branch.keys():
                        errors += format_error(errObj.id, index,
                                               'BRANCH [{0}] has invalid value'.format(branch_code))
                    else:
                        branch_val = branch[branch_code]

                    currency_code = rec['GL-CLASS-CODE']['CURRENCY']
                    if currency_code not in currency.keys():
                        errors += format_error(errObj.id, index,
                                               'CURRENCY [{0}]  has invalid value'.format(currency_code))
                    else:
                        currency_val = currency[currency_code]

                    sg_code = rec['GL-CLASS-CODE']['SEGMENT']
                    if sg_code not in sg.keys():
                        if sg_code == '0':
                            sg_val = 'NULL'
                        else:
                            errors += format_error(errObj.id, index,
                                                   'SEGMENT [{0}]  has invalid value'.format(sg_code))
                    else:
                        sg_val = sg[sg_code]

                    ac_code = rec['GL-CLASS-CODE']['AC']
                    if ac_code not in ac.keys():
                        if ac_code == '00':
                            ac_val = 'NULL'
                        else:
                            errors += format_error(errObj.id, index, 'AC [{0}]  has invalid value'.format(ac_code))
                    else:
                        ac_val = ac[ac_code]

                    sc_code = rec['GL-CLASS-CODE']['SC']
                    if sc_code not in sc.keys():
                        if sc_code == '00':
                            sc_val = 'NULL'
                        else:
                            errors += format_error(errObj.id, index, 'SC [{0}]  has invalid value'.format(sc_code))
                    else:
                        sc_val = sc[sc_code]

                    cc_code = rec['GL-CLASS-CODE']['COST_CENTRE']
                    if cc_code not in cc.keys():
                        if cc_code == '000':
                            cc_val = 'NULL'
                        else:
                            errors += format_error(errObj.id, index,
                                                   'COST_CENTRE [{0}]  has invalid value'.format(cc_code))
                    else:
                        cc_val = cc[cc_code]

                    if rec['GL-CLASS-CODE']['COMP_1'] and rec['GL-CLASS-CODE']['COMP_2']:
                        comp_code = rec['GL-CLASS-CODE']['COMP_1'] + rec['GL-CLASS-CODE']['COMP_2']
                        if comp_code not in coa.keys():
                            errors += format_error(errObj.id, index,
                                                   'Chart of Account [{0}]  has invalid value'.format(comp_code))
                        else:
                            comp_val = coa[comp_code]

                    decimal_bef = rec['LCY-AMT'][-17:-3]
                    decimal_after = rec['LCY-AMT'][-3:]
                    if not decimal_bef.isdigit() or not decimal_after.isdigit():
                        errors += format_error(errObj.id, index,
                                               'Amount [{0}] has invalid value'.format(rec['LCY-AMT']))
                    else:
                        lcy_amt = np.float128(decimal_bef + '.' + decimal_after)
                        amount = "{:.3f}".format(lcy_amt)

                    if len(amount) > 16:
                        errors += format_error(errObj.id, index,
                                               'LCY-AMT [{0}] has large value than system expected'.format(
                                                   rec['LCY-AMT']))

                    if currency_code == 'BDT':
                        fcy_amount = '0.0'
                    else:
                        fcy_d_bef = rec['FCY-AMT'][-17:-4]
                        fcy_d_after = rec['FCY-AMT'][-4:-1]
                        fcy_sign = rec['FCY-AMT'][-1:]
                        if not fcy_d_bef.isdigit() or not fcy_d_after.isdigit():
                            errors += format_error(errObj.id, index,
                                                   'FCY Amount [{0}] has invalid value'.format(rec['FCY-AMT']))
                        else:
                            fcy_amt = np.float128(fcy_d_bef + '.' + fcy_d_after)
                            fcy_amount = "{:.3f}".format(fcy_amt)
                            if fcy_sign == '-':
                                fcy_amount = '-' + fcy_amount   

                        if len(fcy_amount) > 16:
                            errors += format_error(errObj.id, index,
                                                   'FCY-AMT [{0}] has large value than system expected'.format(
                                                       rec['FCY-AMT']))

                    if len(errors) == 0:
                        line = {
                            'move_id': move_id.id,
                            'name': name,
                            'account_id': comp_val,
                            'journal_id': jrnl['CBS'],
                            'analytic_account_id': cc_val,
                            'currency_id': currency_val,
                            'segment_id': sg_val,
                            'acquiring_channel_id': ac_val,
                            'servicing_channel_id': sc_val,
                            'operating_unit_id': branch_val,
                            'date': posting_date,
                            'date_maturity': posting_date,
                            'company_id': self.env.user.company_id.id,
                        }

                        if rec['JOURNAL-SEQ'] == '02':
                            line['debit'] = amount
                            line['credit'] = 0.0
                            line['amount_currency'] = fcy_amount
                            debit += float(amount)

                        elif rec['JOURNAL-SEQ'] == '01':
                            line['debit'] = 0.0
                            line['credit'] = amount
                            line['amount_currency'] = fcy_amount
                            credit += float(amount)
                        journal_entry += format_journal(line)

        if len(errors) > 0:
            self.unlink_move(move_id)
            try:
                query = """
                    INSERT INTO server_file_error_line (line_id,line_no,details,process_date) 
                    VALUES %s """ % errors[:-1]
                self.env.cr.execute(query)
            except Exception:
                errObj.line_ids.create({'line_id': errObj.id,
                                        'line_no': 'UNKNOWN ERROR',
                                        'details': 'Please check your file.'})
        else:
            missmatch = "{:.3f}".format(round(debit - credit, 3))
            try:
                query = """
                INSERT INTO account_move_line 
                (move_id, date,date_maturity, operating_unit_id, account_id, name,ref, currency_id, journal_id,
                analytic_account_id,segment_id,acquiring_channel_id,servicing_channel_id,credit,debit,amount_currency,company_id)  
                VALUES %s""" % journal_entry[:-1]
                self.env.cr.execute(query)

                if move_id.state == 'draft':
                    if round(debit - credit, 2) > 0:
                        msg = 'Debit is greater than Credit. Mismatch Amount: {0}'.format(missmatch)
                        errObj.line_ids.create({'line_id': errObj.id, 'line_no': 'Debit/Credit Amount', 'details': msg})
                        self.unlink_move(move_id)
                    elif round(credit - debit, 2) > 0:
                        msg = 'Credit is greater than Debit. Mismatch Amount: {0}'.format(missmatch)
                        errObj.line_ids.create({'line_id': errObj.id, 'line_no': 'Debit/Credit Amount', 'details': msg})
                        self.unlink_move(move_id)
                    else:
                        journal = move_id.journal_id
                        sequence = journal.sequence_id.with_context(ir_sequence_date=move_id.date).next_by_id()
                        move_id.sudo().write({'state': 'posted',
                                              'name': sequence,
                                              'date': rec['POSTING-DATE'],
                                              'amount': debit})
                        errObj.sudo().write({'state': 'resolved'})
                        return move_id
            except Exception:
                self.unlink_move(move_id)
                errObj.line_ids.create({'line_id': errObj.id,
                                        'line_no': 'Unknown Error',
                                        'details': 'Unbalanced journal, amount variance is {0}'.format(missmatch)})

        return False

    def unlink_move(self, move):
        if move.state == 'draft':
            move.unlink()

    @api.multi
    def action_sftp_test_connection(self):
        """Check if the SFTP settings are correct."""

        if self.env.context.get('target') == 'source':
            connection = 'source'
        else:
            connection = 'destination'

        try:
            # Just open and close the connection
            with self.sftp_connection(connection):
                raise exceptions.Warning(_("Connection Test Succeeded!"))
        except (pysftp.CredentialException,
                pysftp.ConnectionException,
                pysftp.SSHException):
            _logger.info("Connection Test Failed!", exc_info=True)
            raise exceptions.Warning(_("Connection Test Failed!"))

    @api.one
    def directory_check(self, dirs):
        for dir in dirs:
            if not os.path.isdir(dir):
                try:
                    os.makedirs(dir)
                except OSError:
                    pass

    @api.multi
    def sftp_connection(self, connection):
        """Return a new SFTP connection with found parameters."""
        self.ensure_one()
        if connection == 'source':
            params = {
                "host": self.source_sftp_host,
                "username": self.source_sftp_user,
                "port": self.source_sftp_port,
            }
            _logger.debug(
                "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                extra=params)
            if self.source_sftp_private_key:
                params["private_key"] = self.source_sftp_private_key
                if self.source_sftp_password:
                    params["private_key_pass"] = self.source_sftp_password
            else:
                params["password"] = self.source_sftp_password
        else:
            params = {
                "host": self.dest_sftp_host,
                "username": self.dest_sftp_user,
                "port": self.dest_sftp_port,
            }
            _logger.debug(
                "Trying to connect to sftp://%(username)s@%(host)s:%(port)d",
                extra=params)
            if self.dest_sftp_private_key:
                params["private_key"] = self.dest_sftp_private_key
                if self.dest_sftp_password:
                    params["private_key_pass"] = self.dest_sftp_password
            else:
                params["password"] = self.dest_sftp_password

        return pysftp.Connection(**params)

    @api.multi
    @contextmanager
    def backup_log(self):
        """Log a backup result."""
        try:
            _logger.info("Starting database backup: %s", self.name)
            yield
        except:
            _logger.exception("Database backup failed: %s", self.name)
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
                "<p>%s</p><pre>%s</pre>" % (
                    _("Database backup failed."),
                    escaped_tb),
                subtype=self.env.ref(
                    "file_processing.mail_message_subtype_failure"
                ),
            )
        else:
            _logger.info("Database backup succeeded: %s", self.name)
            self.message_post(_("Database backup succeeded."))

    @api.multi
    @contextmanager
    def cleanup_log(self):
        """Log a possible cleanup failure."""
        self.ensure_one()
        try:
            _logger.info("Starting cleanup process after database backup: %s",
                         self.name)
            yield
        except:
            _logger.exception("Cleanup of old database backups failed: %s")
            escaped_tb = tools.html_escape(traceback.format_exc())
            self.message_post(
                "<p>%s</p><pre>%s</pre>" % (
                    _("Cleanup of old database backups failed."),
                    escaped_tb),
                subtype=self.env.ref("file_processing.failure"))
        else:
            _logger.info("Cleanup of old database backups succeeded: %s",
                         self.name)

    @api.one
    def move_file_src_to_des(self, source_con):
        dest_con = ''
        shutil.move(source_con, dest_con)

    @api.one
    def get_formatted_data(self, var_worksheet):
        worksheet_col = []  # list of columns
        for col in range(var_worksheet.ncols):
            worksheet_col.append(str(var_worksheet.cell(0, col).value))

        formatted_data = []  # collection of dict
        for row in range(1, var_worksheet.nrows):
            my_dict = {}
            for col in range(var_worksheet.ncols - 1):
                my_dict[worksheet_col[col]] = str(var_worksheet.cell(row, col).value)
            formatted_data.append(my_dict)

        return formatted_data

    @api.model
    def _needaction_domain_get(self):
        return [('status', '=', True)]


class ServerFileError(models.Model):
    _name = 'server.file.error'
    _description = "File Processing Error"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'

    name = fields.Char(string='Name')
    process_date = fields.Datetime(string="Process Date", default=fields.Datetime.now)
    file_path = fields.Char(string='File Path')
    ftp_ip = fields.Char(string='FTP IP')
    status = fields.Boolean(default=False, string='Status')
    errors = fields.Text(string='Error Details')
    error_count = fields.Char(string="Total Error", compute='_compute_error')
    state = fields.Selection([('issued', 'Issued'), ('resolved', 'Resolved')], default='issued')
    line_ids = fields.One2many('server.file.error.line', 'line_id', readonly=True)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'issued')]

    @api.depends('file_path', 'ftp_ip')
    def _compute_name(self):
        for rec in self:
            if rec.file_path and rec.ftp_ip:
                rec.name = "{0} and {1}".format(rec.ftp_ip, rec.file_path)

    @api.depends('line_ids')
    def _compute_error(self):
        for rec in self:
            rec.error_count = len(rec.line_ids)


class ServerFileErrorDetails(models.Model):
    _name = 'server.file.error.line'
    _description = "File Processing Error Details"
    _inherit = ["mail.thread"]
    _order = 'id asc'

    process_date = fields.Datetime(string="Process Date", default=fields.Datetime.now)
    line_no = fields.Char(string='Line No')
    status = fields.Boolean(default=False, string='Status')
    details = fields.Text(string='Error Details')
    line_id = fields.Many2one('server.file.error', ondelete='cascade')


class ServerFileSuccess(models.Model):
    _name = 'server.file.success'
    _description = "GLIF File Success"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'name desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    start_date = fields.Datetime(string='Start Datetime', required=True)
    stop_date = fields.Datetime(string='Stop Datetime', required=True)
    file_name = fields.Char(string='File Path', required=True)
    upload_file = fields.Binary(string="Upload File", attachment=True)
    time = fields.Text(string='Time', compute="_compute_time")
    move_id = fields.Many2one('account.move', string="Journal")
    status = fields.Boolean(default=False, string='Status')

    @api.depends('start_date', 'stop_date')
    def _compute_time(self):
        for rec in self:
            diff = dt.strptime(rec.stop_date, TIME_FORMAT) - dt.strptime(rec.start_date, TIME_FORMAT)
            rec.time = str(diff)

    @api.multi
    def unlink_glif(self):
        unlink = "UPDATE account_move SET state='draft' WHERE id=%s" % self.move_id.id
        self.env.cr.execute(unlink)
        self._cr.commit()
        if not self.env.cr.execute(unlink):
            self.move_id.unlink()
            self.unlink()
            self._cr.commit()


class GenerateCBSJournalSuccess(models.Model):
    _name = 'generate.cbs.journal.success'
    _description = "MDC Process"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'date desc'

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    date = fields.Datetime(string='Process Time', default=fields.Datetime.now, required=True)
    start_date = fields.Datetime(string='Start Datetime', required=True)
    stop_date = fields.Datetime(string='Stop Datetime', required=True)
    file_name = fields.Char(string='File Path', required=True)
    upload_file = fields.Binary(string="MDC File", attachment=True)
    time = fields.Text(string='Duration', compute="_compute_time")
    status = fields.Boolean(default=False, string='Status')
    journal_count = fields.Char(string="No of Journals", compute='_compute_journal', store=True)
    line_ids = fields.One2many('cbs.journal.line', 'line_id', string="Journal")
    state = fields.Selection([('mdc', 'MDC'), ('report', ' MDC Report')], default='mdc')
    mdc_report_file = fields.Binary(string="Report File", attachment=True)
    mdc_report_process_time = fields.Datetime(string='Process Time')
    has_report = fields.Boolean(default=False, attachment=True)

    @api.depends('start_date', 'stop_date')
    def _compute_time(self):
        for rec in self:
            diff = datetime.strptime(rec.stop_date, TIME_FORMAT) - datetime.strptime(rec.start_date, TIME_FORMAT)
            rec.time = str(diff)

    @api.depends('line_ids')
    def _compute_journal(self):
        for rec in self:
            rec.journal_count = len(rec.line_ids)

    @api.model
    def _needaction_domain_get(self):
        return [('state', '=', 'mdc')]


class CBSJournalLine(models.Model):
    _name = 'cbs.journal.line'
    _description = "CBS Journal Line"
    _inherit = ["mail.thread", "ir.needaction_mixin"]

    line_id = fields.Many2one('generate.cbs.journal.success', ondelete='cascade')
    move_id = fields.Many2one('account.move', string="Journals")


class SystemDateStatus(models.Model):
    _name = 'system.date.status'
    _description = "System Date Status"
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    _order = 'id desc'
    _rec_name = 'previous_date'

    previous_date = fields.Date(string='Previous Date', required=True)
    current_date = fields.Date(string='Current Date', required=True)
    create_date = fields.Datetime(string='Create Date', default=fields.Datetime.now, required=True)
    state = fields.Selection([('success', 'Success'), ('fail', 'Failed')], required=True)
