odoo.define('gbs_purchase_cs_process', function (require) {
   "use strict";
   var form_widget = require('web.form_widgets');
   var ajax = require('web.ajax');
   var core = require('web.core');
   var _t = core._t;
   var session = require('web.session');

   var QuotationsButton = form_widget.WidgetButton.include({


        on_click: function () {
            if(this.node.attrs.custom === "custom_click") {
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var params = {
                    'rfq': rfq_id == false ?'':rfq_id,
                };

                if (params['rfq']){
                    ajax.jsonRpc("/purchase/get_quotations", 'call', {
                        'rfq_id': params['rfq']
                    }).then(function (data) {
                        self.drawTable(data);
                    });
                }else{
                    this.do_warn(_t("The following fields are invalid :"),'Please Select Input Field Correctly.');
                }
            }
            else if(this.node.attrs.custom === "save_click"){
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var listOfObjects = [];
                var error = 0;
                //listOfObjects = self.getRowData(listOfObjects,error);
                let returned_data = self.getRowData(listOfObjects,error);
                listOfObjects = returned_data[0]
                error = returned_data[1]
                var remarks_maker = $("#remarks_maker").val();
                var remarks_checker = $("#remarks_checker").val();
                var remarks_approver = $("#remarks_approver").val();
                var params = {
                    'listOfObjects': listOfObjects == false ?'':listOfObjects,
                    'rfq': rfq_id == false ?'':rfq_id,
                    'remarks_maker':remarks_maker,
                    'remarks_checker':remarks_checker,
                    'remarks_approver':remarks_approver
                };
                if (params['listOfObjects'] && error===0){
                    ajax.jsonRpc("/purchase/save_cs", 'call', {
                        'listOfObjects': params['listOfObjects'],'rfq_id': params['rfq'],'remarks_maker': params['remarks_maker'],'remarks_checker': params['remarks_checker'],'remarks_approver': params['remarks_approver']
                    }).then(function (data) {
                        if(data['return_val'] === "true"){
                            self.alertModal('Success!','Comparative Study selected data saved!');
                        }
                        else{
                            self.alertModal('Error!','Something happened during saving!');
                        }
                    });
                }
            }
            else if(this.node.attrs.custom === "cancel_click"){
                location.reload();
                //$("#status_div").load(location.href + " #status_div");
            }
            else if(this.node.attrs.custom === "send_to_manager_click"){
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var listOfObjects = [];
                var error = 0;
                //listOfObjects = self.getRowData(listOfObjects,error);
                let returned_data = self.getRowData(listOfObjects,error);
                listOfObjects = returned_data[0]
                error = returned_data[1]
                var remarks_maker = $("#remarks_maker").val();
                var remarks_checker = $("#remarks_checker").val();
                var remarks_approver = $("#remarks_approver").val();
                var params = {
                    'listOfObjects': listOfObjects == false ?'':listOfObjects,
                    'rfq': rfq_id == false ?'':rfq_id,
                    'remarks_maker':remarks_maker,
                    'remarks_checker':remarks_checker,
                    'remarks_approver':remarks_approver
                };
                if (params['rfq']&& error===0){
                    ajax.jsonRpc("/purchase/send_to_manager", 'call', {
                        'listOfObjects': params['listOfObjects'],'rfq_id': params['rfq'],'remarks_maker': params['remarks_maker'],'remarks_checker': params['remarks_checker'],'remarks_approver': params['remarks_approver']
                    }).then(function (data) {
                        if(data['return_val'] === "true"){
                            $('.oe_form_field_status li').each(function (i) {
                                $(this).removeClass('oe_active');
                            });
                            $('[data-id="sent_for_confirmation"]').addClass('oe_active');
                            $("#send_to_manager_btn").hide();
                            $("#save_btn").hide();
                            $("#cancel_btn").hide();

                            self.alertModal('Success!','CS Send to Manager for confirmation!');
                        }
                        else{
                            self.alertModal('Error!','Something happened during sending!');
                        }
                    });
                }
            }
            else if(this.node.attrs.custom === "confirm_click"){
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var listOfObjects = [];
                var error = 0;
                //listOfObjects = self.getRowData(listOfObjects,error);
                let returned_data = self.getRowData(listOfObjects,error);
                listOfObjects = returned_data[0]
                error = returned_data[1]
                var remarks_maker = $("#remarks_maker").val();
                var remarks_checker = $("#remarks_checker").val();
                var remarks_approver = $("#remarks_approver").val();
                var params = {
                    'listOfObjects': listOfObjects == false ?'':listOfObjects,
                    'rfq': rfq_id == false ?'':rfq_id,
                    'remarks_maker':remarks_maker,
                    'remarks_checker':remarks_checker,
                    'remarks_approver':remarks_approver
                };
                if (params['rfq']&& error===0){
                    ajax.jsonRpc("/purchase/confirm_cs", 'call', {
                        'listOfObjects': params['listOfObjects'],'rfq_id': params['rfq'],'remarks_maker': params['remarks_maker'],'remarks_checker': params['remarks_checker'],'remarks_approver': params['remarks_approver']
                    }).then(function (data) {
                        if(data['return_val'] === "true"){
                            $('.oe_form_field_status li').each(function (i) {
                                $(this).removeClass('oe_active');
                            });
                            $('[data-id="confirmed"]').addClass('oe_active');
                            $("#confirm_btn").hide();
                            self.alertModal('Success!','CS has been confirmed!');
                        }
                        else{
                            self.alertModal('Error!','Something happened during sending!');
                        }
                    });
                }
            }
            else if(this.node.attrs.custom === "approve_click"){
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var listOfObjects = [];
                var error = 0;
                //listOfObjects = self.getRowData(listOfObjects,error);
                let returned_data = self.getRowData(listOfObjects,error);
                listOfObjects = returned_data[0]
                error = returned_data[1]
                var remarks_maker = $("#remarks_maker").val();
                var remarks_checker = $("#remarks_checker").val();
                var remarks_approver = $("#remarks_approver").val();
                var params = {
                    'listOfObjects': listOfObjects == false ?'':listOfObjects,
                    'rfq': rfq_id == false ?'':rfq_id,
                    'remarks_maker':remarks_maker,
                    'remarks_checker':remarks_checker,
                    'remarks_approver':remarks_approver
                };
                if (params['rfq']&& error===0){
                    ajax.jsonRpc("/purchase/approve_cs", 'call', {
                        'listOfObjects': params['listOfObjects'],'rfq_id': params['rfq'],'remarks_maker': params['remarks_maker'],'remarks_checker': params['remarks_checker'],'remarks_approver': params['remarks_approver']
                    }).then(function (data) {
                        if(data['return_val'] === "true"){
                            $('.oe_form_field_status li').each(function (i) {
                                $(this).removeClass('oe_active');
                            });
                            $('[data-id="approved"]').addClass('oe_active');
                            $("#approve_btn").hide();
                            self.alertModal('Success!','CS has been approved! ');
                        }
                        else{
                            self.alertModal('Error!','Something happened during sending!');
                        }
                    });
                }
            }
            else if(this.node.attrs.custom === "close_click"){
                $("#alert-modal").modal('hide');
                var self = this;
                var rfq_id = self.field_manager.get_field_value('rfq_id');
                var params = {
                    'rfq': rfq_id == false ?'':rfq_id,
                };

                if (params['rfq']){
                    ajax.jsonRpc("/purchase/get_quotations", 'call', {
                        'rfq_id': params['rfq']
                    }).then(function (data) {
                        self.drawTable(data);
                    });
                }else{
                    this.do_warn(_t("The following fields are invalid :"),'Please Select Input Field Correctly.');
                }
                //location.reload();
                //$("#status_div").load(location.href + " #status_div");
            }
            else {
                this._super();
            }
        },

        drawTable: function (data) {
            var json_header = JSON.stringify(data.header.dynamic.length);
            var th10 = "<th rowspan='3' class='text-center'  style='display:none;'></th>";
            var th11 = "<th rowspan='3' class='text-center'>"+data.header.pr_no+"</th>";
            var th12 = "<th rowspan='3' class='text-center product-id'>"+data.header.item+"</th>";
            var th13 = "<th rowspan='3' class='text-center req-qty'>"+data.header.req_qty+"</th>";
            var th14 = "<th rowspan='3' class='text-center'>"+data.header.unit+"</th>";
            var th15 = "<th rowspan='3' class='text-center'>"+data.header.last_price+"</th>";
            var th = th10+th11 + th12 + th13 + th14 + th15;
            for (var n = 0; n < data.header.dynamic.length; n++) {
                var thd =  "<th colspan='3' class='text-center'>"+data.header.dynamic[n].name+"</th>";
                th = th + thd;
            }
            var th16 = "<th rowspan='3' class='text-center'>"+data.header.approved_price+"</th>";
            var th17 = "<th rowspan='3' class='text-center'>"+data.header.total+"</th>";
            var th18 = "<th rowspan='3' class='text-center'>"+data.header.po+"</th>";
            var th19 = "<th rowspan='3' class='text-center' style='display:none;'></th>";
            var th110 = "<th rowspan='3' class='text-center' style='display:none;'></th>";
            var th = th + th16 + th17 + th18 + th19+th110;
            document.getElementById('tr_1').innerHTML = th;

            // tr_2
            var th2 ="";
            for (var n = 0; n < data.header.dynamic.length; n++) {
                var thd2 =  "<th colspan='3' class='text-center'>"+data.header.dynamic[n].supplier+"</th>";
                //var thd3 =  "<th class='text-center'>Total</th>";
                th2 = th2 + thd2;
            }
            document.getElementById('tr_2').innerHTML = th2;
            var th3 ="";
            for (var n = 0; n < data.header.dynamic.length; n++) {
                var thd21 =  "<th class='text-center'>"+"Rate"+"</th>";
                var thd31 =  "<th class='text-center'>Total</th>";
                var thd41 =  "<th class='text-center' style='display:none;'></th>";
                var thd51 =  "<th class='text-center' style='display:none;'></th>";
                var thd61 =  "<th class='text-center' style='display:none;'></th>";
                var thd71 =  "<th class='text-center'></th>";
                th3 = th3 + thd21 + thd31 + thd41+ thd51+ thd61+ thd71;
            }
            document.getElementById('tr_3').innerHTML = th3;

            var final_tr = "";
            var chk = 1;
            var total_quotations = 0;
            var cs_processed_selected_rate = 0;
            var cs_processed_selected_total = 0;
            var created_po_text = "";

            for (var n = 0; n < data.row_objs.length; n++) {

                var tr_ = "<tr>";
                var td0 =  "<td class='text-left product-id' style='display:none;'>"+data.row_objs[n].product_id+"</td>";
                var td1 =  "<td class='text-left'>"+data.row_objs[n].pr_name+"</td>";
                var td2 =  "<td class='text-left'>"+data.row_objs[n].product_name+"</td>";
                var td3 =  "<td class='text-left product-qty'>"+data.row_objs[n].product_ordered_qty+"</td>";
                var td4 =  "<td class='text-left product-unit'>"+data.row_objs[n].product_unit+"</td>";
                var td5 =  "<td class='text-right'>"+data.row_objs[n].last_price+"</td>";
                tr_ = tr_ + td0 + td1 + td2 + td3 + td4 + td5;

                var chkr = 1;
                total_quotations = data.row_objs[n].quotations.length;
                for (var m = 0; m < data.row_objs[n].quotations.length; m++) {
                    if(typeof data.row_objs[n].quotations[m].price === 'object'){
                        data.row_objs[n].quotations[m].price = 0.0;
                        data.row_objs[n].quotations[m].total = 0.0;
                    }
                    var price = data.row_objs[n].quotations[m].price;
                    var total = data.row_objs[n].quotations[m].total;
                    var created_po = data.row_objs[n].quotations[m].created_po;
                    var po_line_id = data.row_objs[n].quotations[m].po_line_id;
                    var vendor_id = data.row_objs[n].quotations[m].vendor_id;
                    var cq_processed = data.row_objs[n].quotations[m].cq_processed;
                    if(typeof created_po === 'string'){
                        created_po_text = created_po;
                    }

                    if(cq_processed === true){
                        cs_processed_selected_rate = price;
                        cs_processed_selected_total = total;
                        var tdm1 =  "<td class='text-right td-color q-data chk-rate group"+chk+chkr+"'" + "id='rate"+chk+chkr+"'>"+price+"</td>";
                        var tdm2 =  "<td class='text-right td-color q-data chk-total group"+chk+chkr+"'" + "id='total"+chk+chkr+"'>"+total+"</td>";
                        var tdm3 =  "<td style='display:none;' class='text-right td-color q-data chk-po_line_id group"+chk+chkr+"'" + "id='po_line_id"+chk+chkr+"'>"+po_line_id+"</td>";
                        var tdm4 =  "<td style='display:none;' class='text-right td-color q-data chk-vendor_id group"+chk+chkr+"'" + "id='vendor_id"+chk+chkr+"'>"+vendor_id+"</td>";
                        var tdm5 =  "<td style='display:none;' class='text-right td-color q-data chk-cs_process group"+chk+chkr+"'" + "id='cs_process"+chk+chkr+"'>"+cq_processed+"</td>";
                        var tdm6 =  "<td class='text-right q-data "+"chk"+chk+chkr+"'><input type='checkbox' class='chk-box' id='"+chk+chkr+"' checked/></td>";
                    }
                    else{
                        var tdm1 =  "<td class='text-right q-data chk-rate group"+chk+chkr+"'" + "id='rate"+chk+chkr+"'>"+price+"</td>";
                        var tdm2 =  "<td class='text-right q-data chk-total group"+chk+chkr+"'" + "id='total"+chk+chkr+"'>"+total+"</td>";
                        var tdm3 =  "<td style='display:none;' class='text-right q-data chk-po_line_id group"+chk+chkr+"'" + "id='po_line_id"+chk+chkr+"'>"+po_line_id+"</td>";
                        var tdm4 =  "<td style='display:none;' class='text-right q-data chk-vendor_id group"+chk+chkr+"'" + "id='vendor_id"+chk+chkr+"'>"+vendor_id+"</td>";
                        var tdm5 =  "<td style='display:none;' class='text-right q-data chk-cs_process group"+chk+chkr+"'" + "id='cs_process"+chk+chkr+"'>"+cq_processed+"</td>";
                        var tdm6 =  "<td class='text-right q-data "+"chk"+chk+chkr+"'><input type='checkbox' class='chk-box' id='"+chk+chkr+"'/></td>";
                    }

                    tr_ = tr_ + tdm1 + tdm2 + tdm3 + tdm4 + tdm5 + tdm6;
                    chkr = chkr + 1;
                }
                if(cs_processed_selected_rate!==0){
                    var td6 =  "<td class='text-left selected-rate'>"+cs_processed_selected_rate+"</td>";
                }
                else{
                    var td6 =  "<td class='text-left selected-rate'></td>";
                }
                if(cs_processed_selected_total!==0){
                    var td7 =  "<td class='text-left selected-total'>"+cs_processed_selected_total+"</td>";
                }
                else{
                    var td7 =  "<td class='text-left selected-total'></td>";
                }
                var td8 =  "<td class='text-left created-po'>"+created_po_text+"</td>";
                var td9 =  "<td style='display:none;' class='text-left selected-po-line'></td>";
                var td10 =  "<td style='display:none;' class='text-left selected-vendor'></td>";
                tr_ =  tr_ + td6 + td7 + td8 + td9 +td10+ "</tr>";
                final_tr = final_tr + tr_;
                chk = chk + 1;
            }
            document.getElementById('tbody_1').innerHTML = final_tr;
            //check if remarks data available
            if(data.user_remarks){
                var remarks_div1 = "<div class='col-md-4'><p>Remarks(Creator):</p><textarea id='remarks_maker' name='remarks_maker' rows='4' cols='50'>"+data.user_remarks+"</textarea></div>";
            }
            else{
                var remarks_div1 = "<div class='col-md-4'><p>Remarks(Creator):</p><textarea id='remarks_maker' name='remarks_maker' rows='4' cols='50'></textarea></div>";

            }
            if(data.manager_remarks){
                var remarks_div2 = "<div class='col-md-4'><p>Remarks(Validator):</p><textarea id='remarks_checker' name='remarks_checker' rows='4' cols='50'>"+data.manager_remarks+"</textarea></div>";

            }
            else{
                var remarks_div2 = "<div class='col-md-4'><p>Remarks(Validator):</p><textarea id='remarks_checker' name='remarks_checker' rows='4' cols='50'></textarea></div>";

            }
            if(data.procurement_head_remarks){
                var remarks_div3 = "<div class='col-md-4'><p>Remarks(Approver):</p><textarea id='remarks_approver' name='remarks_approver' rows='4' cols='50'>"+data.procurement_head_remarks+"</textarea></div>";
            }
            else{
                var remarks_div3 = "<div class='col-md-4'><p>Remarks(Approver):</p><textarea id='remarks_approver' name='remarks_approver' rows='4' cols='50'></textarea></div>";
            }

            var main_remarks_div = "";
            session.user_has_group('purchase.group_purchase_user').then(function(has_group) {
                if(has_group) {
                    main_remarks_div = main_remarks_div + remarks_div1;
                }
            });
            session.user_has_group('purchase.group_purchase_manager').then(function(has_group) {
                if(has_group) {
                    main_remarks_div = main_remarks_div + remarks_div2;
                }
            });
            session.user_has_group('gbs_application_group.group_head_of_procurement').then(function(has_group) {
                if(has_group) {
                    main_remarks_div = main_remarks_div + remarks_div3;
                }
            });

            document.getElementById('remarks_div').innerHTML = main_remarks_div;




            $(document).find('.chk-box').on('click', function(){
                if($(this).is(":checked")){
                    var element_id = $(this).attr('id');
                    var rate = $("#rate"+element_id).html();
                    var total = $("#total"+element_id).html();
                    var po_line_id = $("#po_line_id"+element_id).html();
                    var vendor_id = $("#vendor_id"+element_id).html();

                    $(this).closest('tr').find('.chk-box').attr('checked', false);
                    $(this).prop("checked", true);

                    $(this).closest('tr').find('td.selected-rate').text(rate);
                    $(this).closest('tr').find('td.selected-total').text(total);
                    $(this).closest('tr').find('td.selected-po-line').text(po_line_id);
                    $(this).closest('tr').find('td.selected-vendor').text(vendor_id);
                    //add class =td-color
                    $(this).closest('tr').find('td.q-data').removeClass("td-color");
                    $(this).closest('tr').find('td.group'+element_id).addClass("td-color");
                }
                else{
                    var element_id = $(this).attr('id');
                    $(this).closest('tr').find('td.group'+element_id).removeClass("td-color");
                    $(this).closest('tr').find('td.selected-rate').text('');
                    $(this).closest('tr').find('td.selected-total').text('');
                    $(this).closest('tr').find('td.selected-po-line').text('');
                    $(this).closest('tr').find('td.selected-vendor').text('');
                }

            });
            $(document).ready(function () {
                $('input[type=checkbox]:checked').each(function () {
                    var element_id = $(this).attr('id');
                    var rate = $("#rate"+element_id).html();
                    var total = $("#total"+element_id).html();
                    var po_line_id = $("#po_line_id"+element_id).html();
                    var vendor_id = $("#vendor_id"+element_id).html();

                    $(this).closest('tr').find('.chk-box').attr('checked', false);
                    $(this).prop("checked", true);

                    $(this).closest('tr').find('td.selected-rate').text(rate);
                    $(this).closest('tr').find('td.selected-total').text(total);
                    $(this).closest('tr').find('td.selected-po-line').text(po_line_id);
                    $(this).closest('tr').find('td.selected-vendor').text(vendor_id);
                    //add class =td-color
                    $(this).closest('tr').find('td.q-data').removeClass("td-color");
                    $(this).closest('tr').find('td.group'+element_id).addClass("td-color");
                });
            });
        },
        getRowData: function(listOfObjects,error){
            $("table > tbody > tr").each(function () {
                var currentRow = $(this);
                var selectedRate = currentRow.find(".selected-rate").text();
                if (selectedRate === '') {
                    error = error + 1;
                    $('#alert-modal-title').html('Error!');
                    $('#alert-modal-body').html('Every product line needs to be selected!');
                    $('#alert-modal').modal('show');
                    return;
                }
                var singleObj = {};
                singleObj['po_line'] = currentRow.find(".selected-po-line").text();
                singleObj['pro_id'] = currentRow.find(".product-id").text();
                singleObj['req_qty'] = currentRow.find(".product-qty").text();
                singleObj['pro_unit'] = currentRow.find(".product-unit").text()
                singleObj['selected_rate'] = selectedRate;
                singleObj['selected_total'] = currentRow.find(".selected-total").text();
                singleObj['selected_vendor'] = currentRow.find(".selected-vendor").text();
                listOfObjects.push(singleObj);
            });
            return [listOfObjects, error];
        },

        alertModal: function (title, body) {
            $('#alert-modal-title').html(title);
            $('#alert-modal-body').html(body);
            $('#alert-modal').modal('show');
        },

    });
//
return {
    QuotationsButton: QuotationsButton
};

});