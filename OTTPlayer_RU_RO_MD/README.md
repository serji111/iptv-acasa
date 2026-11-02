# IPTV unic: rusă + română + Moldova

Acest proiect generează automat `playlist.m3u` din fluxurile publice IPTV-org, eliminând duplicatele după URL. Categoriile sunt `Rusa`, `Romana`, `Moldova`.

## Pregătire GitHub
1. Creează un repository **public** nou la https://github.com/new, de exemplu `iptv-acasa`.
2. Încarcă păstrând structura `combine.py` și `.github/workflows/update.yml`. Dacă site-ul GitHub nu permite încărcarea simplă a folderului ascuns `.github`, folosește **Add file > Create new file** și scrie numele `.github/workflows/update.yml`, apoi copiază conținutul din arhivă.
3. Accesează **Actions > Actualizare IPTV > Run workflow**. Dacă Actions sunt dezactivate, activează-le din setările repository-ului.
4. După finalizarea cu succes a fluxului, fișierul `playlist.m3u` va apărea automat în repository.
5. Linkul tău OTTPlayer este:
   `https://raw.githubusercontent.com/UTILIZATORUL_TAU/iptv-acasa/main/playlist.m3u`
   Înlocuiește `UTILIZATORUL_TAU` cu numele contului GitHub și `iptv-acasa` cu numele repository-ului ales. Dacă ramura implicită nu e `main`, folosește numele ramurii efective.
6. În ottplayer.tv intră la Playlists, adaugă acest link ca playlist URL, selectează televizorul și salvează.

Workflow-ul încearcă să actualizeze lista zilnic. Actualizarea automată GitHub Actions nu este garantată la oră fixă; GitHub poate dezactiva joburi programate pentru repository-uri inactive.

## Limitări
- Sunt incluse numai fluxuri publice. Disponibilitatea în UK, licențele și stabilitatea canalelor diferă.
- Moldova și româna se pot suprapune; duplicatele pe același URL sunt eliminate, dar aceeași televiziune poate apărea cu URL-uri diferite.
- Acest proiect **nu** retransmite fluxurile video și nu oferă drepturi de vizionare suplimentare.
- Dacă toate sursele sunt temporar inaccesibile, jobul eșuează și nu suprascrie lista existentă.
