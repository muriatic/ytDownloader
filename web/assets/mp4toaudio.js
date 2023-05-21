async function getFolder() {
    var file_path = await eel.getFilePath()();
    if (file_path) {
        console.log(file_path);
        $('#selectedFile').html(file_path)
    }
}

// need to add function to make sure a non MP4 file isnt selected;; some .onchange thing

async function convertToMP3() {
    $("#Message").addClass('d-none')
    $("#Message").removeClass('alert-success')
    $("#Message").removeClass('alert-danger')
    var filePath = document.getElementById("fileName").innerHTML;

    var responseCode = await eel.convertFile(filePath, '.mp3')();

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
    var filePath = document.getElementById("fileName").innerHTML;

    var responseCode = await eel.convertFile(filePath, '.wav')();

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