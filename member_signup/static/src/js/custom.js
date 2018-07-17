$(function () {
    var dateformat = 'yy-mm-dd'

    $("#birthdate_date").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: dateformat
    });
    $('#birthdate_date').datepicker("option", "dateFormat", dateformat);

    $("#date_of_signature").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: dateformat
    });
    $('#date_of_signature').datepicker("option", "dateFormat", dateformat);

    $('.member_image_layer').on('click', function() {
        $('#member-image-upload').click();
    });

    $("#member-image-upload").change(function() {
        readURL(this,'member_image');
    });

    $('.signature_image_layer').on('click', function() {
        $('#signature-image-upload').click();
    });

    $("#signature-image-upload").change(function() {
        readURL(this,'signature_image');
    });
});

function readURL(input,loc) {

  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#'+loc).attr('src', e.target.result);
    }
    reader.readAsDataURL(input.files[0]);
  }
}


