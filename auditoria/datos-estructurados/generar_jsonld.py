#!/usr/bin/env python3
"""Genera los datos estructurados (JSON-LD) de Selva Maya Tours para pegar en Wix.

Uso:   python3 generar_jsonld.py
Lee:   servicios-datos.csv   (editar: precio, descripcion_propuesta, duracion_real...)
Crea:  listos/organizacion.json y listos/<servicio>.json

Reglas: solo se incluyen datos que existan en el CSV o en el sitio. No se genera
calificación ni reseñas (hay que mostrarlas visibles en la página y que sean reales).
En Wix: Ajustes de SEO de la página > Marcado de datos estructurados > pegar el JSON.
"""
import csv, json, os, re, sys, unicodedata, urllib.parse

BASE = "https://www.jaguarmayatours.com"
ORG = {
    "@context": "https://schema.org",
    "@type": "TravelAgency",
    "name": "Selva Maya Tours",
    "url": BASE + "/",
    "telephone": "+50252038784",
    "email": "selvamaya@jaguarmayatours.com",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": "Avenida La Reforma",
        "addressLocality": "Flores",
        "addressRegion": "Petén",
        "addressCountry": "GT",
    },
    "areaServed": ["Petén, Guatemala", "Belice", "México"],
    "sameAs": [
        "https://www.facebook.com/people/Selva-Maya-Tours/61556567518902/",
        "https://www.instagram.com/toursmayas",
    ],
}
PROVEEDOR = {"@type": "TravelAgency", "name": "Selva Maya Tours", "url": BASE + "/"}


def slug(t):
    t = unicodedata.normalize("NFD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def principal():
    os.makedirs("listos", exist_ok=True)
    with open("listos/organizacion.json", "w", encoding="utf-8") as f:
        json.dump(ORG, f, ensure_ascii=False, indent=2)
    n = 0
    with open("servicios-datos.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            desc = r["descripcion_propuesta"].strip()
            if r["duracion_real"].strip():
                desc += " Duración: " + r["duracion_real"].strip() + "."
            if r["punto_de_recogida"].strip():
                desc += " Recogida: " + r["punto_de_recogida"].strip() + "."
            d = {
                "@context": "https://schema.org",
                "@type": r["tipo_schema"],
                "name": r["nombre"],
                "description": desc,
                "url": BASE + urllib.parse.quote(r["url"], safe="/"),
                "provider": PROVEEDOR,
            }
            if r["tipo_schema"] == "Service":
                d["serviceType"] = "Traslado"
                d["areaServed"] = r["nombre"].replace("Flores a ", "").replace(" - Directo", "")
            if r["precio"].strip():
                d["offers"] = {
                    "@type": "Offer",
                    "price": r["precio"].replace(",", "").strip(),
                    "priceCurrency": r["moneda"],
                    "url": d["url"],
                }
            with open(f"listos/{slug(r['nombre'])}.json", "w", encoding="utf-8") as g:
                json.dump(d, g, ensure_ascii=False, indent=2)
            n += 1
    print(f"Listo: organizacion.json + {n} servicios en listos/")


if __name__ == "__main__":
    principal()
