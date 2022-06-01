odoo.define('ks_dashboard_ninja.ks_dashboard', function (require) {
    "use strict";

    var core = require('web.core');
    var config = require('web.config');
    var Dialog = require('web.Dialog');
    var Model = require('web.DataModel');
    var ajax = require('web.ajax');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var QWeb = core.qweb;
    var _t = core._t;
    var Widget = require('web.Widget');

    //Dashboard filter imports
    var ks_options_status=true;
    var formats = require('web.formats')
    var time = require('web.time');
    var ks_start_date,ks_end_date;

    // Export Chart import
    var crash_manager = require('web.crash_manager');
    var framework = require('web.framework');

    var MAX_LEGEND_LENGTH = 25 * (Math.max(1, config.device.size_class));

    var KsDashBoardNinja = Widget.extend(ControlPanelMixin, {

        need_control_panel : false,
       events: {
            'click #ks_add_item_selection>li': '_onKsAdditemTypeClick',
            'click .ks_dashboard_add_layout': '_onKsAddLayoutClick',
            'click .ks_dashboard_edit_layout': '_onKsEditLayoutClick',
            'click .ks_dashboard_save_layout': '_onKsSaveLayoutClick',
            'click .ks_dashboard_cancel_layout': '_onKsCancelLayoutClick',
            'click .ks_item_click': '_onKsItemClick',
            'click .ks_dashboard_item_customize': '_onKsItemCustomizeClick',
            'click .ks_dashboard_item_delete': '_onKsDeleteItemClick',
            'change .ks_dashboard_header_name': '_onKsInputChange',
            'click .ks_duplicate_item': 'onKsDuplicateItemClick',
            'show.bs.dropdown .ks_dashboard_item_button_container': 'onKsDashboardMenuContainerShow',
            'hide.bs.dropdown .ks_dashboard_item_button_container': 'onKsDashboardMenuContainerHide',
            'click .ks_dashboard_menu_container': function(e){e.stopPropagation();},
            'click .ks_move_item': 'onKsMoveItemClick',
            'click .ks-options-btn': '_onksOptionsClick',
            'click .print-dashboard-btn': '_onKsDashboardPrint',
            'click .apply-dashboard-date-filter': '_onKsApplyDateFilter',
            'click .clear-dashboard-date-filter': '_onKsClearDateValues',
            'click .ks_dashbaord_ninja_toggle_menu': '_onKsToggleMenu',
            'change #ksstartdatepicker': '_ksShowApplyClearDateButton',
            'change #ksenddatepicker': '_ksShowApplyClearDateButton',
            'click .ks_date_filters_menu': '_ksOnDateFilterMenuSelect',
            'click .ks_dashboard_item_action': 'ksStopClickPropagation',
            'click #ks_item_info': 'ksOpenItemFormView',
            'click .ks_chart_color_options': 'ksRenderChartColorOptions',
            // Chart Export events
            'click .chart_xls_export': 'ksChartExportXLS',
            'click .chart_pdf_export': 'ksChartExportPdf',
            // ON chart click Events
            'click .ks_dashboard_item_chart_info': 'onKsChartMoreInfoClick',
            'click #ks_chart_canvas_id': 'onKsChartCanvasClick',
       },
        init: function (parent,state, params) {
            this._super.apply(this, arguments);
            this.form_template = 'ks_dashboard_ninja_template_view';

            this.ksIsDashboardManager = false;
            this.ksDashboardEditMode = false;
            this.ksCurrentDashboardModel = new Model('ks_dashboard_ninja.board');
            this.ks_dashboard_item_model = new Model('ks_dashboard_ninja.item');


            this.ksCurrentDashboard = false;
            this.ksNewDashboardName = false;
            this.file_type_magic_word = {
                '/': 'jpg',
                'R': 'gif',
                'i': 'png',
                'P': 'svg+xml',
            };
            var l10n = _t.database.parameters;
            this.form_template = 'ks_dashboard_ninja_template_view';
            this.date_format = time.strftime_to_moment_format(_t.database.parameters.date_format)
            this.date_format = this.date_format.replace(/\bYY\b/g,"YYYY");
            this.datetime_format = time.strftime_to_moment_format((_t.database.parameters.date_format + ' ' + l10n.time_format))
            this.is_dateFilter_rendered = false;
            this.ks_date_filter_data;

            this.ks_date_filter_selections = {
                'l_none':{'days': false,'text':'Date Filter'},
                'l_day':{'days': 1,'text':'Today'},
                'l_week':{'days': 7,'text':'Last 7 days'},
                'l_month':{'days': 30,'text':'Last 30 days'},
                'l_quarter':{'days': 90,'text':'Last 90 days'},
                'l_year':{'days': 365,'text':'Last 365 days'},
                'l_custom':{'days':'custom_filter','text':'Custom'}
            };
            // To make sure date filter show date in specific order.
            this.ks_date_filter_selection_order = ['l_day','l_week','l_month','l_quarter','l_year','l_custom'];
            this.ks_dashboard_id = state.params.ks_dashboard_id;
            this.gridstack_options = {
                                        staticGrid:true,
                                        float:false
                                     };
            this.gridstackConfig = {};
            this.grid = false;
            this.chartMeasure = {};
            this.chart_container = {}
            this.ksChartColorOptions = ['default', 'cool', 'warm', 'neon']

            this.state_params = params.additional_context.params;
        },

        ksStopClickPropagation : function(e){
            this.ksAllowItemClick = false;
        },

       willStart: function() {
            var self = this;
            if (!window.ace && !this.loadJS_def) {
                this.loadJS_def = ajax.loadJS('/ks_dashboard_ninja/static/lib/js/html2canvas.js').then(function () {
                    return $.when(ajax.loadJS('/ks_dashboard_ninja/static/lib/js/jquery.ui.touch-punch.min.js'),
                        );

                });
            }
            return $.when(this._super(), this.loadJS_def).then(function(){
                return $.when(self.ks_fetch_data());
                });
       },

        start: function () {
            var self = this;

            self.set({ 'title':self.ks_dashboard_data.name});
            this.$el.css("background-color","#f9f9f9");
            this._super.apply(this, arguments);
        },


        on_attach_callback: function () {
            var self = this;
            self.ksRenderDashboard();
            $('.o_content').addClass('ks_bg_color');
            self.ks_set_update_interval();
        },


        ks_set_update_interval : function(){
            var self = this;
            if (self.ks_dashboard_data.ks_set_interval){
                function ksUpdateInterval() {
                    $.when(self.ks_fetch_data()).then(function () {
                        if(self.ks_dashboard_data.ks_item_data){
                            self.ksRenderDashboardItems();
                        }
                    });
                }
                self.ksUpdateDashboard = setInterval(ksUpdateInterval, self.ks_dashboard_data.ks_set_interval);
            }
        },

        ks_remove_update_interval : function(){
            var self = this;
            if (self.ks_dashboard_data.ks_set_interval){
                clearInterval(self.ksUpdateDashboard)
            }
        },

        onKsDashboardMenuContainerShow: function (e) {
            $(e.currentTarget).addClass('ks_dashboard_item_menu_show');
            this.ks_remove_update_interval();
             //            Dynamic Bootstrap menu populate Image Report
            if($(e.target).hasClass('ks_dashboard_more_action')){
                var chart_id = e.target.dataset.itemId;
                var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
                var base64_image = this.chart_container[chart_id].toBase64Image();
                $(e.target).find('.dropdown-menu').empty();
                $(e.target).find('.dropdown-menu').append($(QWeb.render('ksMoreChartOptions', {
                href: base64_image, download_fileName:name,chart_id:chart_id })))
            }
        },

        onKsDashboardMenuContainerHide: function (e) {
            $(e.currentTarget).removeClass('ks_dashboard_item_menu_show');
            this.ks_set_update_interval();
        },

        on_detach_callback : function(){
            var self = this;
            $('.o_content').removeClass('ks_bg_color');
            self.ks_remove_update_interval();
        },

        ks_set_default_chart_view: function () {
            Chart.plugins.register({
                afterDraw: function (chart) {
                    if (chart.data.labels.length === 0) {
                        // No data is present
                        var ctx = chart.chart.ctx;
                        var width = chart.chart.width;
                        var height = chart.chart.height
                        chart.clear();

                        ctx.save();
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.font = "3rem 'Lucida Grande'";
                        ctx.fillText('No data available', width / 2, height / 2);
                        ctx.restore();
                    }
                }
            });
        },

        _onKsSaveLayoutClick: function () {
            var self = this;

            if(self.grid && self.ks_item_data){
               self._ksSaveCurrentLayout();
            }
//        Have  to save dashboard here
            var dashboard_title = $('#ks_dashboard_title_input').val();
            if (self.ks_dashboard_data.name != false && self.ks_dashboard_data.name.length != 0 && dashboard_title !== self.ks_dashboard_data.name) {
                self.ksCurrentDashboardModel.call('ks_save_dashboard_name', [dashboard_title, self.ks_dashboard_id]);
                self.ksCurrentDashboard =dashboard_title;
                self.ks_dashboard_data.name = dashboard_title;
            }
            if(self.ks_dashboard_data.ks_item_data){self._ksSaveCurrentLayout();}
            self._ksToggleEditMode()
        },

        _onKsCancelLayoutClick: function () {
            var self = this;
//        render page again
            this.ksDashboardEditMode = false;
            $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
        },

        _onKsInputChange: function (e) {
            this.ksNewDashboardName = e.target.value
        },

        _ksToggleEditMode: function () {
            var self = this
            if (self.ksDashboardEditMode) {
                self._ksRenderActiveMode()
                self.ksDashboardEditMode = false
            }
            else if (!self.ksDashboardEditMode) {
                self._ksRenderEditMode()
                self.ksDashboardEditMode = true
            }

        },

        _ksRenderActiveMode: function () {
           var self = this

            if (self.grid && self.ks_dashboard_data.ks_item_data) {
                $('.grid-stack').data('gridstack').disable();
            }

            $('#ks_dashboard_title_label').text(self.ks_dashboard_data.name);

            $('.ks_am_element').removeClass("ks_hide");
            $('.ks_em_element').addClass("ks_hide");
            if (self.ks_dashboard_data.ks_item_data) $('.ks_am_content_element').removeClass("ks_hide");

            self.$el.find('.ks_item_not_click').addClass('ks_item_click').removeClass('ks_item_not_click')
            self.$el.find('.ks_dashboard_item').addClass('ks_dashboard_item_header_hover')
            self.$el.find('.ks_dashboard_item_header').addClass('ks_dashboard_item_header_hover')

            self.$el.find('.ks_dashboard_item_l2').addClass('ks_dashboard_item_header_hover')
            self.$el.find('.ks_dashboard_item_header_l2').addClass('ks_dashboard_item_header_hover')

            //      For layout 5
            self.$el.find('.ks_dashboard_item_l5').addClass('ks_dashboard_item_header_hover')


            self.$el.find('.ks_dashboard_item_button_container').addClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_top_settings').removeClass("ks_hide")
            self.$el.find('.ks_dashboard_edit_mode_settings').addClass("ks_hide")

            self.$el.find('.ks_chart_container').removeClass('ks_item_not_click ks_item_click');
            self.ks_set_update_interval();
        },

        _ks_get_rgba_format: function (val) {
            var rgba = val.split(',')[0].match(/[A-Za-z0-9]{2}/g);
            rgba = rgba.map(function (v) {
                return parseInt(v, 16)
            }).join(",");
            return "rgba(" + rgba + "," + val.split(',')[1] + ")";
        },

        ksNumFormatter: function (num, digits) {
            var si = [{
                    value: 1,
                    symbol: ""
                },
                {
                    value: 1E3,
                    symbol: "k"
                },
                {
                    value: 1E6,
                    symbol: "M"
                },
                {
                    value: 1E9,
                    symbol: "G"
                },
                {
                    value: 1E12,
                    symbol: "T"
                },
                {
                    value: 1E15,
                    symbol: "P"
                },
                {
                    value: 1E18,
                    symbol: "E"
                }
            ];
            var rx = /\.0+$|(\.[0-9]*[1-9])0+$/;
            var i;
            for (i = si.length - 1; i > 0; i--) {
                if (num >= si[i].value) {
                    break;
                }
            }
            return (num / si[i].value).toFixed(digits).replace(rx, "$1") + si[i].symbol;
        },


        ks_get_dark_color : function(color,opacity, percent) {
            var num = parseInt(color.slice(1),16), amt = Math.round(2.55 * percent), R = (num >> 16) + amt, G = (num >> 8 & 0x00FF) + amt, B = (num & 0x0000FF) + amt;
            return "#" + (0x1000000 + (R<255?R<1?0:R:255)*0x10000 + (G<255?G<1?0:G:255)*0x100 + (B<255?B<1?0:B:255)).toString(16).slice(1) + "," + opacity;
        },

        _ksRenderEditMode: function () {
            var self = this;
            self.ks_remove_update_interval();
            $('#ks_dashboard_title_input').val(self.ks_dashboard_data.name);

            $('.ks_am_element').addClass("ks_hide");
            $('.ks_em_element').removeClass("ks_hide");

            self.$el.find('.ks_item_click').addClass('ks_item_not_click').removeClass('ks_item_click');
            self.$el.find('.ks_dashboard_item').removeClass('ks_dashboard_item_header_hover');
            self.$el.find('.ks_dashboard_item_header').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_l2').removeClass('ks_dashboard_item_header_hover');
            self.$el.find('.ks_dashboard_item_header_l2').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_l5').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_item_button_container').removeClass('ks_dashboard_item_header_hover');

            self.$el.find('.ks_dashboard_link').addClass("ks_hide")
            self.$el.find('.ks_dashboard_top_settings').addClass("ks_hide")
            self.$el.find('.ks_dashboard_edit_mode_settings').removeClass("ks_hide")

            // Adding Chart grab able cals
            self.$el.find('.ks_chart_container').addClass('ks_item_not_click');
            self.$el.find('.ks_list_view_container').addClass('ks_item_not_click');

            if (self.grid) {
                self.grid.enable();
            }
        },

        ks_fetch_data: function () {
            var self = this;
            return self.ksCurrentDashboardModel.call('ks_fetch_dashboard_data', [self.ks_dashboard_id]).done(function(result){
                self.ks_dashboard_data = result;
            });
        },

        //This function adding the item into gridstack container
        ksRenderDashboardItems: function () {
            var self = this;
            self.$el.find('.print-dashboard-btn').addClass("ks_pro_print_hide");

            var items = Object.values(self.ks_dashboard_data.ks_item_data);
            if (self.ks_dashboard_data.ks_gridstack_config) {
                self.gridstackConfig = JSON.parse(self.ks_dashboard_data.ks_gridstack_config);
            }
            $('.ks_grid-stack').remove();
            var $divItem = $("<div>").addClass("grid-stack ks_grid-stack").attr('data-gs-width','35');
            $divItem.appendTo(self.$el)
            $('.grid-stack').gridstack(self.gridstack_options);

            // In gridstack version 0.3 we have to make static after adding element in dom
            self.grid = $divItem.data('gridstack');
            var item_view;
            var ks_container_class = 'grid-stack-item', ks_inner_container_class = 'grid-stack-item-content';
            for (var i = 0; i < items.length; i++) {
                if(self.grid){

                    if(items[i].ks_dashboard_item_type==='ks_tile'){
                        item_view = self._ksRenderDashboardTile(items[i],ks_container_class,ks_inner_container_class)
                        if(items[i].id in self.gridstackConfig){
                            self.grid.addWidget($(item_view), self.gridstackConfig[items[i].id].x, self.gridstackConfig[items[i].id].y, self.gridstackConfig[items[i].id].width, self.gridstackConfig[items[i].id].height, false, 11, null, 2, 2, items[i].id);
                        }
                        else{
                           self.grid.addWidget($(item_view), 0, 0, 11, 2, true, 11, null, 2, 2, items[i].id);
                        }
                    }else if (items[i].ks_dashboard_item_type === 'ks_list_view') {
                        self._renderListView(items[i], self.grid)
                        }
                    else{
                        self._renderGraph(items[i],self.grid)
                    }
                }
            }
            self.grid.setStatic(true);
        },

        _ksRenderDashboardTile: function (tile,ks_container_class,ks_inner_container_class){
            var self = this;
            var ks_icon_url, item_view;
            var ks_rgba_background_color, ks_rgba_font_color, ks_rgba_default_icon_color;
            var style_main_body, style_image_body_l2, style_domain_count_body, style_button_customize_body,
                style_button_delete_body;

            var data_count = self.ksNumFormatter(tile.count, 1);
                if(tile.ks_icon_select=="Custom"){
                    if(tile.icon[0]){
                    ks_icon_url = 'data:image/' + (self.file_type_magic_word[tile.icon[0]] || 'png') + ';base64,' + tile.icon;
                    }
                    else{
                        ks_icon_url = false;
                    }
                }

                tile.ksIsDashboardManager = self.ks_dashboard_data.ks_dashboard_manager;
                ks_rgba_background_color = self._ks_get_rgba_format(tile.color);
                ks_rgba_font_color = self._ks_get_rgba_format(tile.font_color);
                ks_rgba_default_icon_color = self._ks_get_rgba_format(tile.ks_default_icon_color);
                style_main_body = "background-color:" + ks_rgba_background_color + ";color : " + ks_rgba_font_color + ";";
                switch (tile.layout) {
                    case 'layout1':
                        item_view = QWeb.render('ks_dashboard_item_layout1', {
                            item: tile,
                            style_main_body: style_main_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;

                    case 'layout2':
                        var ks_rgba_dark_background_color_l2 = self._ks_get_rgba_format(self.ks_get_dark_color(tile.color.split(',')[0],tile.color.split(',')[1],-10));
                        style_image_body_l2 = "background-color:" + ks_rgba_dark_background_color_l2 + ";";
                        item_view = QWeb.render('ks_dashboard_item_layout2', {
                            item: tile,
                            style_image_body_l2: style_image_body_l2,
                            style_main_body: style_main_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;

                    case 'layout3':
                        item_view = QWeb.render('ks_dashboard_item_layout3', {
                            item: tile,
                            style_main_body: style_main_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;

                    case 'layout4':
                        style_main_body = "color : " + ks_rgba_font_color + ";border : solid;border-width : 1px;border-color:" + ks_rgba_background_color + "; background-color:white;"
                        style_image_body_l2 = "background-color:" + ks_rgba_background_color + ";";
                        style_domain_count_body = "color:" + ks_rgba_background_color + ";";
                        style_button_customize_body = "color:" + ks_rgba_background_color + ";";
                        style_button_delete_body = "color:" + ks_rgba_background_color + ";";
                        item_view = QWeb.render('ks_dashboard_item_layout4', {
                            item: tile,
                            style_main_body: style_main_body,
                            style_image_body_l2: style_image_body_l2,
                            style_domain_count_body: style_domain_count_body,
                            style_button_customize_body: style_button_customize_body,
                            style_button_delete_body: style_button_delete_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;

                    case 'layout5':
                        item_view = QWeb.render('ks_dashboard_item_layout5', {
                            item: tile,
                            style_main_body: style_main_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;

                    case 'layout6':
                   ks_rgba_default_icon_color = self._ks_get_rgba_format(tile.ks_default_icon_color);
                        item_view = QWeb.render('ks_dashboard_item_layout6', {
                            item: tile,
                            style_image_body_l2: style_image_body_l2,
                            style_main_body: style_main_body,
                            ks_icon_url: ks_icon_url,
                            ks_rgba_default_icon_color: ks_rgba_default_icon_color,
                            ks_container_class : ks_container_class,
                            ks_inner_container_class : ks_inner_container_class,
                            ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                        data_count: data_count
                        });
                        break;


                    default :$('#ks_date_filter_selection').text(self.ks_date_filter_selections[date_filter_selected]["text"])
                        item_view = QWeb.render('ks_dashboard_item_layout_default', {item: tile});
                        break;
                }
                return item_view;
        },

        no_result: function () {
            $(".ks_date_apply_clear_print").hide();
            $('.ks_date_filter_selection_input').hide();
                this.$el.append(
                    $('<div class="oe_view_nocontent ks_dashboard_nocontent ks_view_nocontent">')
                        .append($(QWeb.render('ks_no_content_default_view'))));
        },

        // this fuction is main ENTRY POINT
        ksRenderDashboard: function () {
            var self = this;
            self.$el.empty();
            self.$el.addClass('ks_dashboard_ninja d-flex flex-column');

            var $ks_header = $(QWeb.render('ksDashboardNinjaHeader', {
                ks_dashboard_name: self.ks_dashboard_data.name,
                ks_dashboard_manager: self.ks_dashboard_data.ks_dashboard_manager,
                date_selection_data: self.ks_date_filter_selections,
                date_selection_order: self.ks_date_filter_selection_order
            }));
            self.$el.append($ks_header);
            self.ksRenderDashboardMainContent();
        },

         ksRenderDashboardMainContent: function () {
            var self = this;
            if (self.ks_dashboard_data.ks_item_data) {
                self._renderDateFilterHeader();
                self.$el.find('.ks_dashboard_link').removeClass("ks_hide");
                self.ksRenderDashboardItems();
            } else if (!self.ks_dashboard_data.ks_item_data) {
                self.no_result();
            }
        },

        _onKsEditLayoutClick: function () {
            var self = this;
            self._ksToggleEditMode();
        },

        _onKsAddLayoutClick: function () {
            var self = this;

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'ks_dashboard_ninja.item',
                view_id: 'ks_dashboard_ninja_list_form_view',
                views: [[false, 'form']],
                target: 'current',
                context: {'ks_dashboard_id': self.ks_dashboard_id},
            },{
                on_reverse_breadcrumb : this.on_reverse_breadcrumb,
            });
        },

        on_reverse_breadcrumb : function(state){
            if (this.getParent() && this.getParent().do_push_state) {
            this.getParent().do_push_state({});
            this.do_action("reload");
            }
        },

        _onKsItemClick: function (e) {
            var self = this;

            if(self.ksAllowItemClick){
                e.preventDefault();
                if (e.target.title != "Customize Item") {
                    var id = e.currentTarget.firstElementChild.id
                    self.ksCurrentDashboardModel.call('ks_get_my_dashboard_item_view',[id]
                    ).then(function (data) {
                        if(data.domain_model){
                            self.do_action({
                                name: _t('Selected records'),
                                type: 'ir.actions.act_window',
                                res_model: data.domain_model,
                                domain: data.domain_value || "[]",
                                views: [[false, 'list'], [false, 'form']],
                                view_mode: 'list',
                                target: 'current',
                            },{
                                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                            });
                        }
                        else{
                            alert("No module defined for current dashboard item.")
                        }
                    })
                }
            }
            else{
                self.ksAllowItemClick = true;
            }
        },

        //Sens user to dashboard item edit form view
        _onKsItemCustomizeClick: function (e) {
            var self = this;
            var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'))

            self.do_action({
                type: 'ir.actions.act_window',
                res_model: 'ks_dashboard_ninja.item',
                view_id: 'ks_dashboard_ninja_list_form_view',
                views: [[false, 'form']],
                target: 'current',
                res_id: id
            },{
                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
            });
            e.stopPropagation();
        },

        _renderGraph: function (item, grid) {
            var self = this;
            var chart_data = JSON.parse(item.ks_chart_data);
            var chart_id = item.id,
                chart_title = item.name;
            var chart_title = item.name;
            var chart_type = item.ks_dashboard_item_type.split('_')[1];
            switch (chart_type) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var chart_family = "circle";
                    break;
                case "bar":
                case "line":
                case "area":
                    var chart_family = "square"
                    break;
                default:
                    var chart_family = "none";
                    break;
            }

            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_container', {
                ks_chart_title: chart_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list,
                chart_id: chart_id,
                chart_family: chart_family,
                chart_type: chart_type,
                ksChartColorOptions: this.ksChartColorOptions
            })).addClass('ks_dashboarditem_id');
            $ks_gridstack_container.find('.ks_li_' + item.ks_chart_item_color).addClass('ks_date_filter_selected');
            var $ksChartContainer = $('<canvas id="ks_chart_canvas_id"/>');
            $ks_gridstack_container.find('.card-body').append($ksChartContainer);


            if (chart_id in self.gridstackConfig) {
                grid.addWidget($ks_gridstack_container, self.gridstackConfig[chart_id].x, self.gridstackConfig[chart_id].y, self.gridstackConfig[chart_id].width, self.gridstackConfig[chart_id].height, false, 9, null, 3, null, chart_id);
            } else {
                grid.addWidget($ks_gridstack_container, 0, 0, 13, 4, true, 9, null, 3, null, chart_id);
            }

            if(chart_family === "circle"){
                if (chart_data['labels'].length > 30){
                    $ks_gridstack_container.find(".ks_dashboard_color_option").remove();
                    $ks_gridstack_container.find(".card-body").empty().append($("<div style='font-size:18px;'>Too many records for selected Chart Type. Consider using <strong>Domain</strong> to filter records or <strong>Record Limit</strong> to limit the no of records under <strong>30.</strong>"));
                    return ;
                }
            }
            var ksMyChart = new Chart($ksChartContainer[0], {
                type: chart_type === "area" ? "line" : chart_type,
                data: {
                    labels: chart_data['labels'],
                    groupByIds:chart_data['groupByIds'],
                    datasets: chart_data.datasets,
                },
                options: {
                    maintainAspectRatio: false,
                    responsiveAnimationDuration: 1000,
                    animation: {
                        easing: 'easeInQuad',
                    }
                }
            });

            this.chart_container[chart_id] = ksMyChart;
            self.ksChartColors(item.ks_chart_item_color, ksMyChart, chart_type, chart_family);
            ksMyChart.update();
        },

        ksChartColors: function (palette, ksMyChart, ksChartType, ksChartFamily) {
            var currentPalette = "cool";
            if (!palette) palette = currentPalette;
            currentPalette = palette;

            /*Gradients
              The keys are percentage and the values are the color in a rgba format.
              You can have as many "color stops" (%) as you like.
              0% and 100% is not optional.*/
            var gradient;
            switch (palette) {
                case 'cool':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [220, 237, 200, 1],
                        45: [66, 179, 213, 1],
                        65: [26, 39, 62, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'warm':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [254, 235, 101, 1],
                        45: [228, 82, 27, 1],
                        65: [77, 52, 47, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'neon':
                    gradient = {
                        0: [255, 255, 255, 1],
                        20: [255, 236, 179, 1],
                        45: [232, 82, 133, 1],
                        65: [106, 27, 154, 1],
                        100: [0, 0, 0, 1]
                    };
                    break;
                case 'default':
                    var color_set = ['#F04F65','#53cfce', '#f69032', '#fdc233', '#36a2ec', '#8a79fd', '#b1b5be', '#1c425c', '#8c2620', '#71ecef', '#0b4295', '#f2e6ce', '#1379e7']
            }

            //Find datasets and length
            var chartType = ksMyChart.config.type;

            switch (chartType) {
                case "pie":
                case "doughnut":
                case "polarArea":
                    var datasets = ksMyChart.config.data.datasets[0];
                    var setsCount = datasets.data.length;
                    break;
                case "bar":
                case "line":
                    var datasets = ksMyChart.config.data.datasets;
                    var setsCount = datasets.length;
                    break;
            }

            //Calculate colors
            var chartColors = [];

            if (palette !== "default") {
                //Get a sorted array of the gradient keys
                var gradientKeys = Object.keys(gradient);
                gradientKeys.sort(function (a, b) {
                    return +a - +b;
                });
                for (var i = 0; i < setsCount; i++) {
                    var gradientIndex = (i + 1) * (100 / (setsCount + 1)); //Find where to get a color from the gradient
                    for (var j = 0; j < gradientKeys.length; j++) {
                        var gradientKey = gradientKeys[j];
                        if (gradientIndex === +gradientKey) { //Exact match with a gradient key - just get that color
                            chartColors[i] = 'rgba(' + gradient[gradientKey].toString() + ')';
                            break;
                        } else if (gradientIndex < +gradientKey) { //It's somewhere between this gradient key and the previous
                            var prevKey = gradientKeys[j - 1];
                            var gradientPartIndex = (gradientIndex - prevKey) / (gradientKey - prevKey); //Calculate where
                            var color = [];
                            for (var k = 0; k < 4; k++) { //Loop through Red, Green, Blue and Alpha and calculate the correct color and opacity
                                color[k] = gradient[prevKey][k] - ((gradient[prevKey][k] - gradient[gradientKey][k]) * gradientPartIndex);
                                if (k < 3) color[k] = Math.round(color[k]);
                            }
                            chartColors[i] = 'rgba(' + color.toString() + ')';
                            break;
                        }
                    }
                }
            } else {
                for (var i = 0, counter = 0; i < setsCount; i++, counter++) {
                    if (counter >= color_set.length) counter = 0; // reset back to the beginning

                    chartColors.push(color_set[counter]);
                }

            }

            var datasets = ksMyChart.config.data.datasets;
            var options = ksMyChart.config.options;

            options.legend.labels.usePointStyle = true;
            if (ksChartFamily == "circle") {
                 options.legend.position = 'bottom';
                options.tooltips.callbacks = {
                                              title: function(tooltipItem, data) {
                                                          return data.datasets[tooltipItem[0].datasetIndex]['label']+" : "+data.datasets[tooltipItem[0].datasetIndex]['data'][tooltipItem[0].index];
                                                        },
                                               label : function(tooltipItem, data) {
                                                          return data.labels[tooltipItem.index];
                                                        },
                                                }
                for (var i = 0; i < datasets.length; i++) {
                    datasets[i].backgroundColor = chartColors;
                    datasets[i].borderColor = "rgba(255,255,255,1)";
                }
            } else if (ksChartFamily == "square") {
                options.scales.xAxes[0].gridLines.display = false;
                options.scales.yAxes[0].ticks.beginAtZero = true;
                for (var i = 0; i < datasets.length; i++) {
                    switch (ksChartType) {
                        case "bar":
                            datasets[i].backgroundColor = chartColors[i];
                            datasets[i].borderColor = "rgba(255,255,255,0)";
                            break;
                        case "line":
                            datasets[i].borderColor = chartColors[i];
                            datasets[i].backgroundColor = "rgba(255,255,255,0)";
                            break;
                        case "area":
                            datasets[i].borderColor = chartColors[i];
                            break;
                    }
                }
            }
            ksMyChart.update();
        },

        // for rendering the list view in Dashboard
         _renderListView: function (item, grid) {
            var self = this;
            var list_view_data = JSON.parse(item.ks_list_view_data);
            var item_id = item.id,
                item_title = item.name;

            var $ks_gridstack_container = $(QWeb.render('ks_gridstack_list_view_container', {
                ks_chart_title: item_title,
                ksIsDashboardManager: self.ks_dashboard_data.ks_dashboard_manager,
                ks_dashboard_list: self.ks_dashboard_data.ks_dashboard_list
            })).attr("id", item_id).addClass('ks_dashboarditem_id');
            var $ksItemContainer = $(QWeb.render('ks_list_view_table', {
                list_view_data: list_view_data
            }));
            $ks_gridstack_container.find('.card-body').append($ksItemContainer);

            if (item_id in self.gridstackConfig) {
                grid.addWidget($ks_gridstack_container, self.gridstackConfig[item_id].x, self.gridstackConfig[item_id].y, self.gridstackConfig[item_id].width, self.gridstackConfig[item_id].height, false, 9, null, 3, null, item_id);
            } else {
                grid.addWidget($ks_gridstack_container, 0, 0, 13, 4, true, 9, null, 3, null, item_id);
            }
        },

       //this will delete item from dashboard
        _onKsDeleteItemClick: function (e) {
            var self = this

            Dialog.confirm(this, (_t("Are you sure you want to remove this item?")), {
                confirm_callback: function () {
                    var id = parseInt($($(e.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'))
                    self.ksCurrentDashboardModel.call('ks_delete_dashboard_item',[id]
                            ).then(function (data) {
                            $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                              });
                            });
                        }
                });
            e.stopPropagation();
        },

        //This will save the current item position and their size.
        _ksSaveCurrentLayout: function () {
            var self = this;
            var items = $('.grid-stack').data('gridstack').grid.nodes;
            var grid_config = {}
            for (var i = 0; i < items.length; i++) {
                grid_config[items[i].id] = {'x':items[i].x,'y':items[i].y,'width':items[i].width,'height':items[i].height}
            }
            self.ksCurrentDashboardModel.call('write', [self.ks_dashboard_id, {
                "ks_gridstack_config": JSON.stringify(grid_config),
            }]);

            // Saving config here cause async call sometimes make changes ignore
            self.gridstackConfig = grid_config;
        },

        onKsDuplicateItemClick: function(e){
            var self = this;
            var ks_item_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".ks_dashboard_item_hover").slice(-1)[0]).find('.ks_dashboard_select option:selected').val();
            var dashboard_name = $($(e.target).parentsUntil(".ks_dashboard_item_hover").slice(-1)[0]).find('.ks_dashboard_select option:selected').text();
            self.ks_dashboard_item_model.call('copy',[parseInt(ks_item_id), {'ks_dashboard_ninja_board_id': parseInt(dashboard_id)}]
            ).then(function (result) {

                    self.do_notify(
                        _t("Item Duplicated"),
                        _t('Selected item is duplicated to '+dashboard_name+' .')
                    );
                    $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
             })
        },

        onKsMoveItemClick: function(e){
            var self = this;
            var ks_item_id = $($(e.target).parentsUntil(".ks_dashboarditem_id").slice(-1)[0]).parent().attr('id');
            var dashboard_id = $($(e.target).parentsUntil(".ks_dashboard_item_hover").slice(-1)[0]).find('.ks_dashboard_select option:selected').val();
            var dashboard_name = $($(e.target).parentsUntil(".ks_dashboard_item_hover").slice(-1)[0]).find('.ks_dashboard_select option:selected').text();
            self.ks_dashboard_item_model.call('write',[parseInt(ks_item_id), {'ks_dashboard_ninja_board_id': parseInt(dashboard_id)}]
            ).then(function (result) {

                self.do_notify(
                    _t("Item Moved"),
                    _t('Selected item is moved to '+dashboard_name+' .')
                );
                    $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
             })
        },

        ksOpenItemFormView: function (e) {
            var self = this;
            self.do_action({
                name: _t('Selected record'),
                type: 'ir.actions.act_window',
                res_model: e.currentTarget.dataset.model,
                domain: "[]",
                views: [
                    [false, 'form']
                ],
                view_mode: 'form',
                res_id: parseInt(e.currentTarget.dataset.recordId),
                target: 'current',
            }, {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            });
        },


        ksRenderChartColorOptions: function (e) {
            var self = this;
            if (!$(e.currentTarget).parent().hasClass('ks_date_filter_selected')) {
                //            FIXME : Correct this later.
                var $parent = $(e.currentTarget).parent().parent();
                $parent.find('.ks_date_filter_selected').removeClass('ks_date_filter_selected')
                $(e.currentTarget).parent().addClass('ks_date_filter_selected')
                var data = $parent.data();
                this.ksChartColors(e.currentTarget.dataset.chartColor, this.chart_container[$parent.data().itemId], $parent.data().chartType, $parent.data().chartFamily)
                new Model('ks_dashboard_ninja.item').call('write', [$parent.data().itemId, {
                    "ks_chart_item_color": e.currentTarget.dataset.chartColor
                }]);
            }
        },

         _KsGetDateValues: function(){
            var self = this;
            var date_format = time.strftime_to_moment_format(_t.database.parameters.date_format);
            var check_format = date_format.search(/YYYY/);
            if(!(check_format !== -1)){
                date_format = date_format.replace(/YY/g,"YYYY");
            }
            self.ksCurrentDashboardModel.call('read',[[self.ks_dashboard_id],['ks_dashboard_start_date', 'ks_dashboard_end_date','ks_date_filter_selection']]
            ).then(function (result) {
                self.ks_date_filter_data = result
            }).done(function () {
                var date_filter_selected = self.ks_date_filter_data[0].ks_date_filter_selection;
                $('#'+date_filter_selected ).addClass("ks_date_filter_selected");
                $('#ks_date_filter_selection').text(self.ks_date_filter_selections[date_filter_selected]["text"]);
                if (self.ks_date_filter_data[0].ks_dashboard_start_date && self.ks_date_filter_data[0].ks_dashboard_start_date) {
                    self.ks_start_date = self.ks_date_filter_data[0].ks_dashboard_start_date.split(' ')[0];
                    $("#ksActualStartDateToStore").val(self.ks_start_date);
                    self.ks_end_date = self.ks_date_filter_data[0].ks_dashboard_end_date.split(' ')[0];
                    $("#ksActualEndDateToStore").val(self.ks_start_date);
                    self.ks_start_date = moment( self.ks_start_date).format(date_format);
                    self.ks_end_date = moment( self.ks_end_date).format(date_format);
                    $("#ks_start_date_picker").val(self.ks_start_date);
                    $("#ks_end_date_picker").val(self.ks_end_date);
                }else {
                    self.ks_start_date = self.ks_end_date = null;
                    $(".apply-dashboard-date-filter").hide();
                    $(".clear-dashboard-date-filter").hide();
                }
                if (self.ks_date_filter_data[0].ks_date_filter_selection === 'l_custom' && self.ks_dashboard_data.ks_dashboard_list) {
                    $('.ks_date_filter_selection_input').show();
                    $('.ks_date_filter_selection_input').removeClass('ks_hide');


                    $('.ks_date_input_fields').removeClass('ks_hide');
                    $('.ks_date_filter_dropdown').addClass("ks_btn_first_child_radius");
                }else if (self.ks_date_filter_data[0].ks_date_filter_selection !== 'l_custom' && self.ks_dashboard_data.ks_dashboard_list) {
                // Comment this to see working of date filter selection
                    $('.ks_date_filter_selection_input').show();
                    $('.ks_date_input_fields').addClass('ks_hide');
                }
            });
        },

        _onKsClearDateValues: function(){
            var self = this;
            var board = new Model('ks_dashboard_ninja.board');
            board.call('write', [this.ks_dashboard_id, {
                "ks_dashboard_start_date": false,
                "ks_dashboard_end_date": false,
                "ks_date_filter_selection": 'l_none',
            }]).then(function (data) {
                $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
            }.bind(this));
        },

        _checkDateFields:function(){
            if(!($("#ks_start_date_picker").val())){
                $("#ks_start_date_picker").val($("#ks_end_date_picker").val());
                $("#ksActualStartDateToStore").val($("#ksActualEndDateToStore").val());
            }
            if(!($("#ks_end_date_picker").val())){
                $("#ks_end_date_picker").val($("#ks_start_date_picker").val());
                $("#ksActualEndDateToStore").val($("#ksActualStartDateToStore").val());
            }
        },

         _renderDateFilterHeader:  function () {
            var self = this;

            //Show Print option cause items are present.
            self.$el.find(".ks_dashboard_link").removeClass("ks_hide");

            //Initialization of the date picker with on-select event
            self.$el.find("#ks_start_date_picker").datepicker({
                dateFormat: "yy/mm/dd",
                altFormat: "yy-mm-dd",
                altField: "#ksActualStartDateToStore",
                changeMonth: true,
                changeYear: true,
                language: moment.locale(),
                onSelect: function (ks_start_date) {
                    self.$el.find(".apply-dashboard-date-filter").show();
                    self.$el.find(".clear-dashboard-date-filter").show();
                    self.$el.find(".apply-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find("#ks_start_date_picker").val(moment(new Date(ks_start_date)).format(self.date_format));
                    self._checkDateFields();
                },
            });

            self.$el.find("#ks_end_date_picker").datepicker({
                dateFormat: "yy/mm/dd",
                altFormat: "yy-mm-dd",
                altField: "#ksActualEndDateToStore",
                changeMonth: true,
                changeYear: true,
                language: moment.locale(),
                onSelect: function (ks_end_date) {
                    self.$el.find(".apply-dashboard-date-filter").show();
                    self.$el.find(".clear-dashboard-date-filter").show();
                    self.$el.find(".apply-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find(".clear-dashboard-date-filter").removeClass("ks_hide");
                    self.$el.find("#ks_end_date_picker").val(moment(new Date(ks_end_date)).format(self.date_format));
                    self._checkDateFields();
                },
            });
            self._KsGetDateValues();
            $('#ui-datepicker-div').addClass('ks_dashboard_datepicker_z-index');
        },


        _onKsApplyDateFilter: function (e) {
            var self = this;
            var date_format = time.strftime_to_moment_format(_t.database.parameters.date_format);
            var check_format = date_format.search(/YYYY/);
            if(!(check_format !== -1)){
                date_format = date_format.replace(/YY/g,"YYYY");
            }
            var start_date = $("#ksActualStartDateToStore").val();
            var end_date =  $("#ksActualEndDateToStore").val();
            if(start_date === "Invalid date"){
                alert("Invalid Date is given in Start Date.")
            }else if(end_date === "Invalid date"){
                alert("Invalid Date is given in End Date.")
            }else if($('.ks_date_filter_selected').attr('id')!=="l_custom"){
                self.ksCurrentDashboardModel.call('write', [self.ks_dashboard_id, {
                    "ks_date_filter_selection": $('.ks_date_filter_selected').attr('id'),
                }]).then(function (data) {
                    $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
                });
            }else{
                start_date = start_date + " 00:00:00";
                end_date  = end_date + " 23:59:59";
                if(start_date && end_date){
                    if(start_date < end_date){
                        var board = new Model('ks_dashboard_ninja.board');
                        board.call('write', [this.ks_dashboard_id, {
                            "ks_dashboard_start_date": start_date,
                            "ks_dashboard_end_date": end_date,
                            "ks_date_filter_selection": $('.ks_date_filter_selected').attr('id')
                        }]).then(function (data) {
                            $.when(self.ks_fetch_data()).then(function () {
                                self.ksRenderDashboard();
                            });
                        }.bind(this));
                    }else{
                        alert(_t("Start date should be less than end date"));
                    }
                }else{
                    alert(_t("Please enter start date and end date"));
                }
            }
        },

        _onKsToggleMenu: function (e) {
            if(!($(".ks_dashboard_links").hasClass("d-flex"))){
                $(".ks_dashboard_links").addClass('d-flex');
            }else{
                $(".ks_dashboard_links").removeClass('d-flex');
            }
        },

        _onKsDashboardPrint:function(e){
            var self = this;
            framework.blockUI();
            var current_date  = $.datepicker.formatDate('yy/mm/dd', new Date());
            var report_name = this.ksCurrentDashboard+"_"+current_date
            $(".ks_dashboard_add_layout").css("display","none");
            $(".ks_dashboard_edit_layout").css("display","none");
            $(".apply-dashboard-date-filter").css("display","none");
            $(".clear-dashboard-date-filter").css("display","none");
            $(".ks_date_selection_box").css("display","none");
            $(".ks_date_input_fields").show();
            $(".ks-dashboard-date-labels").show();
            $(".ksstartdatepicker").removeClass("ks_btn_middle_child");
            $(".ksenddatepicker").removeClass("ks_btn_last_child");
            if($(".ks_dashboard_links").hasClass("d-flex")){
                $(".ks_dashboard_links").removeClass('d-flex');
            }
            $(".print-dashboard-btn").css("display","none");
            $(".ks_dashbaord_ninja_toggle_menu").hide();
            $("#ksstartdatepicker").val(this.ks_start_date);
            $("#ksenddatepicker").val(this.ks_end_date);
            $(".ks_header_container_div").css("background","transparent");
            document.querySelector('.ks_dashboard_ninja').style.fontFeatureSettings = this.$el.css("font-family");
            html2canvas(document.querySelector(".ks_dashboard_ninja"),{
                //           To show logs in console related to dashboard, uncomment below line
                //            logging: true,
                profile: true,
                useCORS: true
            }).then(canvas => {
                self.renderElement();
                var ks_img = canvas.toDataURL(
                'image/png');
                var doc = new jsPDF('p', 'mm');
                doc.addImage(ks_img, 'PNG', 5, 10, 200, 0);
                doc.save(report_name);
                framework.unblockUI();
            })
        },

        _ksShowApplyClearDateButton: function () {
            if ($("#ks_start_date_picker").val() && $("#ks_end_date_picker").val()) {
                $(".apply-dashboard-date-filter").removeClass("ks_hide");
                $(".clear-dashboard-date-filter").removeClass("ks_hide");
            } else {
                $(".apply-dashboard-date-filter").addClass("ks_hide");
                $(".clear-dashboard-date-filter").addClass("ks_hide");
            }
        },

       _ksOnDateFilterMenuSelect: function (e) {
            if (e.target.id !== 'ks_date_selector_container') {
                var self = this;
                _.each($('.ks_date_filter_selected'), function ($filter_options) {
                    $($filter_options).removeClass("ks_date_filter_selected")
                });
                $(e.target.parentElement).addClass("ks_date_filter_selected");
                $('#ks_date_filter_selection').text(self.ks_date_filter_selections[e.target.parentElement.id]["text"]);

                if (e.target.parentElement.id !== "l_custom") {
                    $('.ks_date_input_fields').addClass("ks_hide");
                    $('.ks_date_filter_dropdown').removeClass("ks_btn_first_child_radius");
                    e.target.parentElement.id === "l_none" ? self._onKsClearDateValues() : self._onKsApplyDateFilter();
                } else if (e.target.parentElement.id === "l_custom") {
                    $("#ks_start_date_picker").val(null).removeClass("ks_hide");
                    $("#ks_end_date_picker").val(null).removeClass("ks_hide");


                    $('.ks_date_input_fields').removeClass("ks_hide");
                    $('.ks_date_filter_dropdown').addClass("ks_btn_first_child_radius");
                }
            }
        },

        _onKsAdditemTypeClick : function(e){
         var self = this;
         var context = {};
         context['ks_dashboard_id'] = self.ks_dashboard_id;
         context['ks_dashboard_item_type'] = e.currentTarget.dataset.item;
         self.do_action({
            type : 'ir.actions.act_window',
            res_model : 'ks_dashboard_ninja.item',
            view_id : 'ks_dashboard_ninja_list_form_view',
            views : [
                [false, 'form']
            ],
            target : 'current',
            context :context,

         },{
         on_reverse_breadcrumb : this.on_reverse_breadcrumb,
         });
        },

        ksChartExportXLS : function(e){
//            console.log("XLS");
           var chart_id = e.currentTarget.dataset.chartId;
           var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
           var data = {
                        "header":name,
                        "chart_data":this.ks_dashboard_data.ks_item_data[chart_id].ks_chart_data,
                      }
                framework.blockUI();
                this.session.get_file({
                    url: '/ks_dashboard_ninja/export/'+e.currentTarget.dataset.format,
                    data: {data:JSON.stringify(data)},
                    complete: framework.unblockUI,
                    error: crash_manager.rpc_error.bind(crash_manager),
                });
        },

        ksChartExportPdf : function(e){
            console.log("pdf print");
            var chart_id = e.currentTarget.dataset.chartId;
            var name = this.ks_dashboard_data.ks_item_data[chart_id].name;
            var base64_image = this.chart_container[chart_id].toBase64Image()
            var doc = new jsPDF('p', 'mm');
            doc.addImage(base64_image, 'PNG', 5, 10, 200, 0);
            doc.save(name);
        },


        onKsChartMoreInfoClick : function(evt){
            var self = this;
            var item_id = evt.currentTarget.dataset.itemId;
            var item_data = self.ks_dashboard_data.ks_item_data[item_id];
            var groupBy = item_data.ks_chart_groupby_type==='relational_type'?item_data.ks_chart_relation_groupby:item_data.ks_chart_relation_groupby+':'+item_data.ks_chart_date_groupby;
            var domain = JSON.parse(item_data.domain);
            var action = {
                    name: _t(item_data.name),
                    type: 'ir.actions.act_window',
                    res_model: item_data.model_id,
                    domain: domain || [],
                    context: {
                        'group_by':groupBy,
                    },
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    view_mode: 'list',
                    target: 'current',
                }
            self.do_action(action, {
                                on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                            });

        },

        onKsChartCanvasClick : function(evt){
            var self = this;
            var item_id = parseInt($($(evt.currentTarget).parentsUntil('.grid-stack').slice(-1)[0]).attr('data-gs-id'));
            var myChart = self.chart_container[item_id];
            var activePoint = myChart.getElementAtEvent(evt)[0];
            if (activePoint){
                var item_data = self.ks_dashboard_data.ks_item_data[item_id];

                var groupBy = item_data.ks_chart_groupby_type==='relational_type'?item_data.ks_chart_relation_groupby:item_data.ks_chart_relation_groupby+':'+item_data.ks_chart_date_groupby;
                var domain = item_data.domain;
                var action = {
                    name: _t(item_data.name),
                    type: 'ir.actions.act_window',
                    res_model: item_data.model_id,
                    domain: domain || [],
                    context: {
                        'group_by':groupBy,
                    },
                    views: [
                        [false, 'list'],
                        [false, 'form']
                    ],
                    view_mode: 'list',
                    target: 'current',
                }
                if(activePoint._chart.data.groupByIds){
                    action['context']['search_default_'+groupBy] = activePoint._chart.data.groupByIds[activePoint._index];
                }
                self.do_action(action, {
                                    on_reverse_breadcrumb: self.on_reverse_breadcrumb,
                                });
            }
        },
    });

    core.action_registry
        .add('ks_dashboard_ninja', KsDashBoardNinja);

    return KsDashBoardNinja;
});