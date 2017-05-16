from openerp import models, fields
from openerp import api

import os
# import pyodbc

# import sys
from zklib import zklib

# import time
# from zklib import zkconst

import pyodbc



class AttendanceSummary(models.Model):
    _name = 'hr.attendance.summary'
    _inherit = ['mail.thread']
    _description = 'Attendance and over time summary'    

    name = fields.Char(size=100, string='Title', required='True')
    period = fields.Many2one("account.period", "Period", required=True)
    state = fields.Selection([
        ('draft', "Draft"),
        ('generated', "Generated"),
        ('confirmed', "Confirmed"),
        ('approved', "Approved"),
    ], default='draft')


    """ Relational Fields """
    att_summary_lines = fields.One2many('hr.attendance.summary.line', 'att_summary_id', string='Summary Lines')

    # @api.model
    # def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    #     res = super(AttendanceSummary, self).fields_view_get(view_id, view_type, toolbar, submenu)
    #
    #     return res

    @api.multi
    def action_generated(self):
        self.state = 'generated'        

    
    @api.multi
    def action_draft(self):
        self.state = 'draft'
        
    @api.multi
    def action_confirm(self):
        for attendance in self:
            attendance.state = 'confirmed'
            
    @api.multi
    def action_done(self):
        for attendance in self:
            self.state = 'approved'


    @api.multi
    def action_db_connect(self):

        c = pyodbc.connect('DSN=MiConexion')
        csr = c.cursor()
        csr.execute("SELECT * FROM CHECKINOUT")
        row = csr.fetchall()
        print row

        # query = "SELECT * FROM CHECKINOUT"
        # crsr.execute(query)
        # rows = crsr.fetchall()
        # for row in rows:
        #     print row

        db_path = os.path.join("/opt/odoo/att_db/", "att2000.mdb")
        # os.path.join("ftp://192.168.1.47", "att2000.mdb")
        odbc_connection_str = 'DRIVER={MDBTools};DBQ=%s;' % (db_path)
        connection = pyodbc.connect(odbc_connection_str)
        cursor = connection.cursor()

        DBfile = 'opt/odoo/att_db/att2000.mdb'
        conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=' + DBfile)
        # use below conn if using with Access 2007, 2010 .accdb file
        # conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+DBfile)
        cursor = conn.cursor()

        SQL = 'SELECT Artist, AlbumName FROM RecordCollection ORDER BY Year;'
        for row in cursor.execute(SQL):  # cursors are iterable
            print row.Artist, row.AlbumName
            # print row # if print row it will return tuple of all fields

        cursor.close()
        conn.close()


        # dataFile = "att2000.mdb"
        # databaseFile = os.getcwd() + "\\" + dataFile
        # connectionString = "Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s" % databaseFile
        # dbConnection = pyodbc.connect(connectionString)
        # cursor = dbConnection.cursor()
        # cursor.execute("select top 5 * from Suppliers")
        # rows = cursor.fetchall()
        # for row in rows:
        #     print row.CompanyName


        db_path = os.path.join("/opt/odoo/att_db/", "att2000.mdb")
            # os.path.join("ftp://192.168.1.47", "att2000.mdb")
        odbc_connection_str = 'DRIVER={MDBTools};DBQ=%s;' % (db_path)
        connection = pyodbc.connect(odbc_connection_str)
        cursor = connection.cursor()

        query = "SELECT * FROM MSysObjects WHERE Type=1 AND Flags=0"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print row


        # zk = zklib.ZKLib("192.168.1.119", 4370)
        # ret = zk.connect()
        # print "connection:", ret

        # DBfile = '/opt/odoo/att_db/att2000.mdb'
        # conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=' + DBfile)
        # cursor = conn.cursor()
        # SQL = 'SELECT * FROM CHECKINOUT;'
        #
        # for row in cursor.execute(SQL):  # cursors are iterable
        #     print row
        #
        # cursor.close()
        # conn.close()


        # conn_str = (
        #     r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        #     r'DBQ=ftp://192.168.1.36/att2000.mdb;'
        # )
        # cnxn = pyodbc.connect(conn_str)
        # crsr = cnxn.cursor()
        # query = "SELECT * FROM CHECKINOUT"
        # crsr.execute(query)
        # rows = crsr.fetchall()
        # for row in rows:
        #     print row

        # db_path = os.path.join("/opt/odoo/att_db", "", "att2000.mdb")
        # odbc_connection_str = 'DRIVER={MDBTools};DBQ=%s;' % (db_path)
        # connection = pyodbc.connect(odbc_connection_str)
        # cursor = connection.cursor()
        #
        # query = "SELECT * FROM CHECKINOUT"
        # cursor.execute(query)
        # rows = cursor.fetchall()
        # for row in rows:
        #     print row

        # print "Hi......................................"
        # DBfile = '/opt/odoo/att_db/att2000.mdb'
        # conn = pyodbc.connect('DRIVER={Microsoft Access Driver (*.mdb)};DBQ=' + DBfile)
        # # use below conn if using with Access 2007, 2010 .accdb file
        # # conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+DBfile)
        # cursor = conn.cursor()
        #
        # SQL = 'SELECT Artist, AlbumName FROM RecordCollection ORDER BY Year;'
        # for row in cursor.execute(SQL):  # cursors are iterable
        #     print row.Artist, row.AlbumName
        #     # print row # if print row it will return tuple of all fields
        #
        # cursor.close()
        # conn.close()

    # db_file = r'''C:\x.mdb'''
    # user = ''
    # password = ''
    #
    # odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb)};DBQ=%s;UID=%s;PWD=%s' % \
    #                 (db_file, user, password)
    # # Or, for newer versions of the Access drivers:
    # odbc_conn_str = 'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=%s;UID=%s;PWD=%s' % \
    #                 (db_file, user, password)
    #
    # conn = pyodbc.connect(odbc_conn_str)
