function showFileTypes() {
    $("#file-type-div").removeClass('d-none');
}

function hideFileTypes() {
    $("#file-type-div").addClass('d-none');
}

var custom_timestamps = false

function showStartEndQuestion() {
    $("#start-end-div").removeClass('d-none');
    custom_timestamps = true
}

function hideStartEndQuestion() {
    $("#start-end-div").addClass('d-none');
    custom_timestamps = false
}

function setActivePage() {
    page_name = location.pathname.substring(location.pathname.lastIndexOf("/") + 1);
    
    var element = document.getElementById(page_name)
    element.classList.add('active')
}