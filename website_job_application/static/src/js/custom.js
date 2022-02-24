$(function () {
    $('#datepicker').val()
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

    $('#quota').change(function(){
        var quotaVal = $('#quota').val();

        if (quotaVal != 'no_quota'){
            $('#quota_table').show();
        }else{
            $('#quota_table').hide();
        }
    });

    $('.img__description_layer').on('click', function() {
        $('#uploaded_image').click();
    });

    $('#uploaded_image').on('click', function() {
        $('#profile-image-upload').click();
    });

    $("#profile-image-upload").change(function() {
        readURL(this);
    });



});
