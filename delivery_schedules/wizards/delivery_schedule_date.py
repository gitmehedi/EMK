from odoo import api, fields, models

import datetime


class DeliveryScheduleDate(models.TransientModel):
    _name = 'delivery.schedule.date.wizard'

    schedule_date = fields.Date(string="Schedule Date", required=True)


    @api.multi
    def process_schedule_date(self):
        for ds in self:

            schedule_line_obj = ds.env['delivery.schedules.line'].search(
                [('schedule_line_date', '=', ds.schedule_date),
                 ('operating_unit_id', '=', ds.env.user.default_operating_unit_id.id)])

            sql = """DELETE FROM delivery_schedule_date_wise"""
            ds._cr.execute(sql)

            for line in schedule_line_obj:
                vals = {}
                vals['partner_id'] = line.partner_id.id
                vals['pending_do'] = line.pending_do.id
                vals['do_qty'] = line.do_qty
                vals['undelivered_qty'] = line.undelivered_qty
                vals['uom_id'] = line.uom_id.id
                vals['scheduled_qty'] = line.scheduled_qty
                vals['remarks'] = line.remarks

                ds.env['delivery.schedule.date.wise'].create(vals)

            view = self.env.ref('delivery_schedules.delivery_schedule_date_wise_tree')

            return {
                'name': ('Daily Delivery Schedules'),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'delivery.schedule.date.wise',
               # 'domain': [('id', '=', pricelist_obj.ids)],
                'view_id': [view.id],
                'type': 'ir.actions.act_window'
            }