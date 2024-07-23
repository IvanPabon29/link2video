//Codigo

//seleccionar
const cronometro = document.getElementById("cronometro");
const botonIncioPausa = document.getElementById("boton-inicio-pausa");
const botonReiniciar = document.getElementById("boton-reiniciar");

//Se crear la variables
let [horas, minutos, segundos] = [0, 0, 0];

let intervaloTiempo;
let estadoCronometro = "pausado";

function actualizarCronometro(){
    segundos++;

    if (segundos / 60 === 1) {
        segundos = 0;
        minutos++;

        if (minutos / 60 === 1){
            minutos = 0;
            horas++;
        }
    };

    const segundosFormato = asignarFormato(segundos);
    const minutosFormato = asignarFormato(minutos);
    const horasFormato = asignarFormato(horas);

    cronometro.innerText = `${horasFormato}:${minutosFormato}:${segundosFormato}`;
};

//Se crea funcion para cuando el numero es menor 10 y toca mostrar un 0.
function asignarFormato(unidadTiempo){
    return unidadTiempo < 10 ? "0" + unidadTiempo : unidadTiempo;
};

//Se crean los eventos.
botonIncioPausa.addEventListener("click", () =>{
    if(estadoCronometro === "pausado"){     //si esta pausado se EJECUTA
        intervaloTiempo = window.setInterval(actualizarCronometro, 1000);
        botonIncioPausa.innerHTML = `<i class="bi bi-pause-fill"></i>`;
        botonIncioPausa.classList.remove("iniciar"); 
        botonIncioPausa.classList.add("pausar");
        estadoCronometro = "play";
    }else{
        window.clearInterval(intervaloTiempo);
        botonIncioPausa.innerHTML = `<i class="bi bi-play-fill"></i>`;
        botonIncioPausa.classList.remove("pausar");
        botonIncioPausa.classList.add("iniciar");
        estadoCronometro = "pausado"
    }
});

botonReiniciar.addEventListener("click", () =>{
    window.clearInterval(intervaloTiempo);
    segundos = 0;
    minutos = 0;
    horas = 0;
    cronometro.innerText = `00:00:00`;
    //para verificar si el cronometro esta play
    if (estadoCronometro === "play"){
        intervaloTiempo = window.setInterval(actualizarCronometro, 1000);
    }
});
