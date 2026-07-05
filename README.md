# MS Predictor V14

PWA mit GitHub-Actions-Datenimport.

## Upload
Den Inhalt dieses ZIPs direkt ins Root deines Repositories hochladen.

## GitHub Secrets
Repository -> Settings -> Secrets and variables -> Actions -> New repository secret:
- `FOOTBALL_DATA_KEY`
- `ODDS_API_KEY`

## Workflows
- `Deploy GitHub Pages`: veröffentlicht die PWA.
- `Update Predictor Data`: holt Spiele/Quoten und schreibt `data/live-data.json`.
