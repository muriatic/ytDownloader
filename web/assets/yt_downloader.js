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
            $("#error2").html(key + " is not allowed");
            $("#error2").removeClass('d-none');
            invalid_key = true;
        }
        
        return isValid;
    });
});

// check if fileName is empty

const isEmpty = str => !str.trim().length;

document.getElementById("fileName").addEventListener("input", function() {
    if (isEmpty(this.value)) {

        $("#error2").html("A File Name is Required");
        $("#error2").removeClass('d-none')
        no_file_name = true;
    } else {
        $("#error2").addClass('d-none')
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
    allFilled()
    // console.log(test)
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
    partial_validation()
    .then(result => {
        valid_URL = result;
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
        
        if (total_filled) {
            $('#convert').removeClass('disabled');
            // code to remove all error codes
            $('#error1').addClass('d-none')
            $('#error2').addClass('d-none')
            $('#submissionError').addClass('d-none')
        } else {
            $('#convert').addClass('disabled');
        }

    });
}

// enable the button if conditions are met
// is video URL valid

// document.getElementById("videoURL").addEventListener("keyup", loc_partial_validation)

async function partial_validation () {
    url = document.getElementById("videoURL").value;

    if (url == ''){
        return 
    }

    var log = await eel.partial_validation(url)();

    var message;

    var valid_URL;

    switch(log){
        case -2:
            message = 'NonYoutubeLinkException';
            valid_URL = false;
            $("#error1").html("Only YouTube addresses are supported");
            $("#error1").removeClass('d-none')
        no_file_name = false;
            break;

        case -1:
            message = 'NonVideoLinkException';
            valid_URL = false;
            $("#error1").html("Only YouTube Shorts, Clips, and Videos are supported");
            $("#error1").removeClass('d-none')
            break;

        case 0:
            message = 'Valid Link'
            valid_URL = true;
            $("#error1").addClass('d-none')
            break;

        case 1:
            message = 'Unhandled Link Exception'
            valid_URL = false;
            $("#error1").html("Unhandled Link Exception, please report to Dev Team");
            $("#error1").removeClass('d-none')
            break;
    }

    return valid_URL;
}

async function formSubmission() {
    $("successMessage").addClass('d-none')

    var url = document.getElementById("videoURL").value;
    var fileName = document.getElementById("fileName").value;
    
    var audio_only = document.getElementById("audioOnlyTrue").checked;

    var fileFormat = null;
    if (audio_only) {
        fileFormat =  document.getElementById("mp3").checked;
    }


    var customTimestamps = document.getElementById("customTimeStamps").checked;
    
    var start = null;
    var end = null;

    if (customTimestamps) {
        start = document.getElementById("custom_start").value;
        end = document.getElementById("custom_end").value;
    }

    var response_code = await eel.download_video(url, fileName, audio_only, fileFormat, start, end)();

    console.log(response_code)

    switch(response_code){
        case -2:
            $("#submissionError").html(`The following link: ${url} returned a Non 200 Status Code. Please try again`);
            $("#submissionError").removeClass('d-none')
            break;
        case -1:
            $("#submissionError").html(`The YouTube video at: ${url} is unavailable. Check that your link is correct`);
            $("#submissionError").removeClass('d-none')
            break;
        case 0:
            $("#submissionError").addClass('d-none')
            $("#successMessage").html(`File: ${fileName} successfully downloaded!`)
            $("#successMessage").removeClass('d-none')
            break;
        case 1:
            $("#submissionError").html(`Unhandled download exception. Please log what you did submitted and send to the dev team`);
            $("#submissionError").removeClass('d-none')
            break;
    }



}