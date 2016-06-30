from openerp.osv import fields, osv

class res_partner(osv.osv):
    
    _inherit = 'res.partner'
    
    def _get_total_outstanding(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = partner.credit - partner.debit
        
        return res
    
    def _concat_address(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        address = ""
        for partner in self.browse(cr, uid, ids, context=context):
            if partner.street:
                address = partner.street
            if partner.street2:
                if len(address) > 0:
                    address = address + ", " + partner.street2
                else:
                    address = partner.street2
            if partner.city:
                if len(address) > 0:
                    address = address + ", " + partner.city
                else:
                    address = partner.city
            if partner.zip:
                if len(address) > 0:
                    address = address + ", " + partner.zip
                else:
                    address = partner.zip
            if partner.country_id:
                if len(address) > 0:
                    address = address + ", " + partner.country_id.name
                else:
                    address = partner.country_id.name
            res[partner.id] = address
        
        return res
    
    _columns = {
          'dealer':fields.boolean('Dealer', help="Check this box if this contact is a dealer."),
          'corporate':fields.boolean('Corporate', help="Check this box if this contact is a corporate."),
          'institution':fields.boolean('Institution', help="Check this box if this contact is a institution."),
          'retail':fields.boolean('Retailer', help="Check this box if this contact is a retail."),
          'area_id': fields.many2one("sale.area", 'Area'),
          'total_outstanding': fields.function(_get_total_outstanding, string="Outstanding", type="float"),
          'partner_address': fields.function(_concat_address, string='Address', type="char"),
        }
    
res_partner()
