//-*- coding: utf-8 -*-
//############################################################################
//
//   OpenERP, Open Source Management Solution
//   This module copyright (C) 2015 Therp BV <http://therp.nl>.
//
//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU Affero General Public License as
//   published by the Free Software Foundation, either version 3 of the
//   License, or (at your option) any later version.
//
//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU Affero General Public License for more details.
//
//   You should have received a copy of the GNU Affero General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//############################################################################

openerp.web_widget_x2many_2d_checkbox = function(instance)
{
    instance.web.form.widgets.add(
        'x2many_2d_matrix_checkbox',
        'instance.web_widget_x2many_2d_checkbox.FieldX2Many2dCheckBox');
    instance.web_widget_x2many_2d_checkbox.FieldX2Many2dCheckBox = instance.web.form.FieldOne2Many.extend({
        template: 'FieldX2Many2dCheckBox',
        widget_class: 'oe_form_field_x2many_2d_matrix',

        // those will be filled with rows from the dataset
        by_x_axis: {},
        by_y_axis: {},
        field_x_axis: 'x',
        field_label_x_axis: 'x',
        field_y_axis: 'y',
        field_label_y_axis: 'y',
        field_value: 'value',
       
        // this will be filled with the model's fields_get
        fields: {},

        // read parameters
        init: function(field_manager, node)
        {
            this.field_x_axis = node.attrs.field_x_axis || this.field_x_axis;
            this.field_y_axis = node.attrs.field_y_axis || this.field_y_axis;
            this.field_label_x_axis = node.attrs.field_label_x_axis || this.field_x_axis;
            this.field_label_y_axis = node.attrs.field_label_y_axis || this.field_y_axis;
            this.field_value = node.attrs.field_value || this.field_value;
           
            return this._super.apply(this, arguments);
        },

        // return a field's value, id in case it's a one2many field
        get_field_value: function(row, field, many2one_as_name)
        {
        	if(this.fields[field].type == 'many2one' && _.isArray(row[field]))
            {
                if(many2one_as_name)
                {
                    return row[field][1];
                }
                else
                {
                    return row[field][0];
                }
            }
            return row[field];
        },
        
        // setup our datastructure for simple access in the template
        set_value: function()
        {
            var self = this,
                result = this._super.apply(this, arguments);

            self.by_x_axis = {};
            self.by_y_axis = {};
                
            return jQuery.when(result).then(function()
            {
                return self.dataset._model.call('fields_get').then(function(fields)
                {
                    self.fields = fields;

                }).then(function()
                {
                    return self.dataset.read_ids(self.dataset.ids).then(function(rows)
                    {
                        var read_many2one = {},
                            many2one_fields = [
                                self.field_x_axis, self.field_y_axis,
                                self.field_label_x_axis, self.field_label_y_axis
                            ];
                        // prepare to read many2one names if necessary (we can get (id, name) or just id as value)
                        _.each(many2one_fields, function(field)
                        {
                            if(self.fields[field].type == 'many2one')
                            {
                                read_many2one[field] = {};
                            }
                        });
                        // setup data structure
                        _.each(rows, function(row)
                        {
                            self.add_xy_row(row);
                            _.each(read_many2one, function(rows, field)
                            {
                                if(!_.isArray(row[field]))
                                {
                                    rows[row[field]] = rows[row[field]] || []
                                    rows[row[field]].push(row);
                                }
                            });
                        });
                        // read many2one fields if necessary
                        var deferrends = [];
                        _.each(read_many2one, function(rows, field)
                        {
                            if(_.isEmpty(rows))
                            {
                                return;
                            }
                            var model = new instance.web.Model(self.fields[field].relation);
                            deferrends.push(model.call(
                                'name_get',
                                [_.map(_.keys(rows), function(key) {return parseInt(key)})])
                                .then(function(names)
                                {
                                    _.each(names, function(name)
                                    {
                                        _.each(rows[name[0]], function(row)
                                        {
                                            row[field] = name;
                                        });
                                    });
                                }));
                        })
                        if(self.is_started && !self.no_rerender)
                        {
                        	self.renderElement();
                            self.$el.find('.edit').on(
                                    'change', self.proxy(self.xy_value_change));
                            self.effective_readonly_change();
                        }
                        return jQuery.when.apply(jQuery, deferrends);
                    });
                });
            });
        },

        // to whatever needed to setup internal data structure
        add_xy_row: function(row)
        {
            var x = this.get_field_value(row, this.field_x_axis),
                y = this.get_field_value(row, this.field_y_axis);
            this.by_x_axis[x] = this.by_x_axis[x] || {};
            this.by_y_axis[y] = this.by_y_axis[y] || {};
            this.by_x_axis[x][y] = row;
            this.by_y_axis[y][x] = row;
        },

        // get x axis values in the correct order
        get_x_axis_values: function()
        {
            return _.keys(this.by_x_axis);
        },

        // get y axis values in the correct order
        get_y_axis_values: function()
        {
            return _.keys(this.by_y_axis);
        },

        // get the label for a value on the x axis
        get_x_axis_label: function(x)
        {
        	return this.get_field_value(
                _.first(_.values(this.by_x_axis[x])),
                this.field_label_x_axis, true);
        },

        // get the label for a value on the y axis
        get_y_axis_label: function(y)
        {
            return this.get_field_value(
                _.first(_.values(this.by_y_axis[y])),
                this.field_label_y_axis, true);
        },

        // return the class(es) the inputs should have
        get_xy_value_class: function()
        {
            var classes = 'oe_form_field oe_form_required';
            classes+=' oe_form_field_boolean';
            return classes;
        },

        // return row id of a coordinate
        get_xy_id: function(x, y)
        {
            return this.by_x_axis[x][y]['id'];
        },

        // return the value of a coordinate
        get_xy_value: function(x, y)
        {
            return this.get_field_value(
                this.by_x_axis[x][y], this.field_value);
        },

        // validate a value
        validate_xy_value: function(val)
        {
            try
            {
                this.parse_xy_value(val);
            }
            catch(e)
            {
                return false;
            }
            return true;
        },

        // parse a value from user input
        parse_xy_value: function(val)
        {
            return instance.web.parse_value(
                val, {'type': this.fields[this.field_value].type});
        },

        

        start: function()
        {
            var self = this;
            this.$el.find('.edit').on(
                'change', self.proxy(this.xy_value_change));
            this.on("change:effective_readonly",
                    this, this.proxy(this.effective_readonly_change));
            this.effective_readonly_change();
            return this._super.apply(this, arguments);
        },

        xy_value_change: function(e)
        {
            var $this = jQuery(e.currentTarget),
                val = $this.is(':checked');
        	
            if(this.validate_xy_value(val))
            {
                var data = {}, value = this.parse_xy_value(val);
                data[this.field_value] = value;
                
                $this.siblings('.read').text(value);
                $this.attr('checked', value);
                $this.val(value);

                this.dataset.write($this.data('id'), data);
                $this.parent().removeClass('oe_form_invalid');
            }
            else
            {
                $this.parent().addClass('oe_form_invalid');
            }

        },

        effective_readonly_change: function()
        {
            this.$el
            .find('tbody td.oe_list_field_cell span.oe_form_field .edit')
            .toggle(!this.get('effective_readonly'));
            this.$el
            .find('tbody td.oe_list_field_cell span.oe_form_field .read')
            .toggle(this.get('effective_readonly'));
            this.$el.find('.edit').first().focus();
        },

        is_syntax_valid: function()
        {
            return this.$el.find('.oe_form_invalid').length == 0;
        },

        // deactivate view related functions
        load_views: function() {},
        reload_current_view: function() {},
        get_active_view: function() {},
    });
}
