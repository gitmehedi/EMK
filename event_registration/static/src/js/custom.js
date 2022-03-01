$(function () {
    var dateformat = 'yy-mm-dd'

    $("#start_date,#end_date,#last_date_reg,#date_of_payment").datepicker({
        minDate: '+1D',
        maxDate: new Date(2050,12,31),
        changeMonth: true,
        changeYear: true,
        dateFormat: 'yy-mm-dd'
    });

    $('#start_date,#end_date,#last_date_reg,#date_of_payment').datepicker("option", "dateFormat", dateformat);

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

    $('#end_date').change(function(){
    var endDate = $(this).val();
    var startDate = $('#start_date').val();
    if (start_date > endDate){
        $(this).val('');
        alert('Start Date should not greater than End date.');
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
});