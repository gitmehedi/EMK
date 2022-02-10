$(function () {
    var dateformat = 'yy-mm-dd'

    $("#birth_date").datepicker({
        minDate: new Date(1900,1-1,1), maxDate: '-16Y',
        changeMonth: true,
        changeYear: true,
        yearRange: "-100:-15",
        dateFormat: dateformat
    });
    $('#birth_date').datepicker("option", "dateFormat", dateformat);

    $('#birth_date').change(function(){
     var currDate = $(this).val();
     if (currDate){
        var serverDate = new Date().getTime();
        var birthDate = new Date(currDate).getTime();
        if (birthDate >= serverDate){
            $(this).val('');
            alert('Birth Date should not greater than current date.');
            }
      }
    });


    $('#memberapp').validator();

    $('#website').change(function(){
        vals = $(this).val();
        msg = 'Please provide valid Website address.'
        if(!validateURL(vals,msg)){
            $(this).val('');
        }
    });

    $('#memberapp input').keyup(function() {
        var vals=['email','website'];
        if (vals.indexOf(this.name)<0){
            this.value = this.value.toLocaleUpperCase();
        }
    });

    $('input[name=subject_of_interest]').change(function(){
        vals= [];
        var selector = $('#subject_of_interest_others');
        $("input:checkbox[name=subject_of_interest]:checked").each(function(){
           vals.push($(this).parent().text().trim());
        });
        
        if(vals.indexOf('Other')>-1){
            selector.attr('required','required');
            selector.parent().show();
        }else{
            selector.val('').removeAttr('required');
            selector.parent().hide();
        }
        cbx_group = $("input[name=subject_of_interest]");

        cbx_group.prop('required', true);
        if(cbx_group.is(":checked")){
          cbx_group.prop('required', false);
        }
    });




    $('#highest_certification').change(function(){
        var val = $('#highest_certification option:selected').text().trim().toLowerCase();
        var selector = $('#highest_certification_other');
        if (val=="other"){
            selector.attr('required','required');
            selector.parent().show();
        }else{
            selector.val('').removeAttr('required');
            selector.parent().hide();
        }
    });

    $('#occupation').change(function(){
        var val = $('#occupation option:selected').text().trim().toLowerCase();
        var selector = $('#occupation_other');
        if (val=="other"){
            selector.attr('required','required');
            selector.parent().show();
        }else{
            selector.val('').removeAttr('required');
            selector.parent().hide();
        }
    });

    $('input[name=usa_work_or_study]').change(function(){
        var val = $("input:checked[name=usa_work_or_study]:checked").val();
        if (val=='yes'){
            $('#usa_work_or_study_place').attr('required','required').addClass('reqfield').parent().show();
        }else{
            $('#usa_work_or_study_place').removeAttr('required').removeClass('reqfield').val('').parent().hide();
        }
    });

    $('.img_select_layer').on('click', function() {
        $(this).siblings('input').click();
    });

    $("#signature-image-upload").change(function() {
        var validImg = validateFile(this,'signature_image');
        if (validImg==false){
            $(this).val(null);
            $(this).parent('.img_ctx').siblings('.warning').css('color','red');
        } else{
            $(this).parent('.img_ctx').siblings('.warning').css('color','black');
        }

    });

    $("#member-image-upload").change(function() {
        var validImg = validateFile(this,'member_image');
        if (validImg==false){
            $(this).val(null);
            $(this).parent('.img_ctx').siblings('.warning').css('color','red');
        } else{
            $(this).parent('.img_ctx').siblings('.warning').css('color','black');
        }

    });

    $("#email").change(function(){
        var email = $(this).val();
        var url=config.baseurl+"/page/checkemail";
        var data={'email': email}
        callAjax(url,data,'GET',validateEmail,this)
    })
    function validateEmail(responseData,self){
        if (responseData.email){
            $('#exits_email').text($(self).val())
            $(self).val('');
            $(self).next().show();
        }else{
            $('#exits_email').text('')
            $(self).next().hide();
        }
    }


//    $("#file").on('change',function(e){
//        var self = this;
//        if (self.files[0].size>207200){
//            alert('File size is larger than system accept.');
//            $(self).val('');
//        }
//    });
    var maxAttach=10;
    var attachNo=1;
    $('#createAttachment').on('click',function(e){
        e.preventDefault();
        var self = this;
        var val = true;

        $('.attachment').each(function(){
            if ($(this).val() ==''){
                val=false;
            }
        });

        if ( attachNo < maxAttach && val==true){
            $('#uploadtable').append('<tr><td><input type="file" class="attachment" accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,.pdf" name="attachment"/></td><td><a href="#" class="remove_field btn btn-danger btn-xs">Remove</a></td></tr>');
            attachNo++;
        }
    });
    $("#uploadtable").on("click",".remove_field", function(e) {
        e.preventDefault();
        $(this).closest('tr').remove();
        attachNo--;
    })
    });

    function validateFile(file,loc) {
      if (file.files && file.files[0]) {
        var extensions = ['jpg', 'gif', 'png'];
        var reader = new FileReader();
        var fileOrNot=false;
        if (file) {
            var get_ext = file.files[0]['name'].split('.').pop().toLowerCase();
            var iSize = (file.files[0].size / (1024 * 1024));
            if (($.inArray(get_ext, extensions) > -1)) {
                reader.onload = function(e) {
                    var img = new Image;
                    img.src = reader.result;
                    img.onload = function() {
                        if (loc=='member_image'){
                            if ((img.width<=200) && (img.height) <=200 && (iSize < 2)){
                                $('#'+loc).attr('src', e.target.result);
                                fileOrNot=true;
                            } else {
                                $('#'+loc).attr('src','');
                            }
                        }
                        if (loc=='signature_image'){
                            if ((img.width<=300) && (img.height <=80) && (iSize < .2)){
                                $('#'+loc).attr('src', e.target.result);
                                fileOrNot=true;
                            } else {
                                $('#'+loc).attr('src','');
                            }
                        }
                    };
                }
                reader.readAsDataURL(file.files[0]);
            }
        }
      }
    }

    function callAjax(url,data,method,callBack,event){
        var params ={
            url: url,
            method: method,
            data:data
        };
        $.ajax(params).done(function(responseData){
            callBack(JSON.parse(responseData),event);
        });
    }

