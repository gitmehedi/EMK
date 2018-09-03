from odoo import api, fields, models,_



class SalesChannel(models.Model):
    _name = "sales.channel"

    name = fields.Char(string='Name',required=True)
    operating_unit_id = fields.Many2one('operating.unit',string='Operating Unit',required=True)
    employee_id = fields.Many2one('hr.employee',string='Approver Manager', required=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',required=False,)


    @api.onchange('operating_unit_id')
    def _onchange_OP_unit(self):
        if self.operating_unit_id:
            self._cr.execute("""SELECT * FROM stock_warehouse WHERE operating_unit_id= %s LIMIT 1""",
                             (self.operating_unit_id.id,))  # Never remove the comma after the parameter
            warehouse = self._cr.fetchall()

            self.warehouse_id =  warehouse[0][0]

