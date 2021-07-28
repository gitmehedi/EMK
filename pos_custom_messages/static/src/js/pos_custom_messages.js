odoo.define('pos_custom_messages.pos_custom_messages', function(require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    
    var CustomMessagePopup = PopupWidget.extend({
        template: 'CustomMessagePopup'
    });
    gui.define_popup({ name: 'custom_message', widget: CustomMessagePopup });

    return {
        CustomMessagePopup: CustomMessagePopup,
    };
});
