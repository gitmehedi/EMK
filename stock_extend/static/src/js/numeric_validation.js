//$('.o_datepicker_input').keypress(function(event) {
//    if(event.which < 46
//    || event.which > 59) {
//        event.preventDefault();
//    } // prevent if not number/dot
//
//    if(event.which == 46
//    && $(this).val().indexOf('.') != -1) {
//        event.preventDefault();
//    } // prevent if already dot
//});

var el = $('input[type="text"]');
el.prop("autocomplete",false); // remove autocomplete (optional)
el.on('keydown',function(e){
	var allowedKeyCodesArr = [9,96,97,98,99,100,101,102,103,104,105,48,49,50,51,52,53,54,55,56,57,8,37,39,109,189,46,110,190];  // allowed keys
	if($.inArray(e.keyCode,allowedKeyCodesArr) === -1 && (e.keyCode != 17 && e.keyCode != 86)){  // if event key is not in array and its not Ctrl+V (paste) return false;
		e.preventDefault();
	} else if($.trim($(this).val()).indexOf('.') > -1 && $.inArray(e.keyCode,[110,190]) != -1){  // if float decimal exists and key is not backspace return fasle;
		e.preventDefault();
	} else {
		return true;
	};  
}).on('paste',function(e){  // on paste
	var pastedTxt = e.originalEvent.clipboardData.getData('Text').replace(/[^0-9.]/g, '');  // get event text and filter out letter characters
	if($.isNumeric(pastedTxt)){  // if filtered value is numeric
		e.originalEvent.target.value = pastedTxt;
		e.preventDefault();
	} else {  // else 
		e.originalEvent.target.value = ""; // replace input with blank (optional)
		e.preventDefault();  // retur false
	};
});
openerp.stock_extend= function(instance, local) {
	var _t = instance.web._t, _lt = instance.web._lt;
	var QWeb = instance.web.qweb;
	var TestClass = instance.web.Class.extend({
		testMethod : function() {
			return "hello";
		},
	});

	console.log(new TestClass().testMethod());
}
