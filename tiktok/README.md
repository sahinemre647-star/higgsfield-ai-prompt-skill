# TikTok-Protokoll

Ein Eintrag pro gepostetem Video: Hook, Prompt, Modell, Caption und
die Zahlen nach dem Posten. So weiß jede neue Claude-Sitzung, was schon
gemacht wurde und was funktioniert hat.

Daten: `tiktok/videos.json` (wird committet). Werkzeug: `tiktok/log.py`.

## Ablauf

1. **Video erstellt** → `python3 tiktok/log.py add --title "..." --hook "..." --model ... --prompt "..." --length 12`
2. **24–48 h nach dem Posten** → Zahlen aus TikTok-Analytics eintragen:
   `python3 tiktok/log.py stats v001 --views 300 --avg-watch 4.1 --completion 12 --fyp 80`
3. **Erkenntnis** → `python3 tiktok/log.py note v001 "Hook zu langsam"`
4. **Auswerten** → `python3 tiktok/log.py report` (Top/Flop nach Views + Retention)

Retention = Ø Wiedergabedauer ÷ Videolänge. Ziel: über 50 %.

## Für Claude

Bei jeder TikTok- oder Video-Aufgabe zuerst `python3 tiktok/log.py list`
und `report` ausführen. Jedes neue Video sofort mit `add` eintragen,
danach den Nutzer nach den Zahlen fragen und mit `stats` ergänzen.
Änderungen committen und pushen, sonst gehen sie verloren.

## Was wir bisher wissen (aus früheren Sitzungen)

- **Creator Rewards:** nur Videos über 1 Minute (65–75 s einplanen), originaler Inhalt, KI kennzeichnen.
- **Musik:** keine nachgebauten Melodien fremder Songs. Stattdessen Video im Takt rendern
  (Beat-Analyse einer vom Nutzer geladenen Datei) und den Song in TikTok als Sound drüberlegen.
- **Stream-Clips:** nur von Streamern, die Clippen erlauben; Credit angeben.
- **Formate bisher:** Wissensfragen (DE+EN, 37–55 s, also zu kurz für Rewards),
  Glass-Break-Simulationen, Rätsel „Finde das Zeichen“, Ring-Ball zu Musik,
  Streamer-Clips mit Subway Surfers.
- Videodateien lagen nur in den jeweiligen Cloud-Sitzungen; hier ist nur das Protokoll.
