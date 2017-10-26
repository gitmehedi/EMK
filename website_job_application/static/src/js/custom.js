$(function () {
    var dateformat = 'yy-mm-dd'
    $("#datepicker").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: dateformat
    });
    $("#datepicker").datepicker("option", "dateFormat", dateformat);

    $("#datepicker_challan").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: dateformat
    });
    $('#datepicker_challan').datepicker("option", "dateFormat", dateformat);
});