#!/usr/bin/env python3
"""Verifica las redirecciones 301 del mapa de Selva Maya Tours.

Uso (solo lectura, no modifica nada):
    python3 verificar-redirecciones.py                      # las 137 filas del mapa
    python3 verificar-redirecciones.py --limite 10          # prueba rápida
    python3 verificar-redirecciones.py --dominio selvamayatours.com
    python3 verificar-redirecciones.py --solo-fallos        # muestra solo lo que falla

Para cada fila pide la URL antigua, sigue las redirecciones salto a salto y
comprueba que termine en la URL nueva con código 200 y que el primer salto sea
permanente (301 o 308). Guarda el detalle en resultado-verificacion-FECHA.csv.
Pausa entre peticiones para no activar el límite de velocidad de Wix.
"""
import argparse
import csv
import datetime
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASES = {
    "selvamayatours.com": "https://selvamayatours.com",
    "jaguarmayatours.com": "https://www.jaguarmayatours.com",
}
DESTINO_HOST = "www.jaguarmayatours.com"
PERMANENTES = (301, 308)
MAX_SALTOS = 6


class SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(SinRedireccion)


def pedir(url, reintentos=5):
    """Devuelve (codigo, ubicacion) sin seguir redirecciones; reintenta ante 429."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (verificador-redirecciones)"})
    for i in range(reintentos):
        try:
            with OPENER.open(req, timeout=30) as r:
                return r.status, None
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 * (i + 1))
                continue
            return e.code, e.headers.get("Location")
        except Exception:
            time.sleep(2)
    return 0, None


def norm(ruta):
    ruta = urllib.parse.unquote(ruta).rstrip("/")
    return ruta or "/"


def seguir(url, pausa):
    saltos = []
    actual = url
    for _ in range(MAX_SALTOS):
        codigo, loc = pedir(actual)
        saltos.append(codigo)
        if codigo in (301, 302, 303, 307, 308) and loc:
            actual = urllib.parse.urljoin(actual, loc)
            time.sleep(pausa)
            continue
        return codigo, actual, saltos
    return 0, actual, saltos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", default="mapa-redirecciones-propuesto.csv")
    ap.add_argument("--dominio", choices=list(BASES))
    ap.add_argument("--limite", type=int)
    ap.add_argument("--pausa", type=float, default=1.2)
    ap.add_argument("--solo-fallos", action="store_true")
    a = ap.parse_args()

    with open(a.csv, newline="", encoding="utf-8") as f:
        filas = [r for r in csv.DictReader(f) if not a.dominio or r["dominio"] == a.dominio]
    if a.limite:
        filas = filas[: a.limite]

    salida = []
    resumen = {"OK": 0, "FALLA": 0, "AVISO": 0}
    print(f"Verificando {len(filas)} redirecciones (pausa {a.pausa}s)...\n")
    for i, r in enumerate(filas, 1):
        origen = BASES[r["dominio"]] + urllib.parse.quote(r["url_antigua"], safe="/")
        esperado = norm(r["url_nueva_propuesta"])
        codigo, final, saltos = seguir(origen, a.pausa)
        u = urllib.parse.urlparse(final)
        ok_destino = codigo == 200 and u.hostname == DESTINO_HOST and norm(u.path) == esperado
        primer = saltos[0] if saltos else 0
        if ok_destino and primer in PERMANENTES and len(saltos) <= 3:
            estado, nota = "OK", ""
        elif ok_destino:
            estado = "AVISO"
            nota = "no redirige: la URL ya es el destino" if saltos == [200] else (("primer salto no permanente (%s)" % primer) if primer not in PERMANENTES else "demasiados saltos")
        else:
            estado = "FALLA"
            nota = f"terminó en {codigo} {u.path or '/'}" if codigo else "sin respuesta"
        resumen[estado] += 1
        salida.append([r["dominio"], r["url_antigua"], r["url_nueva_propuesta"], estado, codigo, ">".join(map(str, saltos)), u.path, nota])
        if not a.solo_fallos or estado != "OK":
            print(f"[{i:3}/{len(filas)}] {estado:5} {r['dominio'][:6]} {r['url_antigua'][:58]:58} -> {nota or r['url_nueva_propuesta'][:40]}")
        time.sleep(a.pausa)

    nombre = f"resultado-verificacion-{datetime.date.today():%Y%m%d}.csv"
    with open(nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["dominio", "url_antigua", "url_esperada", "estado", "codigo_final", "saltos", "ruta_final", "nota"])
        w.writerows(salida)
    print(f"\nResumen: {resumen['OK']} OK · {resumen['AVISO']} avisos · {resumen['FALLA']} fallas de {len(filas)}")
    print(f"Detalle en {nombre}")
    sys.exit(0 if resumen["FALLA"] == 0 else 1)


if __name__ == "__main__":
    main()
