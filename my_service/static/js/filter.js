// Появление и скрытие плей date-input календаря при выборе интревала в Select
function showCalendar() {
    var interval_start = document.getElementById("interval_start")
    var interval_end = document.getElementById("interval_end")
    interval_start.hidden = false;
    interval_start.disabled = false;
    interval_start.classList.add("text-field__input")
    interval_end.hidden = false;
    interval_end.disabled = false;
    interval_end.classList.add("text-field__input")
}

function hideCalendar() {
    interval_start.hidden = true;
    interval_start.disabled = true;
    interval_start.classList.remove("text-field__input")
    interval_end.hidden = true;
    interval_end.disabled = true;
    interval_end.classList.remove("text-field__input")
}

if (document.getElementById("date_selector").value === "interval"){
    showCalendar()
}

function showHideCalendar(choice){
    if (choice === "interval"){showCalendar()}
    if (choice !== "interval"){hideCalendar()}
    }

// Открытие бокового меню фильтра при нажатии на кнопку
document.getElementById("filter_button").addEventListener("click", function(){
    document.getElementById("filter").classList.add("filter_bar", "active")
})

// Скрытие бокового меню фильтра при нажатии вне его области
document.querySelector("#filter .filter_bar__box").addEventListener('click', event => {
    event._isClickWithInModal = true;
});
document.getElementById("filter").addEventListener('click', event => {
    if (event._isClickWithInModal) return;
    event.currentTarget.classList.remove('active', 'filter_bar');
})