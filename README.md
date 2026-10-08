# moodnook-uchwyty

Strona **NOOK FORM** (Mood Nook): gałki, uchwyty, klamki i ramki elektryczne z litego, bezołowiowego mosiądzu CW724R. Osiem kolekcji na jednym systemie złączy M4, konfigurator 3D, katalog PDF, wersja PL i EN.

Strona: https://wojjee.github.io/moodnook-uchwyty/

## Gałęzie

- `gh-pages` – opublikowana strona (źródło GitHub Pages). Zawartość w całości generuje workflow `site v13`; nie edytować ręcznie.
- `main` – źródła i automatyzacja:
  - `.github/workflows/site-v13.yml` – geometria (6 części), rendery (16 części), złożenie strony, prerender wszystkich adresów PL/EN, katalog PDF, testy (linki i SEO, przeglądarka: 3D, konfigurator, mobile, kontrola treści przed publikacją) i publikacja na `gh-pages` wyłącznie po zaliczonych testach.
  - `v13src/pack/a`…`d` – spakowane źródła builda (tar.xz w base64, rozpakowywane po kolei, późniejsze nadpisują wcześniejsze); sumy kontrolne w `SHA256SUMS_*`.

## Uruchomienie

Actions → **site v13** → Run workflow:

- `reuse_run` – id wcześniejszego przebiegu, którego artefakty geometrii i renderów mają zostać użyte (pomija CAD i Blender; artefakty są przechowywane 3 dni). Puste pole = pełna budowa.
- `deploy` – `yes` publikuje na `gh-pages` po zaliczonych testach, `no` tylko buduje i testuje.

Stare adresy (`klasyczna.html`, `/v8/`, `/p/`) przekierowują do odpowiednich stron v13.

Dane firmy, ceny, certyfikaty i treści prawne na stronie są oznaczonymi miejscami do uzupełnienia przez właściciela.
