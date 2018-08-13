$(function()
{
    $(document).on("keydown", '.number', function(e) {
        var key = e.charCode || e.keyCode || 0;
        // allow backspace, tab, delete, arrows, numbers and keypad numbers ONLY
        return (
                key == 8 ||
                key == 9 ||
                key == 46 ||
                key == 110 ||
                key == 190 ||
                (key >= 37 && key <= 40) ||
                (key >= 48 && key <= 57) ||
                (key >= 96 && key <= 105))
                ;
    });
    /*  =================== This part written by Md. Mehedi Hasan ======================*/

    /**
     * limit the number of digits where only 11 digits are allowed in a text field
     */

    $(document).on('keyup', '.limitClass9', function() {
        var limit11 = $(this).val();
        if (limit11.length > 9)
        {
            var digits11 = $(this).val().slice(0, 9);
            $(this).val(digits11);
            return false;
        }
    });
    /**
     * limit the number of digits where only 5 digits are allowed in a text field
     */

    $(document).on('keyup', '.limitClass5', function() {
        var limit5 = $(this).val();
        if (limit5.length > 7)
        {
            var digits5 = $(this).val().slice(0, 7);
            $(this).val(digits5);
            return false;
        }
    });
    // Delete Button in Edit Mode

    $(".amount").each(function(index) {
        var id = $(this).attr("id");
        var amount;
        $(this).blur(function() {
            if ($(this).val() == "" || $(this).val() == ".00") {
                $(this).val("0.00");
            } else {
                amount = utils.formatNumber($(this).val(), 'FLOAT');
                amount = amount.toFixed(2);
                $(this).val(amount);
            }
        });
        $(this).focus(function() {
            if ($(this).val() == "0.00") {
                $(this).val(".00");
                utils.setCaretToPos(this, 0);
            }
        });
        $(this).keyup(function() {
            var length = $(this).length;
            // Validation need to done
            // Check length
            // Check pos(.)
        });
    });
    $(".integer").each(function(index) {
        var id = $(this).attr("id");
        var amount;
        $("#" + id).blur(function() {
            if ($(this).val() == "") {
                $(this).val("0");
            } else {
                amount = utils.formatNumber($(this).val(), 'INT');
                $(this).val(amount);
            }
        });
        $("#" + id).focus(function() {
            if ($(this).val() == "0") {
                $(this).val("");
            }
        });
    });
    $('.invalidfile').change(function() {
        var id = $(this).attr("id");
        var file = $('input[type="file"]').val();
        var exts = ['jpg', 'gif', 'png'];
        if (file) {
            var get_ext = file.split('.');
            get_ext = get_ext.reverse();
            var iSize = ($("#" + id)[0].files[0].size / (1024 * 1024));
            if (($.inArray(get_ext[0].toLowerCase(), exts) > -1) && (iSize < 2)) {
                if (id == 'photo') {
                    utils.PreviewImage();
                }
                return true;
            } else {
              if (id == 'photo') {
                    $("#uploadPreview").find("img").remove();
                }
                $("#dialog-confirm").dialog({
                    title: "Sorry! upload jpg, png or gif file (2MB limit)",
                    autoOpen: true,
                    resizable: false,
                    height: 140,
                    modal: true,
                    show: 'fade',
                    create: function(event, ui)
                    {
                        $(this).parent(".ui-dialog:first").addClass('dialoge-shadow');
                        $(this).parent(".ui-dialog:first").find(".ui-dialog-titlebar").addClass('dialoge-header');
                        $(this).parent(".ui-dialog:first").find(".ui-dialog-buttonpane").addClass('dialoge-footer');
                        $(this).parent(".ui-dialog:first").find(".ui-dialog-content").addClass('ui-widget-content-dialog');
                        $(this).parent(".ui-dialog:first").find(".ui-dialog-titlebar .ui-dialog-titlebar-close").css("display", "none");
                    },
                    buttons: [
                        {
                            text: "OK",
                            "class": 'btn dialog-delete_confirm-btn btn-hossbrag margin-right-05',
                            click: function() {
                                $(this).dialog("close");
                            }
                        }
                    ]

                });
                $('#' + id).val('');
                return false;
            }
        }
    });


    $(document).on("change", '.input_start_year_edit', function() {
        var sYear = $(this).val();
        var eYear = $(this).closest('.control-group ').next().next().find('input').val();
        var eMonth = $(this).closest('.control-group').next().next().find('select').val();
        if (eYear != "" || eMonth != "") {
            $(this).closest('.control-group ').next().next().find('input').val('');
            $(this).closest('.control-group ').next().next().find('select').val('');
        }
    });

    $(document).on("change", '.start_month_edit', function() {
        var sMonth = $(this).val();
        var eYear = $(this).closest('.control-group ').next().next().next().find('input').val();
        var eMonth = $(this).closest('.control-group').next().next().next().find('select').val();
        if (eYear != "" || eMonth != "") {
            $(this).closest('.control-group ').next().next().next().find('input').val("");
            $(this).closest('.control-group').next().next().next().find('select').val("");
        }
    });

    $(document).on("change", '.input_end_year_edit', function() {
        var sYear = $(this).closest('.control-group').prev().prev().find('input').val();
        var sMonth = $(this).closest('.control-group').prev().prev().prev().find('select').val();
        var eMonth = $(this).closest('.control-group').find('select').val();
        var eYear = $(this).val();
        if (sYear == "" || sMonth == "") {
            $(this).val('');
        } else {
            var ckYearMonth = utils.yearValidate(sYear, eYear, sMonth, eMonth);
            if (ckYearMonth) {
                return true;
            } else {
                $(this).val('');
            }
        }
    });

    $(document).on("change", '.end_month_edit', function() {
        var sYear = $(this).closest('.control-group').prev().prev().find('input').val();
        var sMonth = $(this).closest('.control-group').prev().prev().prev().find('select').val();
        var eMonth = $(this).val();
        var eYear = $(this).closest('.control-group').find('input').val();
        if (sYear == "" || sMonth == "") {
            $(this).val('');
        } else if (eYear == "") {
            return true;
        } else {
            var ckYearMonth = utils.yearValidate(sYear, eYear, sMonth, eMonth);
            if (ckYearMonth) {
            } else {
                $(this).val('');
            }
        }
    });

    $(document).on("change", '.dateLimitYear', function() {
        var inputYear = $(this).val();
        var currentYear = (new Date).getFullYear();
        var year = currentYear.toString();
        if (inputYear > year) {
            $(this).val("");
        }
    });
});

function ucFirstAllWords(str)
{
    var pieces = str.split(" ");
    for (var i = 0; i < pieces.length; i++)
    {
        var j = pieces[i].charAt(0).toUpperCase();
        pieces[i] = j + pieces[i].substr(1);
    }
    return pieces.join(" ");
}

function redirect(url) {
    document.location.href = baseUrl + "/" + url;
}



function ajaxRequest(url, data, callBack)
{
    $.ajax({
        url: url,
        type: "POST",
        context: document.body,
        data: data
    }).done
            (function(responseData)
            {
                callBack(responseData);
            });
}
function showFormError(id)
{
    $('#' + id).addClass('error');
    $('#' + id).focus();
    $("div.alert-error").html('Required Field is empty.');
    $("div.alert-error").show();
    return false;
}
function getTodaysDate()
{
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1; //January is 0!

    var yyyy = today.getFullYear();
    if (dd < 10)
    {
        dd = '0' + dd
    }
    if (mm < 10)
    {
        mm = '0' + mm
    }
    var currentDate = yyyy + '-' + mm + '-' + dd;
    return currentDate;
}

var utils = {
    disableSelectBox: function(selectBoxId)
    {
        $('select#' + selectBoxId + ' option:not(:selected)').attr('disabled', true);
    },
    enableSelectBox: function(selectBoxId)
    {
        $('select#' + selectBoxId + ' option').attr('disabled', false);
    },
    addReadOnlyToInput: function(inputId, req)
    {
        $('#' + inputId).attr({
            readonly: 'readonly',
            tabindex: '-1'
        })
        if (req == 0)
        {
            this.removeRequiredClassToInput(inputId);
        }
    },
    removeReadOnlyToInput: function(inputId, req)
    {
        $('#' + inputId).removeAttr('readonly');
        $('#' + inputId).removeAttr('tabindex');
        if (req == 1)
        {
            this.addRequiredClassToInput(inputId);
        }
    },
    addRequiredClassToInput: function(id) {
        $('#' + id).addClass('required');
        $('#' + id).closest('div.control-group').find('label').addClass('required');
    },
    removeRequiredClassToInput: function(id) {
        $('#' + id).removeClass('required');
        $('#' + id).closest('div.control-group').find('label').removeClass('required');
    },
    checkToDate: function(date)
    {
        if (date == '0000-00-00')
        {
            var to_date = '';
        }
        else
        {
            to_date = date;
        }
        return to_date;
    },
    getTodaysDate: function()
    {
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth() + 1; //January is 0!

        var yyyy = today.getFullYear();
        if (dd < 10)
        {
            dd = '0' + dd
        }
        if (mm < 10)
        {
            mm = '0' + mm
        }
        var currentDate = yyyy + '-' + mm + '-' + dd;
        return currentDate;
    },
    gotoTop: function()
    {
        $('html, body').animate({
            scrollTop: 0
        }, 'slow');
    },
    ucFirstAllWords: function(str)
    {
        var pieces = str.split(" ");
        for (var i = 0; i < pieces.length; i++)
        {
            var j = pieces[i].charAt(0).toUpperCase();
            pieces[i] = j + pieces[i].substr(1);
        }
        return pieces.join(" ");
    },
    hideAllErrorMessage: function()
    {
        $('div.alert-error').hide();
        $('div.alert-success').hide();
    },
    validateForm: function(formId)
    {
        $('#' + formId).validate({
            highlight: function(element, errorClass) {
                $(element).addClass('ui-state-error');
            },
            errorPlacement: function(error, element) {
                return true;
            },
            unhighlight: function(element, errorClass) {
                $(element).removeClass('ui-state-error');
            }
        });

    },
    checkForValidation: function() {

    },
    sumOfColumns: function(tableID, className) {
        var sum = 0;
        $('#' + tableID + " tbody input." + className).each(function() {
            if ($(this).is(":visible")) {
                if (!isNaN(this.value) && this.value.length != 0) {
                    sum += parseFloat(this.value);
                }
            }
        });
        return sum;
    },
    ajaxFormValidation: function(data)
    {
        utils.hideAllErrorMessage();
        var className = '';
        var flag = 0;
        if (data == '0')
        {
            $('.alert-error').html('Failed');
            $('.alert-error').show();
            return flag;
        }
        if (data != '')
        {
            var message = '';
            var j = 0;
            for (var i in data)
            {
                var innerObj = data[i];
                if (i == 'success')
                {
                    className = '.alert-success';
                    flag = 1;
                    for (j in innerObj)
                    {
                        message += innerObj[j] + '<br />';
                    }
                }
                else
                {
                    className = '.alert-error';
                    flag = 0;
                    for (j in innerObj)
                    {
                        message += i + ' : ' + innerObj[j] + '<br />';
                    }
                }
            }
            if (message != '')
            {
                $(className).html(message);
                $(className).show();
            }
            return flag;
        }

    },
    set_min_max_date: function(obj) {
        var data = 'fiscal_year_id=' + $(obj).val();
        $('.loading').show();
        $.ajax({
            url: serverUrl + '/app/ajaxfiscalyear/',
            type: "POST",
            data: data,
            cache: false,
            success: function(html) {
                $('#ajaxminmaxplaceholder').html(html);
                var currentFyStart = $('#selected_fiscal_year_start_date').text();
                utils.changeFromTo(currentFyStart);
            }
        });
    },
    set_min_max_date1: function(obj) {
        var data = 'fiscal_year_id=' + $(obj).val();
        $('.loading').show();
        $.ajax({
            url: serverUrl + '/app/ajaxfiscalyear/',
            type: "POST",
            data: data,
            cache: false,
            success: function(html) {
                $('#ajaxminmaxplaceholder').html(html);
                var currentFyStart = $('#selected_fiscal_year_start_date').text();
                //                utils.changeFromTo(currentFyStart);
            }
        });
    },
    changeFromTo: function(dateObj)
    {
        if (dateObj.length > 0)
        {
            var c_date = new Date(dateObj);
            var c_year = c_date.getFullYear();
            var c_month = c_date.getMonth() + 1;
            var start = null;
            var end = null;
            if (c_month > 6)
            {
                start = c_year + "-07-01";
                end = c_year + "-12-31";
            }
            else if (c_month <= 6)
            {
                start = c_year + "-01-01";
                end = c_year + "-06-30";
            }
            $('#from_date').val(start);
            $('#to_date').val(end);
        }
    },
    resetErrorsOnAllForms: function()
    {
        $('.alert').hide();
        for (var i = 0, j = arguments.length; i < j; i++)
        {
            if (arguments[i] == null || arguments[i] == '')
            {
                continue;
            }
            var validator = $('#' + arguments[i]).validate();
            validator.resetForm();
        }
    },
    clearForm: function(formId)
    {
        var validator = $("#" + formId).validate();
        $('.alert').hide();
        validator.resetForm();
    },
    /**
     * Increase particular number of day to a specific date.
     * @specDate:
     * @fieldId : input field Id , where jqury UI date picker will be applied.
     * @inc : number of days that will added to the specDate
     */
    increaseDay: function(specDate, fieldId, inc)
    {
        var date = new Date(specDate);
        var d = date.getDate();
        var m = date.getMonth();
        var y = date.getFullYear();
        var newDate = new Date(y, m, d + inc);
        if (specDate != '')
        {
            $('#' + fieldId).datepicker({
                minDate: newDate,
                dateFormat: 'yy-mm-dd',
                changeMonth: true,
                changeYear: true
            });
        }
    },
    clearInput: function(id, event, animalImg)
    {
        utils.clearForm(id);
        if ($('#' + id + ' input.generated_code').length) {
        } else {
            $('#' + id + ' input[type="text"]').val('');
        }
        if ($('#' + id + ' input.amount').length) {
            $('#' + id + ' input.amount').val('0.00')
        } else if ($('#' + id + ' input.number').length) {
            $('#' + id + ' input.number').val('0')
        }

        $('#' + id + ' input[type="checkbox"]').checked = false;
        $('#' + id + ' input[type="password"]').val('');
        $('#' + id + ' select').val('');
        $('#' + id + ' textarea').val('');
        var boxes = document.getElementsByTagName('input');
        for (i = 0; i < boxes.length; i++) {
            if (boxes[i].type == 'checkbox')
                boxes[i].checked = false;
            if (boxes[i].type == 'radio')
                boxes[i].checked = false;
        }


        $('#' + id + ' input[type="file"]').val('');
        if (animalImg != undefined && animalImg != '' && animalImg != null)
        {
            $('#' + id + ' img.preview_img').attr('src', serverUrl + '/img/' + animalImg);
        }
        event.preventDefault();
        event.stopPropagation();
    },
    /**
     * For print Report
     * @param string div_id The container div id, which innerHtml will be printed.
     */
    printContent: function(div_id) {
        var innercontent = $('#' + div_id).html();
        var HeaderContainer = document.getElementById("printheader");
        var headercontent = HeaderContainer.innerHTML;
        var html = '<html><head><title></title>' +
                '<link href="' + serverUrl + '/css/bootstrap.css" rel="stylesheet" type="text/css" />' +
                '</head><body style="background:#ffffff;">' + headercontent +
                innercontent +
                '</body></html>';
        var WindowObject = window.open("", "PrintWindow",
                "width=750,height=650,top=50,left=50");
        WindowObject.document.writeln(html);
        WindowObject.document.close();
        WindowObject.focus();
        WindowObject.print();
        WindowObject.close();
    },
    formatNumber: function(nval, ntype) {
        var return_value;
        var nvalue;
        if (nval == "") {
            nvalue = 0;
        } else {
            switch (ntype) {
                case 'FLOAT':
                    nvalue = parseFloat(nval);
                    break;
                case 'INT':
                    nvalue = parseInt(nval, 10);
                    break;
                default:
                    nvalue = parseFloat(nval);
                    break;
            }
        }

        if (typeof nvalue == 'number') {
            return_value = nvalue;
        } else {
            return_value = parseInt(nvalue, 10);
        }
        return return_value;
    },
    checkDateDiff: function(start, end, message, inc)
    {
        var incVal = (typeof(inc) === "undefined") ? 0 : inc;
        var diff = incVal * 86400000;
        var firstDate = $('#' + start).val(),
                first = new Date(firstDate).getTime();
        var secondTime = $('#' + end).val(),
                second = new Date(secondTime).getTime();
        if ((second - first) >= diff)
        {
            return false;
        }
        else if ((second - first) < diff)
        {
            alert(message);
            $('#' + end).val('');
            return true;
        }

    },
    destroyDatepicker: function(id)
    {
        alert(id);
        $('#' + id).datepicker('destroy');
    },
    setSelectionRange: function(input, selectionStart, selectionEnd) {
        if (input.setSelectionRange) {
            input.focus();
            input.setSelectionRange(selectionStart, selectionEnd);
        }
        else if (input.createTextRange) {
            var range = input.createTextRange();
            range.collapse(true);
            range.moveEnd('character', selectionEnd);
            range.moveStart('character', selectionStart);
            range.select();
        }
    },
    setCaretToPos: function(input, pos) {
        utils.setSelectionRange(input, pos, pos);
    },
    countChar: function(val, MaxChar, showId) {
        var len = $(val).val().length;
        if (len > MaxChar) {
            val.value = val.value.substring(0, MaxChar);
        } else {
            $('#' + showId).text(MaxChar - len);
        }
    },
    countCharClass: function(val, MaxChar, showId) {
        var getID = $(val).attr("id");
        var id = getID.split("_");
        var len = $(val).val().length;
        if (len > MaxChar) {
            val.value = val.value.substring(0, MaxChar);
        } else {
            $('#' + showId + "_" + id[1]).text(MaxChar - len);
        }
    },
    PreviewImage: function() {

        if (window.File && window.FileReader && window.FileList && window.Blob) {
            oFReader = new FileReader();
            oFReader.readAsDataURL(document.getElementById("photo").files[0]);
            oFReader.onload = function(oFREvent) {
                document.getElementById("uploadPreview").innerHTML = '<img class="newsFeedPreview" src="' + oFREvent.target.result + '">';
            };
        }
    },
    yearValidate: function(sYear, eYear, sMonth, eMonth) {
        var sYear = parseInt(sYear, 10);
        var eYear = parseInt(eYear, 10);
        var sMonth = parseInt(sMonth, 10);
        var eMonth = parseInt(eMonth, 10);
        if (sYear === eYear) {
            if (eMonth > sMonth) {
                return true;
            } else {
                return false;
            }
        } else if (sYear > eYear) {
            return false;
        } else {
            return true;
        }
    }


};
var commonMessages = {
    success: "Information Inserted Successfully.",
}

var dialogMessage = {
    success: function(commonMessages) {
        $("#dialog-confirm_image").text(commonMessages);
        $("#dialog-confirm_image").addClass('dialoge-header');
        $("#dialog-confirm_image").dialog({
            autoOpen: true,
            resizable: false,
            height: 140,
            modal: true,
            show: 'fade',
            create: function(event, ui)
            {
                //here we can apply unique styling
                $(this).parent(".ui-dialog:first").addClass('dialoge-shadow');
                $(this).parent(".ui-dialog:first").find(".ui-dialog-titlebar").addClass('dialoge-header');
                $(this).parent(".ui-dialog:first").find(".ui-dialog-buttonpane").addClass('dialoge-footer');
                $(this).parent(".ui-dialog:first").find(".ui-dialog-content").addClass('ui-widget-content-dialog');
                $(this).parent(".ui-dialog:first").find(".ui-dialog-titlebar ").css("display", "none");
            },
            buttons: [
                {
                    text: "OK",
                    "class": 'btn dialog-delete_confirm-btn btn-hossbrag margin-right-05',
                    click: function() {
                        $(this).dialog("close");
                    }
                }
            ]

        });
    }
};
var countryStateCity = {
    changeState: function(responseData, state) {

        var select = "<option value=''>State</option>";
        var data = responseData.response;
        if (data) {
            for (var i in data) {
                select += "<option value='" + data[i].id + "'>" + data[i].name + "</option>";
            }
        }
        $('#' + state).empty().append(select);
    },
    changeCity: function(responseData, city) {
        var select = "<option value=''>City</option>";
        var data = responseData.response;
        if (data) {
            for (var i in data) {
                select += "<option value='" + data[i].id + "'>" + data[i].name + "</option>";
            }
        }
        $('#' + city).empty().append(select);
    },
    changeCityByCountry: function(responseData, city) {
        var select = "<option value=''>City</option>";
        var data = responseData.response;
        if (data) {
            for (var i in data) {
                select += "<option value='" + data[i].id + "'>" + data[i].name + "</option>";
            }
        }
        $('#' + city).empty().append(select);
    },
};




