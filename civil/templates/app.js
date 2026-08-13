"use strict";

const CONFIG = { 
    invitationUrl: "https://civil.mya2026.galaxymanager.systems/", 
    weddingDate: new Date("2026-10-17T12:00:00-06:00") 
};

function initShare() { 
    document.getElementById("shareBtn")?.addEventListener("click", async () => { 
        const d = { 
            title: "Montserrat & Alan | Boda Civil", 
            text: "Te invitamos a celebrar nuestra boda civil.", 
            url: CONFIG.invitationUrl 
        }; 
        try { 
            if (navigator.share) await navigator.share(d); 
            else { 
                await navigator.clipboard.writeText(CONFIG.invitationUrl); 
                alert("Enlace copiado."); 
            } 
        } catch (_) { } 
    }); 
}

function initCountdown() { 
    const e = Object.fromEntries(["days", "hours", "minutes", "seconds"].map(id => [id, document.getElementById(id)])); 
    function u() { 
        const diff = Math.max(0, CONFIG.weddingDate - new Date()); 
        e.days.textContent = Math.floor(diff / 86400000); 
        e.hours.textContent = String(Math.floor(diff % 86400000 / 3600000)).padStart(2, "0"); 
        e.minutes.textContent = String(Math.floor(diff % 3600000 / 60000)).padStart(2, "0"); 
        e.seconds.textContent = String(Math.floor(diff % 60000 / 1000)).padStart(2, "0"); 
    } 
    u(); 
    setInterval(u, 1000); 
}

function initPetals() { 
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return; 
    setInterval(() => { 
        const p = document.createElement("span"); 
        p.className = "floating-petal"; 
        p.style.left = `${Math.random() * 100}vw`; 
        p.style.setProperty("--x", `${Math.random() * 160 - 80}px`); 
        p.style.animationDuration = `${7 + Math.random() * 6}s`; 
        document.body.appendChild(p); 
        setTimeout(() => p.remove(), 14000); 
    }, 1200); 
}

// ÚNICO LISTENER DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => { 
    initShare(); 
    initCountdown(); 
    initPetals();

    const form = document.getElementById("formBusqueda");
    
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            
            const texto = document.getElementById("buscar").value;
            const resultadoDiv = document.getElementById("resultado");
            const mensajeDiv = document.getElementById("mensajeBusqueda");

            mensajeDiv.textContent = "Consultando base de datos...";
            mensajeDiv.className = "form-message";
            resultadoDiv.innerHTML = "";

            try {
                // Consulta directa y exclusiva al backend Flask
                const response = await fetch(`/buscar?q=${encodeURIComponent(texto)}`);
                const data = await response.json();

                if (data.error) {
                    mensajeDiv.textContent = data.error;
                    mensajeDiv.className = "form-message error";
                    return;
                }

                mensajeDiv.textContent = "Invitación localizada.";
                mensajeDiv.className = "form-message ok";

                resultadoDiv.innerHTML = `
                <article class="ticket">
                    <div class="ticket-main">
                        <h3>Pase civil</h3>
                        <div class="ticket-name">${data.nombre}</div>
                        <div class="ticket-info">
                            Código: <strong>${data.codigo}</strong><br>
                            Invitación válida para <strong>${data.pases}</strong> personas<br>
                            Mesa/Zona: <strong>${data.mesa || "Por asignar"}</strong>
                        </div>
                    </div>
                    <div class="ticket-seal">M&A</div>
                </article>`;
                
            } catch (error) {
                mensajeDiv.textContent = "Error de conexión con el servidor.";
                mensajeDiv.className = "form-message error";
            }
        });
    }
});