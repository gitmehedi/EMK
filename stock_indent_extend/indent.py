from openerp.osv import fields, osv
from openerp.tools.translate import _

class indent_indent(osv.Model):
    _inherit = 'indent.indent'
    
    def _get_default_warehouse(self, cr, uid, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        company_id = self.pool.get('res.users').browse(cr, uid, uid).company_id.id
        warehouse_ids = warehouse_obj.search(cr, uid, [('company_id', '=', company_id)], context=context)
        warehouse_id = warehouse_ids and warehouse_ids[0] or False
        return warehouse_id
    
    def _get_source_location(self, cr, uid, context=None):
        warehouse_obj = self.pool.get('stock.warehouse')
        warehouse_id = self._get_default_warehouse(cr, uid, context)
        if warehouse_id:
            warehouse = warehouse_obj.browse(cr, uid, warehouse_id)
            if warehouse and warehouse.lot_stock_id:
                location_id = warehouse.lot_stock_id.id or False
            else:
                return False
        else:
            return False
        
        return location_id
    
    def _check_consumption(self, cr, uid, ids, name, args, context=None):
        res = {}
        for indent in self.browse(cr, uid, ids, context=context):
            if indent.department_id and (indent.department_id.usage == 'production'):
                res[indent.id] = True
            else:
                res[indent.id] = False
                
        return res
    
    _columns = {
        'source_department_id': fields.many2one('stock.location', 'From Department', required=True, readonly=True, track_visibility='onchange', states={'draft': [('readonly', False)]}),
        'consumption': fields.function(_check_consumption, method=True, type='boolean', string='Consumption', store=True)
    }
    
    _defaults = {
        'source_department_id': _get_source_location,
    }
    
    def _prepare_indent_line_move(self, cr, uid, indent, line, picking_id, date_planned, context=None):
        if indent and indent.source_department_id:
            location_id = indent.source_department_id.id
        else:
            location_id = indent.warehouse_id.lot_stock_id.id

        res = {
            'name': line.name,
            'indent_id':indent.id,
            'picking_id': picking_id,
            'picking_type_id': indent.picking_type_id.id or False,
            'product_id': line.product_id.id,
            'date': date_planned,
            'date_expected': date_planned,
            'product_uom_qty': line.product_uom_qty,
            'product_uom': line.product_uom.id,
            'product_uos_qty': (line.product_uos and line.product_uos_qty) or line.product_uom_qty,
            'product_uos': (line.product_uos and line.product_uos.id)\
                    or line.product_uom.id,
            'location_id': location_id,
            'location_dest_id': indent.department_id.id,
            'state': 'draft',
            'price_unit': line.product_id.standard_price or 0.0
        }

        if line.product_id.type in ('service'):
            if not line.original_product_id:
                raise osv.except_osv(_("Warning !"), _("You must define material or parts that you are going to repair !"))

            upd_res = {
                'product_id':line.original_product_id.id,
                'product_uom': line.original_product_id.uom_id.id,
                'product_uos':line.original_product_id.uom_id.id
            }
            res.update(upd_res)

        if indent.company_id:
            res = dict(res, company_id = indent.company_id.id)
        return res
    
indent_indent()