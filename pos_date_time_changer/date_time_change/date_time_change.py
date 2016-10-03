# -*- coding: utf-8 -*-

from openerp import fields, models
import time

class pos_date_time_format(models.Model):
    _inherit = 'pos.config'

    date_format=fields.Many2one('more.formats','DateTime Format')
    def get_the_date(self, cr, uid,pos_config, context={}):
        iopo=int(pos_config)
        date_format=[]
        time_format=[]
        for i in self.browse(cr,uid,iopo,context=context):
            date_format.append(i.date_format.date_format)
            time_format.append(i.date_format.time_format)
        if isinstance(date_format[0], (bool)) or isinstance(time_format[0], (bool)):
            return [[0]]
        else:
            date=time.strftime(date_format[0])
            times=time.strftime(time_format[0])
            print('Here is the date :',date,'Here is the time : ',times)
            return [date +" "+ times]
pos_date_time_format()