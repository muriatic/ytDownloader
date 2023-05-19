var invalid_key;
var no_file_name;

$(function () {
    $("#fileName").keypress(function (e) {
        var keyCode = e.keyCode || e.which;
        
        $("#lblError").addClass('d-none')
        
        //Regex for Valid Characters i.e. Alphabets and Numbers.
        var regex = /^[A-Za-z0-9!@#$%&']+$/;
        
        key = String.fromCharCode(e.which)
        
        invalid_key = false;
        
        if (e.which == 32) {
            key = "Space "
        }
        else {
            key = "Key: " + key
        }
        
        //Validate TextBox value against the Regex.
        var isValid = regex.test(String.fromCharCode(keyCode));
        if (!isValid) {
            $("#error1").html(key + " is not allowed");
            $("#error1").removeClass('d-none');
            invalid_key = true;
        }
        
        return isValid;
    });
});

// check if fileName is empty

const isEmpty = str => !str.trim().length;

document.getElementById("fileName").addEventListener("input", function() {
    if (isEmpty(this.value)) {

        $("#error1").html("A File Name is Required");
        $("#error1").removeClass('d-none')
        no_file_name = true;
    } else {
        $("#error1").addClass('d-none')
        $("#error1").addClass('d-none')
        no_file_name = false;
    }
});

// is there a fileName?


document.getElementById("custom_start").addEventListener("keyup", compareTimes);
document.getElementById("custom_end").addEventListener("keyup", compareTimes);

var invalid_times;

function compareTimes() {
    var input1 = document.getElementById("custom_start");
    var input2 = document.getElementById("custom_end");
    
    if (input1.value != '' && input2.value != '' && input1.value >= input2.value){
        $("#invalidTimes").removeClass('d-none')
        invalid_times = true;
    }
    else {
        $("#invalidTimes").addClass('d-none')
        invalid_key = false;
    }       
}

var fields = "#videoURL, #fileName, #custom_start, #custom_end, #custom_timestamps_question";
var req_fields = "#videoURL, #fileName";
var optional_fields = "#custom_start, #custom_end"

$(fields).on('change', function() {
    var test = allFilled()
    // .then(enableConvert => {
    //     convertEnabled= enableConvert;
    //     console.log(convertEnabled)
    //     if (convertEnabled) {
    //         $('#convert').removeClass('disabled');
    //     } else {
    //         $('#convert').addClass('disabled');
    //     }
    // });
});
// are customtimestamps filled in and start is less than end

function allFilled() {

    let valid_URL
    loc_partial_validation()
    .then(result => {
        valid_URL = result;
        console.log(valid_URL);
    });

    console.log(valid_URL);

    var filled = true;
    var optional_filled = true;
    var total_filled = true;
    
    $(req_fields).each(function() {
        if ($(this).val() == '') {
            filled = false;
        }
    });
    
    if (customtimestamps) {
        $(optional_fields).each(function() {
            if ($(this).val() == '') {
                optional_filled = false;
            }
        });
    }

    

    if (optional_filled == false || filled == false || valid_URL == false) {
        var total_filled = false;
    }

    console.log(valid_URL)
    return total_filled
}

// enable the button if conditions are met
// is video URL valid

// document.getElementById("videoURL").addEventListener("keyup", loc_partial_validation)

async function loc_partial_validation () {
    url = document.getElementById("videoURL").value;

    var log = await eel.partial_validation(url)();

    var message;

    var valid_URL;

    switch(log){
        case -2:
            message = 'NonYoutubeLinkException';
            valid_URL = false;
            break;

        case -1:
            message = 'NonVideoLinkException';
            valid_URL = false;
            break;

        case 0:
            message = 'Valid Link'
            valid_URL = true;
            break;

        case 1:
            message = 'Unhandled Link Exception'
            valid_URL = false;
            break;
    }

    return valid_URL;
}