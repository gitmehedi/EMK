odoo.define('gbs_purchase_cs_process', function (require) {
   "use strict";
   var form_widget = require('web.form_widgets');
   var ajax = require('web.ajax');
   var core = require('web.core');
   var _t = core._t;


   var QuotationsButton = form_widget.WidgetButton.include({
//         start: function() {
//            this._super.apply(this, arguments);
//            var self = this;
//            if (self.view.model === 'purchase.rfq.cs') {
//                $(".chk11").change(function() {
//                    if(this.checked) {
//                        console.log('Checked!');
//                    }
//                });
//            }
//        },
//        events: {
//            'focus input': 'onfocus_input',
//            'blur input': 'onblur_input',
//        },

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
            }else {
                this._super();
            }
        },

//        on_click_input: function() {
//            console.log("Hello World!");
//        },

//        onfocus_input: function (e) {
//            console.log("Hello World!");
//        },
//        onblur_input: function (e) {
//            console.log("Hello World!");
//        },

        drawTable: function (data) {
            var json_header = JSON.stringify(data.header.dynamic.length);
            var th11 = "<th rowspan='3' class='text-center'>"+data.header.pr_no+"</th>";
            var th12 = "<th rowspan='3' class='text-center'>"+data.header.item+"</th>";
            var th13 = "<th rowspan='3' class='text-center'>"+data.header.req_qty+"</th>";
            var th14 = "<th rowspan='3' class='text-center'>"+data.header.unit+"</th>";
            var th15 = "<th rowspan='3' class='text-center'>"+data.header.last_price+"</th>";
            var th = th11 + th12 + th13 + th14 + th15;
            for (var n = 0; n < data.header.dynamic.length; n++) {
                var thd =  "<th colspan='3' class='text-center'>"+data.header.dynamic[n].name+"</th>";
                th = th + thd;
            }
            var th16 = "<th rowspan='3' class='text-center'>"+data.header.approved_price+"</th>";
            var th17 = "<th rowspan='3' class='text-center'>"+data.header.total+"</th>";
            var th18 = "<th rowspan='3' class='text-center'>"+data.header.remarks+"</th>";

            var th = th + th16 + th17 + th18;
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
                var thd41 =  "<th class='text-center'></th>";
                th3 = th3 + thd21 + thd31 + thd41;
            }
            document.getElementById('tr_3').innerHTML = th3;

            var final_tr = "";
            var chk = 1;
            for (var n = 0; n < data.row_objs.length; n++) {

                var tr_ = "<tr>";

                var td1 =  "<td class='text-left'>"+data.row_objs[n].pr_name+"</td>";
                var td2 =  "<td class='text-left'>"+data.row_objs[n].product_name+"</td>";
                var td3 =  "<td class='text-left'>"+data.row_objs[n].product_ordered_qty+"</td>";
                var td4 =  "<td class='text-left'>"+data.row_objs[n].product_unit+"</td>";
                var td5 =  "<td class='text-right'>"+data.row_objs[n].last_price+"</td>";
                tr_ = tr_ + td1 + td2 + td3 + td4 + td5;

                var chkr = 1;
                for (var m = 0; m < data.row_objs[n].quotations.length; m++) {
                    var price = data.row_objs[n].quotations[m].price;
                    var total = data.row_objs[n].quotations[m].total;
                    var tdm1 =  "<td class='text-right chk-rate'" + "id='rate"+chk+chkr+"'>"+price+"</td>";
                    var tdm2 =  "<td class='text-right chk-total'" + "id='total"+chk+chkr+"'>"+total+"</td>";
                    var tdm3 =  "<td class='text-right "+"chk"+chk+chkr+"'><input type='checkbox' class='chk-box' id='"+chk+chkr+"'/></td>";
                    tr_ = tr_ + tdm1 + tdm2 + tdm3;
                    chkr = chkr + 1;
                }

                var td6 =  "<td class='text-left'></td>";
                var td7 =  "<td class='text-left'></td>";
                var td8 =  "<td class='text-left'></td>";
                tr_ =  tr_ + td6 + td7 + td8 + "</tr>";
                final_tr = final_tr + tr_;
                chk = chk + 1;
            }
            document.getElementById('tbody_1').innerHTML = final_tr;
            $(document).find('.chk-box').on('click', function(){
                if($(this).is(":checked")){
                    var element_id = $(this).attr('id');
                    var rate = $("#rate"+element_id).html();
                    var total = $("#total"+element_id).html();
                    alert("Rate: " + rate +"Total: " + total);
                }else{
                    $('.foo').attr('checked', false);
                }

            });
        },


    });
//
return {
    QuotationsButton: QuotationsButton
};

});