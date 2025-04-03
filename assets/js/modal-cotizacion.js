// Obtener el modal
var modal = document.getElementById("cotizacion");

// Obtener el enlace que abre el modal
var link = document.getElementById("openModalCoti");

// Obtener el <span> que cierra el modal
var span = document.getElementsByClassName("closeCoti")[0];

// Cuando el usuario haga clic en el enlace, abre el modal
link.onclick = function(event) {
    event.preventDefault();
    modal.style.display = "block";
}

// Cuando el usuario haga clic en <span> (x), cierra el modal
span.onclick = function() {
    modal.style.display = "none";
}

// Cuando el usuario haga clic en cualquier lugar fuera del modal, cierra el modal
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
