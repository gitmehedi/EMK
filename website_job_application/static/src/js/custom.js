$(function () {
    var dateformat = 'yy-mm-dd'
    $("#datepicker").datepicker({
        dateFormat: dateformat
    });
    $("#datepicker").datepicker("option", "dateFormat", dateformat);

    $("#datepicker_challan").datepicker({
        dateFormat: dateformat
    });
    $('#datepicker_challan').datepicker("option", "dateFormat", dateformat);
});