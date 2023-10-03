
function showCalendar() {
    document.getElementById("interval_start").hidden = false;
    document.getElementById("interval_end").hidden = false;
    document.getElementById("interval_start").disabled = false;
    document.getElementById("interval_end").disabled = false;
}

function hideCalendar() {
    document.getElementById("interval_start").hidden = true;
    document.getElementById("interval_end").hidden = true;
    document.getElementById("interval_start").disabled = true;
    document.getElementById("interval_end").disabled = true;
}

if (document.getElementById("date_selector").value === "interval"){
    showCalendar()
}

function showHideCalendar(choice){
    if (choice === "interval"){showCalendar()}
    if (choice !== "interval"){hideCalendar()}
    }