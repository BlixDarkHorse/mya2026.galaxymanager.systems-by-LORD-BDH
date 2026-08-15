$dirs = @("Civ", "Civ2", "Civ3", "Civ4", "Civ5", "SFYM", "SFYM2", "SFYM3", "SFYM4", "SFYM5")

foreach ($d in $dirs) {
    if (Test-Path $d) {
        # Find PDF file
        $pdf = Get-ChildItem -Path $d -Filter "*.pdf" | Select-Object -First 1
        $pdfName = "1.pdf"
        if ($pdf) {
            $pdfName = $pdf.Name
        }

        $indexPath = Join-Path $d "index.html"
        if (Test-Path $indexPath) {
            $content = Get-Content -Raw $indexPath

            # Replace download button
            $content = $content -replace '<button class="btn gold" type="button" onclick="window.print\(\)">Imprimir Pase / Guardar PDF</button>', "<a href=`"$pdfName`" class=`"btn gold`" download>Descargar Pase en PDF</a>"
            $content = $content -replace '<a href="pase.pdf"[^>]*>Descargar Pase en PDF</a>', "<a href=`"$pdfName`" class=`"btn gold`" download>Descargar Pase en PDF</a>"

            # Replace QR
            $content = $content.Replace('<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Boda-Montserrat-Alan-2026&color=3b0710" alt="QR de Boda">', '<img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://mya2026.galaxymanager.systems&color=c9a646&bgcolor=29020a" alt="QR Oficial" style="border: 2px solid var(--gold); border-radius: 8px; box-shadow: 0 0 15px rgba(201,166,70,0.3);">')

            Set-Content -Path $indexPath -Value $content
        }
    }
}

# Fix data/pases index.html etc if any QR needs replacing
$pasesFiles = Get-ChildItem -Path "data\pases" -Filter "*.html"
foreach ($f in $pasesFiles) {
    $content = Get-Content -Raw $f.FullName
    $content = $content.Replace('<img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=Boda-Montserrat-Alan-2026&color=3b0710" alt="QR de Boda">', '<img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=https://mya2026.galaxymanager.systems&color=c9a646&bgcolor=29020a" alt="QR Oficial" style="border: 2px solid var(--gold); border-radius: 8px; box-shadow: 0 0 15px rgba(201,166,70,0.3);">')
    Set-Content -Path $f.FullName -Value $content
}

# Fix JS files
$jsFiles = Get-ChildItem -Recurse -Filter "app.js"
foreach ($js in $jsFiles) {
    $content = Get-Content -Raw $js.FullName
    if ($content -notmatch 'p\.style\.zIndex="9999"') {
        $content = $content -replace 'p\.className="floating-petal";', 'p.className="floating-petal";p.style.zIndex="9999";'
        $content = $content -replace 'p\.className = "floating-petal";', 'p.className = "floating-petal"; p.style.zIndex = "9999";'
        Set-Content -Path $js.FullName -Value $content
    }
}
