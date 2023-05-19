
function showFileType() {
    $("#file_type_div").removeClass('d-none');
}

function hideFileType() {
    $("#file_type_div").addClass('d-none');
}

var customtimestamps = false

function showStartEndQuestion() {
    $("#start_end_div").removeClass('d-none');
    customtimestamps = true
}

function hideStartEndQuestion() {
    $("#start_end_div").addClass('d-none');
    customtimestamps = false
}

function setActivePage() {
    pageName = location.pathname.substring(location.pathname.lastIndexOf("/") + 1);
    
    var element = document.getElementById(pageName)
    element.classList.add('active')
}