
document.getElementById("add_work").addEventListener("click", function(){
    document.getElementById("add_work_popup").classList.add("open")
})
document.getElementById("close_add_work_popup").addEventListener("click", function(){
    document.getElementById("add_work_popup").classList.remove("open")
})

document.getElementById("edit_client").addEventListener("click", function(){
    document.getElementById("edit_client_popup").classList.add("open")
})
document.getElementById("close_edit_client_popup").addEventListener("click", function(){
    document.getElementById("edit_client_popup").classList.remove("open")
})


document.getElementById("delete_order").addEventListener("click", function(){
    document.getElementById("delete_popup").classList.add("open")
})
document.getElementById("close_delete_popup").addEventListener("click", function(){
    document.getElementById("delete_popup").classList.remove("open")
})


window.scroll({
    top: 500,
    behavior: "auto"
});
