odoo.define('ks_dashboard_ninja_pro_list.ks_dashboard_list_view_preview', function (require) {
    "use strict";


    var common = require('web.form_common');
    var core = require('web.core');

    var QWeb = core.qweb;

    var KsListViewPreview = common.AbstractField.extend({




        start : function(){
         this.field_manager.fields.ks_dashboard_item_type.on('change',this.field_manager.fields.ks_list_view_preview,this.preview_update);
            this.field_manager.fields.ks_chart_data_count_type.on('change',this.field_manager.fields.ks_list_view_preview,this.preview_update);
            this.field_manager.fields.ks_list_view_data.on('change',this.field_manager.fields.ks_list_view_preview,this.preview_update);
            this.field_manager.fields.ks_list_view_fields.on('change',this.field_manager.fields.ks_list_view_preview,this.preview_update);
            return this._super();
        },

        preview_update : function(){
            this.render_value();
        },

        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.state = {};
        },

        render_value: function () {
            this.$el.empty()
            var fields = this.view.get_fields_values();
            if (fields.ks_dashboard_item_type === 'ks_list_view') {
                if (fields.ks_list_view_fields.length !== 0) {
                    this.ksRenderListView()
                } else {
                    this.$el.append($('<div>').text("Select Fields to show in list view."));

                }
            }
        },

        ksRenderListView: function () {
            var field = this.view.get_fields_values();
            var ks_list_view_name;
            if (field.name) ks_list_view_name = field.name;
            else if (field.ks_model_name) ks_list_view_name = this.field_manager.fields.ks_model_id.current_display;
            else ks_list_view_name = "Name";

            var list_view_data;
            if (field.ks_list_view_data) list_view_data = JSON.parse(field.ks_list_view_data);
            else list_view_data = false;

            var $listViewContainer = $(QWeb.render('ks_list_view_container', {
                ks_list_view_name: ks_list_view_name,
                list_view_data: list_view_data
            }));
            this.$el.append($listViewContainer);

        },

    });
    core.form_widget_registry.add('ks_dashboard_list_view_preview', KsListViewPreview);

    return {
        KsListViewPreview: KsListViewPreview,
    };

});