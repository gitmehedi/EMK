odoo.define('web_dynamic_dashboard.web_widget_colorpicker', function(require) {
    "use strict";

    var core = require('web.core');
    var widget = require('web.form_widgets');

    var FieldColorPicker = widget.FieldChar.extend({

        template: 'FieldColorPicker',
        widget_class: 'oe_form_field_color',

        store_dom_value: function() {
            if (!this.silent) {
                if (!this.get('effective_readonly') &&
                    this.$input.val() !== '') {
                    this.set_value(this.$input.val());
                }
            }
        },

        render_value: function () {
            if (!this.get("effective_readonly")) {
                var show_value = this.get('value');
                var $input = this.$el.find('input');
                $input.val(show_value);
                this.$el.colorpicker({format: 'rgba'});
                this.$input = $input;
            } else {
                var show_value = this.get('value');
                var $input = this.$el.find('input');
                $input.val(show_value || '');
                this.$el.colorpicker({format: 'rgba'});
                $input.attr('readonly', true);
            }
        }

    });

    core.form_widget_registry
    .add('colorpicker', FieldColorPicker);

    return {
        FieldColorPicker: FieldColorPicker
    };
});

odoo.define('web_dynamic_dashboard.web_widget_iconpicker', function(require) {
    "use strict";

    var core = require('web.core');
    var FieldChar = core.form_widget_registry.get('char');

    var FieldIconPicker = FieldChar.extend({

        template: 'FieldIconPicker',
        widget_class: 'oe_form_field_icon',

        store_dom_value: function() {
            if (!this.silent) {
                if (!this.get('effective_readonly') &&
                    this.$input.val() !== '') {
                    this.set_value(this.$input.val());
                }
            }
        },

        render_value: function () {
            if (!this.get("effective_readonly")) {
                var self = this;
                var show_value = this.get('value');
                var $input = this.$el.find('input');
                $input.val(show_value);
                setTimeout(function() {
                    $input.iconpicker();
                    $input.on('iconpickerSelected', function(event){
                        self.set_value($input.val());
                    });
                }, 300);
                this.$input = $input;
            } else {
                var show_value = this.get('value');
                this.$el.text(show_value || '');
            }
        }

    });

    core.form_widget_registry
    .add('iconpicker', FieldIconPicker);

    return {
        FieldIconPicker: FieldIconPicker
    };
});

