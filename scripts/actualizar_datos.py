#!/usr/bin/env python3
"""Descarga el snapshot diario de precios desde la API pública de la CNE
(Bencina en Línea) y lo guarda en data/estaciones.json y data/marcas.json.
Se ejecuta automáticamente con GitHub Actions (ver .github/workflows)."""
import gzip
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

API_ESTACIONES = "https://api.bencinaenlinea.cl/api/busqueda_estacion_filtro?region=13"
API_MARCAS = "https://api.bencinaenlinea.cl/api/marca"
DATA = Path(__file__).resolve().parent.parent / "data"

CAMPOS_COMBUSTIBLE = ("nombre_corto", "nombre_largo", "suministra", "precio",
                      "unidad_cobro", "actualizado", "precio_fecha")


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "bencina-comuna/1.0 (sitio sin fines de lucro)",
        "Accept-Encoding": "gzip, identity",
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        raw = r.read()
    if raw[:2] == b"\x1f\x8b":  # magic number gzip
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def main():
    DATA.mkdir(exist_ok=True)

    # Marcas (id -> nombre)
    marcas = fetch(API_MARCAS)["data"]
    marcas_min = [{"id": m["id"], "nombre": m["nombre"]} for m in marcas]
    (DATA / "marcas.json").write_text(json.dumps(marcas_min, ensure_ascii=False), encoding="utf-8")

    # Estaciones: nos quedamos solo con los campos que usa la web (reduce peso)
    est = fetch(API_ESTACIONES)["data"]
    est_min = []
    for e in est:
        est_min.append({
            "id": e.get("id"),
            "marca": e.get("marca"),
            "direccion": (e.get("direccion") or "").strip(),
            "comuna": e.get("comuna"),
            "region": e.get("region"),
            "latitud": e.get("latitud"),
            "longitud": e.get("longitud"),
            "logo": e.get("logo"),
            "combustibles": [
                {k: c.get(k) for k in CAMPOS_COMBUSTIBLE}
                for c in (e.get("combustibles") or [])
            ],
        })

    hora_chile = datetime.now(timezone(timedelta(hours=-4)))
    snapshot = {"fecha": hora_chile.strftime("%d-%m-%Y %H:%M (hora Chile)"), "data": est_min}
    (DATA / "estaciones.json").write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    print(f"OK: {len(est_min)} estaciones, {len(marcas_min)} marcas — {snapshot['fecha']}")


if __name__ == "__main__":
    main()
