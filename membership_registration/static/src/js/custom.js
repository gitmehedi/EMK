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

        if (quotaVal){
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

function readURL(input) {

  if (input.files && input.files[0]) {
    var reader = new FileReader();

    reader.onload = function(e) {
      $('#uploaded_image').attr('src', e.target.result);
    }

    reader.readAsDataURL(input.files[0]);
  }
}


