# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError

import json
import ast


class KsDashboardNinjaItems(models.Model):
    _name = 'ks_dashboard_ninja.item'

    name = fields.Char(string="Name", size=256)
    ks_model_id = fields.Many2one('ir.model', string='Model', required=True,
                                  domain="[('access_ids','!=',False),('transient','=',False),('model','not ilike','base_import%'),('model','not ilike','ir.%'),('model','not ilike','web_editor.%'),('model','not ilike','web_tour.%'),('model','!=','mail.thread'),('model','!=','ks_dashboard_ninja.item'),('model','!=','ks_dashboard_ninja.board'),('model','!=','ks_dashboard_ninja.board_template')]")
    ks_is_model_valid = fields.Boolean()
    ks_domain = fields.Char(string="Domain")
    ks_dashboard_ninja_board_id = fields.Many2one('ks_dashboard_ninja.board',
                                                  default=lambda self: self._context['ks_dashboard_id'] if 'ks_dashboard_id' in self._context else False)
    ks_background_color = fields.Char(default="#337ab7,0.99", string="Background Color")
    ks_icon = fields.Binary(string="Icon", attachment=True)
    ks_default_icon = fields.Char(string="Icon", default="bar-chart")
    ks_default_icon_color = fields.Char(default="#ffffff,0.99", string="Icon Color")
    ks_icon_select = fields.Char(string="Icon Option", default="Default")
    ks_font_color = fields.Char(default="#ffffff,0.99", string="Font Color")
    ks_dashboard_item_theme = fields.Char(default="blue", string="Theme")
    ks_layout = fields.Selection([('layout1', 'Layout 1'),
                                  ('layout2', 'Layout 2'),
                                  ('layout3', 'Layout 3'),
                                  ('layout4', 'Layout 4'),
                                  ('layout5', 'Layout 5'),
                                  ('layout6', 'Layout 6'),
                                  ], default=('layout1'), required=True, string="Layout")
    ks_preview = fields.Integer(default=1,string="Preview")
    ks_model_name = fields.Char(related='ks_model_id.model')

    ks_record_count_type = fields.Selection([('count', 'Count'),
                                             ('sum', 'Sum'),
                                             ('average', 'Average')], string="Record Count Type", default="count")
    ks_record_count = fields.Float(string="Record Count", compute='ks_get_record_count', readonly=True)
    ks_record_field = fields.Many2one('ir.model.fields',
                                      domain="[('model_id','=',ks_model_id),('name','!=','id'),'|','|',('ttype','=','integer'),('ttype','=','float'),('ttype','=','monetary')]",
                                      string="Record Field")

    # Condition to tell if date filter is applied or not
    ks_isDateFilterApplied = fields.Boolean(default=False)
    # This field will store on which field the date filter will be applied
    ks_date_filter_field = fields.Many2one('ir.model.fields',
                                           domain="[('model_id','=',ks_model_id),'|',('ttype','=','date'),('ttype','=','datetime')]",
                                           string="Date Filter Field")
    #charts related field
    ks_dashboard_item_type = fields.Selection([('ks_tile', 'Tile'),
                                               ('ks_bar_chart', 'Bar Chart'),
                                               ('ks_line_chart', 'Line Chart'),
                                               ('ks_area_chart', 'Area Chart'),
                                               ('ks_pie_chart', 'Pie Chart'),
                                               ('ks_doughnut_chart', 'Doughnut Chart'),
                                               ('ks_polarArea_chart', 'Polar Area Chart'),
                                               ('ks_list_view', 'List View'),
                                               ], default=lambda self: self._context.get('ks_dashboard_item_type','ks_tile'), required=True, string="Dashboard Item Type")

    ks_chart_groupby_type = fields.Char(compute='get_chart_groupby_type')
    ks_chart_relation_groupby = fields.Many2one('ir.model.fields',
                                                domain="[('model_id','=',ks_model_id),('name','!=','id'),('store','=',True),'|',"
                                                       "('ttype','=','many2one'),('ttype','=','datetime')]",
                                                string="Group By")

    ks_chart_date_groupby = fields.Selection([('day', 'Day'),
                                              ('week', 'Week'),
                                              ('month', 'Month'),
                                              ('quarter', 'Quarter'),
                                              ('year', 'Year'),
                                              ], string="Dashboard Item Chart Group By Type")
    ks_graph_preview = fields.Char(string="Preview", default="Graph Preview")
    ks_chart_data = fields.Char(string="Chart Data in string form", compute='ks_get_chart_data')
    ks_chart_data_count_type = fields.Selection([('count','Count'),('sum', 'Sum'), ('average', 'Average')],
                                                string="Chart Data Count Type", default="sum")
    ks_chart_measure_field = fields.Many2many('ir.model.fields',
                                              domain="[('model_id','=',ks_model_id),('name','!=','id'),('store','=',True),'|','|',"
                                                     "('ttype','=','integer'),('ttype','=','float'),"
                                                     "('ttype','=','monetary')]",
                                              string="Record Field")

    ks_sort_by_field = fields.Many2one('ir.model.fields',
                                       domain="[('model_id','=',ks_model_id),('name','!=','id'),('store','=',True),"
                                              "('ttype','!=','one2many'),('ttype','!=','many2one'),('ttype','!=','binary')]",
                                       string="Sort By Field")
    ks_sort_by_order = fields.Selection([('ASC', 'Ascending'), ('DESC', 'Descending')],
                                        string="Sort Order")
    ks_record_data_limit = fields.Integer(string="Record Limit")

    # This field main purpose is to only store the ordering of the many2many fields.
    ks_many2many_field_ordering = fields.Char()

    ks_list_view_preview = fields.Char(string="List View Preview", default="List View Preview")

    ks_chart_item_color = fields.Selection(
        [('default', 'Default'), ('cool', 'Cool'), ('warm', 'Warm'), ('neon', 'Neon')],
        string="Chart Color Palette", default="default")

    #list view related field
    ks_list_view_fields = fields.Many2many('ir.model.fields', 'ks_dn_list_field_rel', 'list_field_id', 'field_id',
                                           domain="[('model_id','=',ks_model_id),('store','=',True),"
                                                  "('ttype','!=','one2many'),('ttype','!=','many2many'),('ttype','!=','binary')]",
                                           string="Fields to show in list")
    ks_list_view_data = fields.Char(string="List View Data in JSon", compute='ks_get_list_view_data')

    # -------------------- Multi Company Feature ---------------------
    ks_company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.multi
    @api.onchange('ks_chart_relation_groupby')
    def get_chart_groupby_type(self):
        for rec in self:
            if rec.ks_chart_relation_groupby.ttype == 'datetime':
                rec.ks_chart_groupby_type = 'date_type'
            elif rec.ks_chart_relation_groupby.ttype == 'many2one':
                rec.ks_chart_groupby_type = 'relational_type'
                rec.ks_chart_date_groupby = False
            else:
                rec.ks_chart_groupby_type = 'none'
                rec.ks_chart_date_groupby = False

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        read_data = super(KsDashboardNinjaItems, self).read(fields, load=load)
        for rec in self:
            if rec['ks_many2many_field_ordering']:
                ks_many2many_field_ordering = json.loads(rec['ks_many2many_field_ordering'])
                if rec['ks_list_view_fields']:
                    rec['ks_list_view_fields'] = rec['ks_list_view_fields'].browse(
                        ks_many2many_field_ordering['ks_list_view_fields'])
        return read_data

    @api.model
    def create(self, values):
        """ Override to save list view fields ordering """
        if values.get('ks_list_view_fields', False):
            ks_many2many_field_ordering = {
                'ks_list_view_fields': values['ks_list_view_fields'][0][2],
            }
            values['ks_many2many_field_ordering'] = json.dumps(ks_many2many_field_ordering)
        return super(KsDashboardNinjaItems, self).create(
            values)

    @api.multi
    def write(self, values):
        for rec in self:
            if rec['ks_many2many_field_ordering']:
                ks_many2many_field_ordering = json.loads(rec['ks_many2many_field_ordering'])
            else:
                ks_many2many_field_ordering = {}
            if values.get('ks_list_view_fields', False):
                ks_many2many_field_ordering['ks_list_view_fields'] = values['ks_list_view_fields'][0][2]
            values['ks_many2many_field_ordering'] = json.dumps(ks_many2many_field_ordering)

        return super(KsDashboardNinjaItems, self).write(values)

    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if not name:
                name = rec.ks_model_id.name
            res.append((rec.id, name))
        return res


     # Using this function just to let js call rpc to load some data later
    @api.model
    def ks_chart_load(self):
        return True


    @api.onchange('ks_layout')
    def layout_four_font_change(self):
        if self.ks_layout == 'layout4':
            self.ks_font_color = self.ks_background_color
            self.ks_default_icon_color = "#ffffff,0.99"
        elif self.ks_layout == 'layout6':
            self.ks_font_color = "#ffffff,0.99"
            self.ks_default_icon_color = self.ks_get_dark_color(self.ks_background_color.split(',')[0],
                                                                self.ks_background_color.split(',')[1])
        else:
            self.ks_default_icon_color = "#ffffff,0.99"
            self.ks_font_color = "#ffffff,0.99"

    # To convert color into 10% darker. Percentage amount is hardcoded. Change amt if want to change percentage.
    def ks_get_dark_color(self, color, opacity):
        num = int(color[1:], 16)
        amt = -25
        R = (num >> 16) + amt
        R = (255 if R > 255 else 0 if R < 0 else R) * 0x10000
        G = (num >> 8 & 0x00FF) + amt
        G = (255 if G > 255 else 0 if G < 0 else G) * 0x100
        B = (num & 0x0000FF) + amt
        B = (255 if B > 255 else 0 if B < 0 else B)
        return "#" + hex(0x1000000 + R + G + B).split('x')[1][1:] + "," + opacity

    @api.one
    @api.constrains('ks_is_model_valid','ks_domain')
    def _check_model_valid(self):
        if not self.ks_is_model_valid:
            raise ValidationError("Current Model cannot be selected for dashboard item. Please Choose correct model.")
        self.ks_get_record_count()
        self.ks_get_chart_data()

    @api.multi
    @api.depends('ks_chart_measure_field', 'ks_chart_relation_groupby', 'ks_chart_date_groupby', 'ks_domain',
                 'ks_dashboard_item_type', 'ks_model_id', 'ks_sort_by_field', 'ks_sort_by_order',
                 'ks_record_data_limit', 'ks_chart_data_count_type')
    def ks_get_chart_data(self):
        for rec in self:
            # To handel empty selection in item form view (v10 issue)
            if rec.ks_dashboard_item_type and rec.ks_dashboard_item_type != 'ks_tile' and rec.ks_dashboard_item_type != 'ks_list_view' and rec.ks_model_id:
                if rec.ks_chart_relation_groupby:
                    ks_chart_data = {'labels': [], 'datasets': []}
                    ks_chart_measure_field = []
                    if rec.ks_chart_data_count_type=="count":
                        ks_chart_data['datasets'].append({'data': [], 'label': "Count"})
                    else:
                        for res in rec.ks_chart_measure_field:
                            ks_chart_measure_field.append(res.name)
                            ks_chart_data['datasets'].append({'data': [], 'label': res.field_description})
                    # ks_chart_records = self.ks_fetch_model_data(rec.ks_model_name,rec.ks_domain,'search',rec)
                    # ks_chart_measure_field = [res.name for res in rec.ks_chart_measure_field]
                    ks_chart_groupby_relation_field = rec.ks_chart_relation_groupby.name
                    ks_chart_domain = self.ks_convert_into_proper_domain(rec.ks_domain, rec)
                    orderby = rec.ks_sort_by_field.name if rec.ks_sort_by_field else "id"

                    if rec.ks_sort_by_order:
                        orderby = orderby + " " + rec.ks_sort_by_order
                    limit = rec.ks_record_data_limit if rec.ks_record_data_limit else False
                    if (rec.ks_chart_data_count_type != "count" and ks_chart_measure_field) or (
                            rec.ks_chart_data_count_type == "count" and not ks_chart_measure_field):
                        if rec.ks_chart_groupby_type == 'relational_type' and rec.ks_chart_relation_groupby:
                            ks_chart_data['groupByIds'] = []
                            ks_chart_records = self.env[rec.ks_model_name].read_group(ks_chart_domain,
                                                                                      ks_chart_measure_field + [
                                                                                          ks_chart_groupby_relation_field],
                                                                                      [ks_chart_groupby_relation_field],
                                                                                      orderby=orderby, limit=limit)

                            for res in ks_chart_records:
                                if res[ks_chart_groupby_relation_field] and all(
                                        measure_field in res for measure_field in ks_chart_measure_field):
                                    ks_chart_data['labels'].append(res[ks_chart_groupby_relation_field][1])
                                    ks_chart_data['groupByIds'].append(res[ks_chart_groupby_relation_field][0])
                                    counter = 0
                                    if ks_chart_measure_field:
                                        for field_rec in ks_chart_measure_field:
                                            data = res[field_rec] if rec.ks_chart_data_count_type == 'sum' else res[field_rec] / \
                                                                                                                res[
                                                                                                                    ks_chart_groupby_relation_field + "_count"]
                                            ks_chart_data['datasets'][counter]['data'].append(data)
                                            counter += 1
                                    else:
                                        data = res[ks_chart_groupby_relation_field + "_count"]
                                        ks_chart_data['datasets'][0]['data'].append(data)

                        elif rec.ks_chart_groupby_type == 'date_type' and rec.ks_chart_date_groupby :
                            ks_chart_records = self.env[rec.ks_model_name].read_group(ks_chart_domain,
                                                                                      ks_chart_measure_field + [
                                                                                          ks_chart_groupby_relation_field],
                                                                                      [
                                                                                          ks_chart_groupby_relation_field + ":" + rec.ks_chart_date_groupby],
                                                                                      orderby=orderby, limit=limit)
                            # Converting in chart data format
                            # chart_data = {labels:[], datasets:[{}]}
                            for res in ks_chart_records:
                                if res[ks_chart_groupby_relation_field + ":" + rec.ks_chart_date_groupby] and all(
                                        measure_field in res for measure_field in ks_chart_measure_field):
                                    ks_chart_data['labels'].append(
                                        res[ks_chart_groupby_relation_field + ":" + rec.ks_chart_date_groupby])
                                    counter = 0
                                    if ks_chart_measure_field:
                                        for field_rec in ks_chart_measure_field:
                                            data = res[
                                                field_rec] if rec.ks_chart_data_count_type == 'sum' else res[field_rec] / res[
                                                ks_chart_groupby_relation_field + "_count"]
                                            ks_chart_data['datasets'][counter]['data'].append(data)
                                            counter += 1
                                    else:
                                        data = res[ks_chart_groupby_relation_field + "_count"]
                                        ks_chart_data['datasets'][0]['data'].append(data)
                        else:
                            rec.ks_chart_data = False

                    rec.ks_chart_data = json.dumps(ks_chart_data)
                else:
                    rec.ks_chart_data = False
            else:
                rec.ks_chart_data = False


    @api.multi
    @api.depends('ks_domain', 'ks_dashboard_item_type', 'ks_model_id', 'ks_sort_by_field', 'ks_sort_by_order',
                 'ks_record_data_limit', 'ks_list_view_fields')
    def ks_get_list_view_data(self):
        for rec in self:
            if rec.ks_dashboard_item_type and rec.ks_dashboard_item_type == 'ks_list_view' and rec.ks_model_id and rec.ks_list_view_fields:
                ks_list_view_data = {'label': [res.field_description for res in rec.ks_list_view_fields],
                                     'data_rows': [], 'model': rec.ks_model_name}
                ks_list_view_fields = [res.name for res in rec.ks_list_view_fields]
                ks_list_view_type = [res.ttype for res in rec.ks_list_view_fields]
                ks_chart_domain = self.ks_convert_into_proper_domain(rec.ks_domain, rec)
                orderby = rec.ks_sort_by_field.name if rec.ks_sort_by_field else "id"
                if rec.ks_sort_by_order:
                    orderby = orderby + " " + rec.ks_sort_by_order
                limit = rec.ks_record_data_limit if rec.ks_record_data_limit else False
                ks_list_view_records = self.env[rec.ks_model_name].sudo().search_read(ks_chart_domain,
                                                                                      ks_list_view_fields,
                                                                                      order=orderby, limit=limit)

                for res in ks_list_view_records:
                    counter = 0
                    data_row = {'id': res['id'], 'data': []}
                    for field_rec in ks_list_view_fields:
                        if ks_list_view_type[counter] == "datetime" or ks_list_view_type[counter] == "date":
                            res[field_rec] = res[field_rec].split(" ")[0]
                        elif ks_list_view_type[counter]=="many2one":
                            if res[field_rec]:
                                res[field_rec] = res[field_rec][1]

                        data_row['data'].append(res[field_rec])
                        counter += 1
                    ks_list_view_data['data_rows'].append(data_row)

                rec.ks_list_view_data = json.dumps(ks_list_view_data)


    @api.onchange('ks_model_id')
    def make_record_field_empty(self):
        for rec in self:
            rec.ks_date_filter_field = False
            if rec.ks_model_id:
                if rec.env[rec.ks_model_id.model]._abstract:
                    rec.ks_is_model_valid = False
                    rec.ks_domain = "Current Model cannot be selected (Abstact Model)."
                else:
                    datetime_field_list = rec.ks_date_filter_field.search(
                        [('model_id', '=', rec.ks_model_id.id), '|', ('ttype', '=', 'date'),
                         ('ttype', '=', 'datetime')]).read(['id', 'name'])
                    for field in datetime_field_list:
                        if str(field['name']) == 'create_date':
                            rec.ks_date_filter_field = field['id']
            else:
                rec.ks_date_filter_field = False
                rec.ks_is_model_valid = True
                rec.ks_domain = False

            rec.ks_record_field = False
            rec.ks_chart_relation_groupby = False
            rec.ks_chart_measure_field = False
            rec.ks_chart_relation_groupby = False
            rec.ks_chart_date_groupby = False
            rec.ks_sort_by_field = False
            rec.ks_sort_by_order = False
            rec.ks_record_data_limit = False
            rec.ks_list_view_fields = False

    @api.onchange('ks_dashboard_item_theme')
    def change_dashboard_item_theme(self):
        if self.ks_dashboard_item_theme == "red":
            self.ks_background_color = "#d9534f,0.99"
            self.ks_default_icon_color = "#ffffff,0.99"
            self.ks_font_color = "#ffffff,0.99"
        elif self.ks_dashboard_item_theme == "blue":
            self.ks_background_color = "#337ab7,0.99"
            self.ks_default_icon_color = "#ffffff,0.99"
            self.ks_font_color = "#ffffff,0.99"
        elif self.ks_dashboard_item_theme == "yellow":
            self.ks_background_color = "#f0ad4e,0.99"
            self.ks_default_icon_color = "#ffffff,0.99"
            self.ks_font_color = "#ffffff,0.99"
        elif self.ks_dashboard_item_theme == "green":
            self.ks_background_color = "#5cb85c,0.99"
            self.ks_default_icon_color = "#ffffff,0.99"
            self.ks_font_color = "#ffffff,0.99"

        if self.ks_layout == 'layout4':
            self.ks_font_color = self.ks_background_color

        elif self.ks_layout == 'layout6':
            self.ks_default_icon_color = self.ks_get_dark_color(self.ks_background_color.split(',')[0],
                                                                self.ks_background_color.split(',')[1])

    @api.multi
    @api.depends('ks_record_count_type', 'ks_model_id', 'ks_domain', 'ks_record_field')
    def ks_get_record_count(self):
        # Used try cache to handle invalid domain error.
        for rec in self:
            if rec.ks_is_model_valid:
                if rec.ks_record_count_type == 'count':
                    rec.ks_record_count = rec.ks_fetch_model_data(rec.ks_model_name, rec.ks_domain, 'search_count',rec)
                elif rec.ks_record_count_type == 'sum' and rec.ks_record_field:
                    ks_records = rec.ks_fetch_model_data(rec.ks_model_name, rec.ks_domain, 'search',rec)
                    for filtered_records in ks_records:
                        rec.ks_record_count += filtered_records[rec.ks_record_field.name]
                elif rec.ks_record_count_type == 'average' and rec.ks_record_field:
                    ks_records = rec.ks_fetch_model_data(rec.ks_model_name, rec.ks_domain, 'search',rec)
                    ks_record_count = rec.ks_fetch_model_data(rec.ks_model_name, rec.ks_domain, 'search_count',rec)
                    for filtered_records in ks_records:
                        rec.ks_record_count += filtered_records[rec.ks_record_field.name]
                    rec.ks_record_count = rec.ks_record_count / ks_record_count if ks_record_count else 0
                else:
                    rec.ks_record_count = 0

    # Writing separate function to fetch dashboard item data
    def ks_fetch_model_data(self, ks_model_name,ks_domain, ks_func,rec):
        if ks_domain and ks_domain != '[]' and ks_model_name:
            try:
                proper_domain = self.ks_convert_into_proper_domain(ks_domain,rec)
                if ks_func == 'search_count':
                    data = self.env[ks_model_name].sudo().search_count(proper_domain)
                elif ks_func == 'search':
                    data = self.env[ks_model_name].sudo().search(proper_domain)
            except ValueError as invalidFieldError:
                if 'could not convert' in invalidFieldError.message:
                    raise ValidationError('Invalid Domain Value : %s' % invalidFieldError.message)
                elif 'osv.ExtendedLeaf' in invalidFieldError.message:
                    raise ValidationError(
                        (invalidFieldError.message).replace('leaf', 'domain').replace('"<osv.ExtendedLeaf:', '').replace(
                            '(ctx: )>"', ''))
                elif 'leaf' in invalidFieldError.message:
                    raise ValidationError((invalidFieldError.message).replace('leaf', 'Domain Operator in:'))
                else:
                    raise ValidationError(
                        "Domain Syntax is wrong. \nProper Syntax Example : [['<field_name'>,'<operator>','<value_to_compare>']]")
            except AccessError as ae:
                return 0
                # raise AccessError("Not Loaded one item")
            except Exception as syntaxError:
                raise ValidationError(
                    "Domain Syntax is wrong. \nProper Syntax Example : [['<field_name'>,'<operator>','<value_to_compare>']]")
        elif ks_model_name:
            # Have to put extra if condition here because on load,model giving False value
            proper_domain = self.ks_convert_into_proper_domain(False, rec)
            if ks_func == 'search_count':
                try:
                    data = self.env[ks_model_name].search_count(proper_domain)
                except AccessError as ae:
                    return 0
                    # raise AccessError("Not Loaded one item")
            elif ks_func == 'search':
                data = self.env[ks_model_name].sudo().search(proper_domain)
        else :
            return 0
        return data

    # This function working has to be changed domain with widget
    def ks_convert_into_proper_domain(self,ks_domain,rec):
        proper_domain = []
        selected_start_date = rec.env["ks_dashboard_ninja.board"].browse(
            rec.ks_dashboard_ninja_board_id.id).ks_dashboard_start_date
        selected_end_date = rec.env["ks_dashboard_ninja.board"].browse(
            rec.ks_dashboard_ninja_board_id.id).ks_dashboard_end_date
        if ks_domain:
            try:
                ks_domain = list(ast.literal_eval(ks_domain))
                for element in ks_domain:
                    proper_domain.append(element) if type(element) != list else proper_domain.append(tuple(element))
                if selected_start_date and selected_end_date and rec.ks_date_filter_field:
                    proper_domain.extend([(rec.ks_date_filter_field.name, ">=", selected_start_date),
                                          (rec.ks_date_filter_field.name, "<=", selected_end_date)])
                    rec.ks_isDateFilterApplied = True
                else:
                    rec.ks_isDateFilterApplied = False
                return proper_domain
            except Exception :
                raise ValidationError(
                    "Domain Syntax is wrong. \nProper Syntax Example : [['<field_name'>,'<operator>','<value_to_compare>']]")

        else:
            if selected_end_date and selected_end_date and rec.ks_date_filter_field:
                proper_domain = [(rec.ks_date_filter_field.name, ">=", selected_start_date),
                                 (rec.ks_date_filter_field.name, "<=", selected_end_date)]
            else:
                proper_domain = []
        return proper_domain


    @api.multi
    @api.onchange('ks_dashboard_item_type')
    def set_color_palette(self):
        for rec in self:
            if rec.ks_dashboard_item_type == "ks_bar_chart" or rec.ks_dashboard_item_type == "ks_line_chart" or rec.ks_dashboard_item_type == "ks_area_chart":
                rec.ks_chart_item_color = "cool"
            else:
                rec.ks_chart_item_color = "default"