#!/usr/bin/env python3
"""Semi-automatización de descuentos: descarga la guía mensual de Chócale
(fuente pública que consolida los descuentos de bencina) y extrae los párrafos
con los descuentos por día. NO publica nada automáticamente: genera
data/descuentos_sugeridos.txt para que tú revises y actualices descuentos.json.

Se ejecuta el día 2 de cada mes vía GitHub Actions y también puedes correrlo
a mano: python scripts/revisar_descuentos.py
"""
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.texto = []
        self._capturar = False

    def handle_starttag(self, tag, attrs):
        if tag in ("li", "p", "h2", "h3"):
            self._capturar = True
            self._buffer = []

    def handle_endtag(self, tag):
        if tag in ("li", "p", "h2", "h3") and self._capturar:
            t = " ".join("".join(self._buffer).split())
            if t:
                self.texto.append(t)
            self._capturar = False

    def handle_data(self, data):
        if self._capturar:
            self._buffer.append(data)


def main():
    hoy = datetime.now(timezone(timedelta(hours=-4)))
    # La guía de Chócale sigue el patrón /YYYY/MM/descuentos-en-bencina...
    # El slug exacto cambia mes a mes, así que buscamos en la portada de la sección.
    indice = "https://chocale.cl/temas/descuentos-bencinas/"
    req = urllib.request.Request(indice, headers={"User-Agent": "Mozilla/5.0 (bencina-comuna)"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    patron = rf"https://chocale\.cl/{hoy.year}/{hoy.month:02d}/[a-z0-9\-]*descuentos[a-z0-9\-]*/"
    urls = re.findall(patron, html)
    if not urls:
        print("Aún no se publica la guía de este mes. Revisa manualmente:", indice)
        return
    url = urls[0]

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (bencina-comuna)"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "ignore")
    ex = Extractor()
    ex.feed(html)
    relevantes = [t for t in ex.texto
                  if any(t.lower().startswith(d + ":") or f"**{d}" in t.lower() or t.lower().startswith(d) for d in DIAS)
                  and len(t) > 30]

    DATA.mkdir(exist_ok=True)
    out = DATA / "descuentos_sugeridos.txt"
    cuerpo = [f"Fuente: {url}", f"Extraído: {hoy:%d-%m-%Y}", "-" * 60]
    cuerpo += relevantes or ["No se pudieron extraer líneas automáticamente; abre la fuente y copia a mano."]
    cuerpo += ["-" * 60, "Revisa esto y actualiza data/descuentos.json a mano.",
               "Recuerda citar la fuente y verificar condiciones con cada banco/distribuidora."]
    out.write_text("\n".join(cuerpo), encoding="utf-8")
    print(f"OK: {len(relevantes)} líneas sugeridas escritas en {out}")


if __name__ == "__main__":
    main()
