$(function () {
    var dateformat = 'yy-mm-dd'

    $("#birthdate").datepicker({
        changeMonth: true,
        changeYear: true,
        dateFormat: dateformat
    });
    $('#birthdate').datepicker("option", "dateFormat", dateformat);

    $('#birthdate').change(function(){
     currDate = $(this).val();
     if (currDate){
        serverDate = new Date().toLocaleDateString();
        birthDate = new Date(currDate).toLocaleDateString();
        if (birthDate > serverDate){
            $(this).val('');
            alert('Birth Date should not greater than current date.');
        }
        }
    });

//    $('#login').change(function(){
//        vals = $(this).val();
//        msg = 'Please provide valid email.'
//        if (!validateEmail(vals,msg)){
//            $(this).val('');
//        }
//    });

    $('#website').change(function(){
        vals = $(this).val();
        msg = 'Please provide valid Website address.'
        if(!validateURL(vals,msg)){
            $(this).val('');
        }
    });

    $('input[name=subject_of_interest]').change(function(){
        vals= [];
        $("input:checkbox[name=subject_of_interest]:checked").each(function(){
            vals.push($(this).val());
        });

        if(vals.indexOf('other')>-1){
            $('#subject_of_interest_others').parent().show();
        }else{
            $('#subject_of_interest_others').val('');
            $('#subject_of_interest_others').parent().hide();
        }
    });



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

    function validateEmail(email,msg) {
        var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        if (!re.test(String(email).toLowerCase())){
            alert(msg)
            return false;
        }
        return true;
    }

    function validateURL(url,msg){
        var re = /^(http[s]?:\/\/){0,1}(www\.){0,1}[a-zA-Z0-9\.\-]+\.[a-zA-Z]{2,5}[\.]{0,1}/;
        if (!re.test(url)) {
            alert(msg);
            return false;
        }
        return true;
    }

