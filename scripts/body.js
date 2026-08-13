'use strict';
/* =========================
   CONFIGURACIÓN RÁPIDA
   ========================= */
const INVITATION_URL = 'https://mya2026.galaxymanager.systems/';
const CONTACT_TOKEN = 'MXA-2026';
const ACCESS_KEY = 'M&A2026';
const WEDDING_DATE = new Date('2026-10-24T16:30:00-06:00');
/* QR funcional. Usa servicio externo para generar el QR.
   Si prefieres hacerlo offline, reemplaza src por un SVG/PNG local generado previamente. */
const qr = document.getElementById('qrImage');
          const privateUrl = `${INVITATION_URL}?token=${encodeURIComponent(CONTACT_TOKEN)}#contactos`;
          qr.src = `https://quickchart.io/qr?size=420&margin=2&dark=5A0F1B&light=FFFDF7&text=${encodeURIComponent(privateUrl)}`;

          /* Compartir */
          document.getElementById('shareBtn')?.addEventListener('click', async () => {
            const shareData = {
              title: 'Montserrat & Álan | Nuestra boda',
              text: 'Te invitamos a celebrar nuestra boda el 24 de octubre de 2026.',
              url: INVITATION_URL
            };
            try {
              if (navigator.share) { await navigator.share(shareData); }
              else {
                await navigator.clipboard.writeText(INVITATION_URL);
                alert('Enlace copiado al portapapeles.');
              }
            } catch (_) { /* el usuario canceló compartir */ }
          });

          /* Tabs de ubicación */
          const tabButtons = document.querySelectorAll('.tab-btn');
          const panels = document.querySelectorAll('.tab-panel');
          tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
              const target = btn.dataset.tab;
              tabButtons.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });
              panels.forEach(p => p.classList.remove('active'));
              btn.classList.add('active');
              btn.setAttribute('aria-selected', 'true');
              document.getElementById(`tab-${target}`)?.classList.add('active');
            });
          });

          /* Contactos privados */
          const unlockBtn = document.getElementById('unlockBtn');
          const accessKey = document.getElementById('accessKey');
          const phoneActions = document.getElementById('phoneActions');
          const accessMsg = document.getElementById('accessMsg');

          function unlockContacts() {
            const token = new URLSearchParams(location.search).get('token');
            const okByKey = accessKey.value.trim() === ACCESS_KEY;
            const okByToken = token === CONTACT_TOKEN;
            if (okByKey || okByToken) {
              phoneActions.classList.add('show');
              accessMsg.textContent = 'Contactos desbloqueados. Gracias por confirmar con los novios.';
            } else {
              phoneActions.classList.remove('show');
              accessMsg.textContent = 'Clave incorrecta. Verifica tu invitación o solicita la clave a los novios.';
            }
          }
          unlockBtn.addEventListener('click', unlockContacts);
          accessKey.addEventListener('keydown', e => { if (e.key === 'Enter') unlockContacts(); });
          if (new URLSearchParams(location.search).get('token') === CONTACT_TOKEN) { unlockContacts(); }

          /* Cuenta regresiva */
          const d = document.getElementById('days');
          const h = document.getElementById('hours');
          const m = document.getElementById('minutes');
          const s = document.getElementById('seconds');
          function updateCountdown() {
            const diff = WEDDING_DATE - new Date();
            const safe = Math.max(0, diff);
            const days = Math.floor(safe / 86400000);
            const hours = Math.floor((safe % 86400000) / 3600000);
            const minutes = Math.floor((safe % 3600000) / 60000);
            const seconds = Math.floor((safe % 60000) / 1000);
            d.textContent = days;
            h.textContent = String(hours).padStart(2, '0');
            m.textContent = String(minutes).padStart(2, '0');
            s.textContent = String(seconds).padStart(2, '0');
          }
          updateCountdown();
          setInterval(updateCountdown, 1000);

          /* Pétalos/brillos ligeros */
          const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          if (!reduceMotion) {
            setInterval(() => {
              const petal = document.createElement('span');
              petal.className = 'floating-petal';
              petal.style.left = `${Math.random() * 100}vw`;
              petal.style.setProperty('--x', `${(Math.random() * 160) - 80}px`);
              petal.style.animationDuration = `${7 + Math.random() * 6}s`;
              petal.style.transform = `rotate(${Math.random() * 180}deg)`;
              document.body.appendChild(petal);
              setTimeout(() => petal.remove(), 14000);
            }, 900);
          }