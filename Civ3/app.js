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
        p.className = "floating-petal"; p.style.zIndex = "9999";
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

                // Inyección de Pase Maestro con Código QR
                resultadoDiv.innerHTML = `
                <article class="ticket-master">
                    <div class="ticket-m-img"></div>
                    <div class="ticket-m-info">
                        <h3>Pase Reservado</h3>
                        <div class="ticket-m-name">${data.nombre}</div>
                        
                        <div class="ticket-events">
                            <div class="e-col">
                                <h4>Unión Civil</h4>
                                <p><strong>17 de Octubre, 2026</strong><br>Calle del Encanto<br>Zoyatepec, Gro.</p>
                            </div>
                            <div class="e-col">
                                <h4>Ceremonia Religiosa</h4>
                                <p><strong>24 de Octubre, 2026</strong><br>Recepción Principal<br>Chilpancingo, Gro.</p>
                            </div>
                        </div>

                        <div class="ticket-m-footer">
                            <div class="details">
                                <p>Pases asignados: <strong>${data.pases}</strong></p>
                                <p>Mesa / Zona: <strong>${data.mesa || "Por asignar"}</strong></p>
                                <p style="font-size: 0.85rem; margin-top: 8px; color: var(--gold-deep);">CÓDIGO: ${data.codigo}</p>
                            </div>
                            <div class="qr-box">
                                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(data.codigo)}&color=3b0710" alt="QR de Acceso">
                            </div>
                        </div>
                    </div>
                </article>
                <div class="btn-print-row">
                    <button class="btn gold" type="button" onclick="window.print()">Imprimir Pase / Guardar PDF</button>
                </div>`;

            }
            catch (error) {
                mensajeDiv.textContent = "Error de conexión con el servidor.";
                mensajeDiv.className = "form-message error";
            }
        });
    }
});
