// makes element visible or hidden and outputs a message, alongisde a success alert if requested
// responseId will NOT include # since this will interfere with some of our functions
function changeResponseAppearance(responseId, responseMessage='', alertSuccess=null) {
    if (responseMessage == '') {
        // if no error message, let's assume you want it hidden
        document.getElementById(responseId).style.visibility = 'hidden';
    }
    else {
        $(`#${responseId}`).html(`${responseMessage}`)
        document.getElementById(responseId).style.visibility = 'visible';
    }

    if (alertSuccess != null) {
        if (alertSuccess) {
            // change the item to .alert-success
            // remove .alert-danger
            $(`#${responseId}`).addClass('alert-success')
            $(`#${responseId}`).removeClass('alert-danger')
        }
        else {
            // change the item to .alert-danger
            // remove .alert-success
            $(`#${responseId}`).removeClass('alert-success')
            $(`#${responseId}`).addClass('alert-danger')
        }
    }
}

// changes the element to valid or invalid
function changeValidity(inputId, isValid='') {
    if (isValid) {
        $(`#${inputId}`).addClass('is-valid');
        $(`#${inputId}`).removeClass('is-invalid');
    }
    // if you submit nothing for isValid, then it wipes out all classes
    else if (isValid == '') {
        $(`#${inputId}`).removeClass('is-invalid');
        $(`#${inputId}`).removeClass('is-valid');
    }
    else {
        $(`#${inputId}`).addClass('is-invalid');
        $(`#${inputId}`).removeClass('is-valid');
    }    
}

// prevents keys not in the acceptable list regEx from being inputted
$(function filterKeys () {
    $("#file-name").keypress(function (e) {
        var keyCode = e.keyCode || e.which;
        
        document.getElementById("error-2").style.visibility = "hidden";
        
        //regEx for Valid Characters i.e. Alphabets and Numbers.
        var regEx = /^[A-Za-z0-9!@#$%&']+$/;
        
        key = String.fromCharCode(e.which)
        
        if (e.which == 32) {
            key = "Spaces " + "are"
        }
        else {
            key = "Key: " + key + " is"
        }
        
        //Validate TextBox value against the regEx.
        var isValid = regEx.test(String.fromCharCode(keyCode));
        if (!isValid) {
            changeResponseAppearance('error-2', `${key} not allowed`)
        }
        else {
            // less the second param which will hide the element
            changeResponseAppearance('error-2')
        }
        
        return isValid;
    });
});

// check if file-name is empty
document.getElementById("file-name").addEventListener("input", 
    function isFileNameEmpty() {

    const isEmpty = str => !str.trim().length;

        if (isEmpty(this.value)) {
            changeResponseAppearance('error-2', "A File Name is Required");
            changeValidity("file-name", false)
        } else {
            changeResponseAppearance('error-2');
            changeValidity("file-name", true)
        }
    }
);

document.getElementById("custom-start").addEventListener("keyup", compareTimes);
document.getElementById("custom-end").addEventListener("keyup", compareTimes);

// checks to make sure the customTimestamps start and end times are valid
function compareTimes() {
    var customStart = document.getElementById("custom-start").value;
    var customEnd = document.getElementById("custom-end").value;
    
    // start is less than end and both are not empty
    if (customStart != '' && customEnd != '' && parseInt(customStart) < parseInt(customEnd)){
        // hide error
        changeResponseAppearance('invalidTimes')
        changeValidity("custom-start", true)
        changeValidity("custom-end", true)
    }
    // if there is nothing inputted, just don't show an error or feedback
    else if (customStart == '' && customEnd == '') {
        changeResponseAppearance('invalidTimes')
        // if second arg is not sent, it will wipe out both feedbacks
        changeValidity("custom-start")
        changeValidity("custom-end")
    }
    // start is greater than or equal to end 
    else if (parseInt(customStart) >= parseInt(customEnd)) {
        // present error
        changeResponseAppearance('invalid-times', 'Start Time Must Be Before the End Time')

        // feedback invalid
        changeValidity("custom-start", false)
        changeValidity("custom-end", false)
    }       
}

var allFields = "#video-url, #file-name, #custom-start, #custom-end, #custom-timestamps-question";
var requiredFields = "#video-url, #file-name";
var optionalFields = "#custom-start, #custom-end"

$(allFields).on('change', function() {
    allFilled()
});

function allFilled() {
    partialValidation()
    .then(validUrl => {
        var filled = true;
        var optionalFilled = true;
        var totalFilled = true;
        
        $(requiredFields).each(function() {
            if ($(this).val() == '') {
                filled = false;
            }
        });
        
        customTimestamps = document.getElementById("custom-timestamps").checked;
        if (customTimestamps) {
            $(optionalFields).each(function() {
                if ($(this).val() == '') {
                    optionalFilled = false;
                }
            });
        }
    
        
    
        if (optionalFilled == false || filled == false || validUrl == false) {
            var totalFilled = false;
        }
        
        if (totalFilled) {
            $('#convert').removeClass('disabled');
            // code to remove all error codes
            // this is redundant?? you couldn't have errors and submit??
            changeResponseAppearance('error-1')
            changeResponseAppearance('error-2')
            changeResponseAppearance('submission-response')
        } else {
            $('#convert').addClass('disabled');
        }
    });
}

// enable the button if conditions are met
// is video URL valid


async function partialValidation () {
    url = document.getElementById("video-url").value;

    // no point in giving them an error message with no URL, they should know its an issue, 
    // or maybe this is bad UI/UX and  i should only activate it when the user specificly clicks on it and leaves it blank,
    // instead of the .onchange for the entire form
    if (url == ''){
        // remove any type of validation
        changeValidity("video-url")
        changeResponseAppearance('error-1')
        return
    }

    // get the partial validation of the URL, non-internet testing, just checks for formatting
    var validationResponse = await eel.partial_validation_python(url)();

    console.log(url)
    var validUrl = false;

    switch(validationResponse){
        case -2:
            // NonYoutubeLinkException
            // make the error visible and set its text
            changeResponseAppearance('error-1', "Only YouTube addresses are supported");
            break;

        case -1:
            // NonVideoLinkException
            // make the error visible and set its text
            changeResponseAppearance('error-1', "Only YouTube Shorts, Clips, and Videos are supported");
            break;

        case 0:
            // Valid Link
            validUrl = true;
            
            // hide the error
            changeResponseAppearance('error-1')
            break;

        case 1:
            // Unhandled Link Exception
            // make error visible and set its text
            changeResponseAppearance('error-1', "Unhandled Link Exception, please report to Dev Team")
            break;
    }


    console.log(validUrl)
    // change input to valid or invalid dependending on if the Url is valid
    changeValidity("video-url", validUrl)

    // return boolean
    return validUrl;
}

async function formSubmission() {
    // hide submission-response
    changeResponseAppearance('submission-response')

    var url = document.getElementById("video-url").value;
    var fileName = document.getElementById("file-name").value;
    
    var audioOnly = document.getElementById("audio-only").checked;

    var fileFormat = null;

    if (audioOnly) {
        // fileFormat == True means mp3 else wav
        fileFormat =  document.getElementById("mp3").checked;
    }


    var customTimestamps = document.getElementById("custom-timestamps").checked;
    
    var start = null;
    var end = null;

    if (customTimestamps) {
        start = document.getElementById("custom-start").value;
        end = document.getElementById("custom-end").value;
    }

    var responseCode = await eel.download_video(url, fileName, fileFormat, start, end)();

    switch(responseCode){
        case -2:
            changeResponseAppearance('submission-response', `The following link: ${url} returned a Non 200 Status Code. Please try again`, false)
            break;
        case -1:
            changeResponseAppearance('submission-response', `The YouTube video at: ${url} is unavailable. Check that your link is correct`, false)
            break;
        case 0:
            // this was a success so change accordingly
            changeResponseAppearance('submission-response', `File: ${fileName} successfully downloaded!`, true)         
            break;
        case 1:
            changeResponseAppearance('submission-response', `Unhandled download exception. Please log what you did submitted and send to the dev team`, false)
            break;
    }
}