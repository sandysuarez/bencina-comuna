# ⛽ Bencina por Comuna

Web gratuita que muestra los precios de la bencina en Chile, filtrables por región y comuna, con los descuentos vigentes por día. Costo de operación: **$0**.

## Cómo funciona

- **Precios**: la API pública de la CNE ([Bencina en Línea](https://www.bencinaenlinea.cl)) entrega todas las estaciones del país con sus precios. Un robot de GitHub Actions la consulta cada mañana y guarda el snapshot en `data/estaciones.json`. Si el snapshot no existe, la página consulta la API en vivo.
- **Descuentos**: viven en `data/descuentos.json` (editable a mano). El día 2 de cada mes, el robot descarga la guía mensual de descuentos de Chócale y deja las líneas encontradas en `data/descuentos_sugeridos.txt` para que las revises y actualices el JSON en 5 minutos. No se publica nada sin tu revisión (evita errores y problemas de derechos).
- **Hosting**: GitHub Pages (gratis, sin servidor, sin base de datos).

## Publicar la web (una sola vez, ~15 min)

1. Crea una cuenta gratis en [github.com](https://github.com) si no tienes.
2. Crea un repositorio nuevo, público, llamado por ejemplo `bencina-comuna`.
3. Sube TODO el contenido de esta carpeta (incluida la carpeta oculta `.github`). Puedes arrastrar los archivos en la web de GitHub ("uploading an existing file") o usar git:
   ```bash
   git init && git add . && git commit -m "primera versión"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/bencina-comuna.git
   git push -u origin main
   ```
4. En el repo: **Settings → Pages → Source: Deploy from a branch → Branch: `main` / (root) → Save**.
5. En la pestaña **Actions**, acepta habilitar los workflows y ejecuta "Actualizar datos diariamente" con el botón **Run workflow** (la primera vez, para generar `data/estaciones.json`).
6. Listo: tu web queda en `https://TU_USUARIO.github.io/bencina-comuna/` y se actualiza sola cada mañana.

## Mantención mensual (5 minutos)

1. Los primeros días del mes, abre `data/descuentos_sugeridos.txt` en tu repo.
2. Compara con `data/descuentos.json` y actualiza montos/bancos/días.
3. Guarda (commit). Nada más.

Formato de un descuento (`dias`: 0=domingo, 1=lunes … 6=sábado):
```json
{ "dias": [5], "marca": "COPEC", "medio": "Tarjeta Tenpo vía App Copec", "beneficio": "Cashback de $50 a $300 por litro" }
```

## Probar en tu computador

```bash
python -m http.server 8000
# abre http://localhost:8000
```
(Sirve la carpeta con un servidor local; abrir el archivo directo con doble clic bloquea la carga de los JSON.)

## Ideas para crecer (todo gratis)

- Dominio propio `.cl` (esto sí cuesta ~$10.000/año, opcional; GitHub Pages lo soporta).
- Mapa con las estaciones usando Leaflet + OpenStreetMap (gratis; ya se guardan latitud/longitud).
- Histórico de precios: el robot ya hace un commit diario, así que el historial queda gratis en git.

## Créditos y condiciones

- Precios: Comisión Nacional de Energía, [Bencina en Línea](https://www.bencinaenlinea.cl) / [api.cne.cl](https://api.cne.cl) (datos públicos y gratuitos).
- Referencias de descuentos: guías mensuales de [Chócale](https://chocale.cl/temas/descuentos-bencinas/), citadas como fuente. Verifica siempre las condiciones con cada banco o distribuidora.
