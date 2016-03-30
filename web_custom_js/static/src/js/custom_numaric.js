openerp.web_autonumaric = function(instance) {
	// module code goes here
	console.log('My module has been initialized');
	openerp.web.FormView.include({
		load_form: function(data)
		{
			var self = this;
			console.log('form_view_loaded');
			$(".autonumaric input").autoNumeric('init',{vMin: '0', lZero: 'deny'});
			$(".autonumaric").autoNumeric('init',{vMin: '0', lZero: 'deny'});
	        return self._super(data);
		},
	});
}
