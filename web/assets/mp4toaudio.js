async function getFolder() {
    var file_path = await eel.get_file_path()();
    if (file_path) {
        $('#selectedFile').html(file_path)
        $('#convertToMP3').removeClass('disabled')
        $('#convertToWAV').removeClass('disabled')
    }
    else {
        $('#convertToMP3').addClass('disabled')
        $('#convertToWAV').addClass('disabled')
    }
}

// need to add function to make sure a non MP4 file isnt selected;; some .onchange thing

async function convertToMP3() {
    $("#Message").addClass('d-none')
    $("#Message").removeClass('alert-success')
    $("#Message").removeClass('alert-danger')
    var filePath = document.getElementById("selectedFile").innerHTML;

    var responseCode = await eel.convert_file(filePath, '.mp3')();

    switch(responseCode) {
        case 0:
            $("#Message").html(`File successfully converted!`);
            $("#Message").removeClass('d-none');
            $("#Message").addClass('alert-success');
            break;
        case -1:            
            $("#Message").html(`File unsuccessfully converted. Try again`);
            $("#Message").removeClass('d-none');
            $("#Message").addClass('alert-danger');
            break;
    }
}

async function convertToWAV() {
    $("#Message").addClass('d-none')
    $("#Message").removeClass('alert-success')
    $("#Message").removeClass('alert-danger')
    var filePath = document.getElementById("selectedFile").innerHTML;

    var responseCode = await eel.convert_file(filePath, '.wav')();

    switch(responseCode) {
        case 0:
            $("#Message").html(`File successfully converted!`)
            $("#Message").removeClass('d-none')
            $("#Message").addClass('alert-success')
            break;
        case -1:            
            $("#Message").html(`File unsuccessfully converted. Try again`)
            $("#Message").removeClass('d-none')
            $("#Message").addClass('alert-danger')
            break;
    }
}