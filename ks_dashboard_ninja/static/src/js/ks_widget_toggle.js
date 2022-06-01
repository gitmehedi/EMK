odoo.define('ks_dashboard_ninja_list.ks_widget_toggle', function (require) {
    "use strict";

       var core = require('web.core');
    var common = require('web.form_common');


    var QWeb = core.qweb;


    var KsWidgetToggle = common.AbstractField.extend({

        //      To render preview item again on main page.
        start: function() {
            this.on('change:value',this.field_manager.fields.ks_preview,this.preview_change);
            this.on("change:effective_readonly", this, function(){ this.render_value()});
            return this._super();
        },

        preview_change : function(e){
            this.render_value();
        },

        events: _.extend({}, common.AbstractField.prototype.events, {
            'change .ks_toggle_icon_input': 'ks_toggle_icon_input_click',
        }),


        render_value: function () {
            var self = this,value = self.get_value();
            self.$el.empty();


            var $view = $(QWeb.render('ks_widget_toggle'));
            if(value){
                $view.find("input[value='"+value+"']").prop("checked", true);
            }
            this.$el.append($view)

            if (self.get('effective_readonly')) {
                this.$el.find('.ks_select_dashboard_item_toggle').addClass('ks_not_click');
            }
        },


        ks_toggle_icon_input_click : function(e){
            var self = this;
            self.set_value(e.currentTarget.value);
        }



    });
    core.form_widget_registry.add('ks_widget_toggle', KsWidgetToggle);

    return {
        KsWidgetToggle: KsWidgetToggle
    };

});

