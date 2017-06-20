from openerp import models, fields
from openerp import api
import pyodbc
import datetime
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import Warning, ValidationError


driver = '{ODBC Driver 13 for SQL Server}'
IN_CODE = 'IN'
OUT_CODE = 'OUT'

MAX_ATTEMPT_TO_SUCCESS = 5

get_BADGENUMBER = """SELECT DISTINCT (usr.BADGENUMBER)
                     FROM CHECKINOUT att
                     JOIN USERINFO usr ON usr.USERID = att.USERID
                     WHERE att.IsRead = 0 AND att.Id <= ?"""

get_employee_ids = """SELECT device_employee_acc, id
                      FROM hr_employee WHERE device_employee_acc IN %s"""

get_att_data_sql = """SELECT
                          usr.BADGENUMBER, att.VERIFYCODE, att.CHECKTIME, att.SENSORID
                      FROM CHECKINOUT att
                      JOIN USERINFO usr ON usr.USERID = att.USERID
                      WHERE att.IsRead = 0 AND att.Id <= ?
                      ORDER BY usr.BADGENUMBER, att.CHECKTIME ASC"""


class DeviceDetail(models.Model):
    _name = 'hr.attendance.device.detail'

    name = fields.Char(size=100, string='Location', required='True')
    is_active = fields.Boolean(string='Is Active', default=False)
    connection_type = fields.Selection([
        ('ip', "IP"),
        ('url', "URL"),
        ('port', "Port")
    ], string='Connection Type', required=True)

    server = fields.Char(size=100, string='Server Address')
    database = fields.Char(size=100, string='Database Name')

    username = fields.Char(size=100, string='Username')
    password = fields.Char(size=100, string='Password')



    last_update = fields.Datetime(string='Last Update')

    """ Relational Fields """
    device_lines = fields.One2many('hr.attendance.device.line', 'device_detail_id', string='Devices')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'This Location is already in use'),
    ]

    @api.multi
    def toggle_connect(self):
        self.is_active = not self.is_active

    @api.multi
    def action_pull_error_data(self):

        hr_employee_pool = self.env['hr.employee']

        hr_att_error_pool = self.env['hr.attendance.import.error']
        errorDataList = hr_att_error_pool.search([('attempt_to_success', '<=', MAX_ATTEMPT_TO_SUCCESS),
                                              ('import_id', '=', None)], order='id asc')
        for row in errorDataList:
            if row.employee_code:
                emp = hr_employee_pool.search([('device_employee_acc', '=', row.employee_code)], limit=1)
                if emp:
                    self.processErrorData(row, emp.id)
                    row.unlink()
                else:
                    row.write({'attempt_to_success': row.attempt_to_success + 1})

            else:
                row.write({'attempt_to_success': row.attempt_to_success + 1})

    def processErrorData(self, row, employeeId):

        hr_att_pool = self.env['hr.attendance']

        if row.check_in:
            self.createDataFromError(row, employeeId, hr_att_pool)
        elif row.check_out:

            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_in', '!=',False)], limit=1, order='check_in desc')

            if preAttData and preAttData.check_out is False:
                chk_in = self.getDateTimeFromStr(preAttData.check_in)
                durationInHour = (self.getDateTimeFromStr(row.check_out) - chk_in).total_seconds() / 60 / 60
                if durationInHour <=15 and durationInHour >= 0:
                    preAttData.write({'check_out': self.getDateTimeFromStr(row.check_out),
                                      'worked_hours': durationInHour,
                                      'write_date': datetime.datetime.now(),
                                      'has_error': False,
                                      'attendance_server_id': row.attendance_server_id})
                else:
                    self.createDataFromError(row, employeeId, hr_att_pool)
            else:
                self.createDataFromError(row, employeeId, hr_att_pool)

    def createDataFromError(self, row, employeeId, hr_att_pool):

        if row.check_in:
            create_vals = {'employee_id': employeeId,
                              'check_in': self.getDateTimeFromStr(row.check_in),
                              'create_date': datetime.datetime.now(),
                              'write_date': datetime.datetime.now(),
                              'has_error': True,
                              'manual_attendance_request': False,
                              'is_system_generated': True,
                              'attendance_server_id': row.attendance_server_id}
        else:
            create_vals = {'employee_id': employeeId,
                              'check_in': None,
                              'check_out': self.getDateTimeFromStr(row.check_out),
                              'create_date': datetime.datetime.now(),
                              'write_date': datetime.datetime.now(),
                              'has_error': True,
                              'manual_attendance_request': False,
                              'is_system_generated': True,
                              'attendance_server_id': row.attendance_server_id}
        res = hr_att_pool.create(create_vals)

    ############################################################################################################
    @api.multi
    def action_check_connection(self):

        isConnect = False
        conn = None
        cursor = None
        try:
            conn = pyodbc.connect('DRIVER=' + driver +';PORT=1433;SERVER=' +
                                self.server + ';PORT=1443;DATABASE=' +
                                self.database + ';UID=' + self.username +
                                ';PWD=' + self.password)
            cursor = conn.cursor()
            isConnect = True
        except Exception as e:
            isConnect = False
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
            if isConnect == True:
                raise Warning("Successfully connect to the "+self.server+ " server.")
            else:
                raise ValidationError("Unable to connect the "+self.server+ " server. Please check the configuration.")

    @api.multi
    def action_pull_data(self):

        conn = None
        cursor = None
        try:
            hr_att_device_pool = self.env['hr.attendance.device.detail']
            attDevice = hr_att_device_pool.search([('id', '=', self.id)])
            if attDevice is None:
                return

            conn = pyodbc.connect('DRIVER=' + driver + ';PORT=1433;SERVER=' +
                                  attDevice.server + ';PORT=1443;DATABASE=' +
                                  attDevice.database + ';UID=' + attDevice.username +
                                  ';PWD=' + attDevice.password)
            cursor = conn.cursor()

            currentDate = datetime.datetime.now()
            cursor.execute("""SELECT max(Id) FROM CHECKINOUT WHERE IsRead = 0""")
            maxId = cursor.fetchone()

            if maxId[0] is None:
                return

            self.processData(maxId[0], attDevice, conn, cursor)

            self.last_update = currentDate
        except Exception as e:
            msg = "Exception on gbs_hr_device_config-> device_details.py -> action_pull_data() at " + \
                  str(datetime.datetime.now()) + "  \n Error Message : " + str(e[0])
            _logger.error(msg)
            print ("Exception : ", msg)
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()

    def processData(self, maxId, attDevice, conn, cursor):

        deviceInOutCode = {}  # Where key is code and value is "IN" OR OUT
        for line in attDevice.device_lines:
            if line.in_code:
                deviceInOutCode[str(line.in_code)] = IN_CODE
            if line.out_code:
                deviceInOutCode[str(line.out_code)] = OUT_CODE

        # Map employee_id to device_employee_acc
        cursor.execute(get_BADGENUMBER, maxId)
        badge_numbers = cursor.fetchall()

        if badge_numbers is None:
            return

        badge_numbers_lst = []
        for item in badge_numbers:
            badge_numbers_lst.append(item[0])

        self._cr.execute(get_employee_ids, (tuple(badge_numbers_lst),))
        employee_ids = self._cr.fetchall()

        employeeIdMap = {} # Where key is device_employee_acc
        for item in employee_ids:
            employeeIdMap[str(item[0])] = item[1]

        cursor.execute(get_att_data_sql, maxId)
        att_rows = cursor.fetchall()
        _logger.debug("Attendance Date pull from " + attDevice.server + " : at " + str(datetime.datetime.now()) + " : " + str(att_rows))

        try:

            for row in att_rows:
                if self.isValidData(row, deviceInOutCode, employeeIdMap) == False:
                    self.saveAsError(row, employeeIdMap, deviceInOutCode, attDevice.id)
                else:
                    self.storeData(row, deviceInOutCode, employeeIdMap, attDevice.id)

            # Store all attendance data to application database.
            # Now Update on SQL Server Database(External)
            cursor.execute("UPDATE CHECKINOUT SET IsRead = 1 WHERE id <=? AND IsRead = 0", maxId)
            conn.commit()
        except Exception as e:
            self.env.cr.rollback()
            msg = "Exception on gbs_hr_device_config-> device_details.py -> processData() at " + \
                  str(datetime.datetime.now()) + ": \n Attendance Data: " + str(row) + "  \n Error Message : " + str(e[0])
            _logger.error(msg)
            print (msg)



    def storeData(self, row, deviceInOutCode, employeeIdMap, deviceId):

        hr_att_pool = self.env['hr.attendance']

        employeeId = employeeIdMap.get(row[0])

        if(deviceInOutCode.get(str(row[1])) == IN_CODE):
            self.createData(row, employeeId, IN_CODE, hr_att_pool, deviceId)
        elif(deviceInOutCode.get(str(row[1])) == OUT_CODE):

            preAttData = hr_att_pool.search([('employee_id', '=', employeeId),
                                             ('check_in', '!=',False)], limit=1, order='check_in desc')

            # preAttData = hr_att_pool.search([('employee_id', '=', employeeId)], limit=1,
            #                                                   order='check_in desc')

            if preAttData and preAttData.check_out is False:
                chk_in = self.getDateTimeFromStr(preAttData.check_in)
                durationInHour = (self.convertDateTime(row[2]) - chk_in).total_seconds() / 60 / 60
                if durationInHour <=15 and durationInHour >= 0:
                    preAttData.write({'check_out': self.convertDateTime(row[2]),
                                      'worked_hours':durationInHour,
                                      'write_date':datetime.datetime.now(),
                                      'has_error': False,
                                      'attendance_server_id': deviceId
                                      })
                else:
                    self.createData(row, employeeId, OUT_CODE, hr_att_pool, deviceId)
            else:
                self.createData(row, employeeId, OUT_CODE, hr_att_pool, deviceId)

    def createData(self, row, employeeId, inOrOut, hr_att_pool, deviceId):

        if inOrOut == IN_CODE:
            create_vals = {'employee_id': employeeId,
                              'check_in': self.convertDateTime(row[2]),
                              'create_date': datetime.datetime.now(),
                              'write_date': datetime.datetime.now(),
                              'has_error': True,
                              'manual_attendance_request': False,
                              'is_system_generated': True,
                              'attendance_server_id': deviceId}
        else:
            create_vals = {'employee_id': employeeId,
                              'check_in': None,
                              'check_out': self.convertDateTime(row[2]),
                              'create_date': datetime.datetime.now(),
                              'write_date': datetime.datetime.now(),
                              'has_error': True,
                              'manual_attendance_request': False,
                              'is_system_generated': True,
                              'attendance_server_id': deviceId}
        res = hr_att_pool.create(create_vals)




    def saveAsError(self, row, employeeIdMap, deviceInOutCode, serverId):

        attendance_error_obj = self.env['hr.attendance.import.error']

        error_vals = {}
        if (deviceInOutCode.get(str(row[1])) == IN_CODE):
            error_vals['check_in'] = self.convertDateTime(row[2])
        else:
            error_vals['check_out'] = self.convertDateTime(row[2])

        if employeeIdMap.get(row[0]) is not None:
            error_vals['employee_code'] = employeeIdMap.get(row[0])
        else:
            error_vals['employee_code'] = row[0]

        error_vals['attendance_server_id'] = serverId

        attendance_error_obj.create(error_vals)

    def isValidData(self, row, deviceInOutCode, employeeIdMap):
        if row[0] is None: # Check device_employee_acc is not null
            return False
        if employeeIdMap.get(row[0]) is None: # Check device_employee_acc is mapped or not
            return False
        if row[1] is None: # Check in_out code is not null
            return False
        if deviceInOutCode.get(str(row[1])) != IN_CODE and deviceInOutCode.get(str(row[1])) != OUT_CODE: # Check in_out code is valid or not
            return False
        if row[2] is None: # Check time is not null
            return False
        if row[3] is None: # Check sensor_id is not null
            return False
        return True

    def getDateTimeFromStr(self, dateStr):
        if dateStr:
            return datetime.datetime.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        else:
            return None

    def convertDateTime(self, dateStr):
        if dateStr:
            return dateStr + timedelta(hours=-6)