"""DataUpdateCoordinator for Andorra Preus Carburants.

Fetch strategy
──────────────
For each selected fuel type, fetches all 7 parishes in parallel using
asyncio.gather.  Data is stored as:

  coordinator.data = {
      "sp95": {
          "Canillo":            StationList,
          "Encamp":             StationList,
          ...
          "Escaldes-Engordany": StationList,
          "__global__": GlobalStats,
      },
      "gasoil": { ... },
      ...
  }

Where StationList = {
    "stations":       list[dict],   # {name, price}
    "min_price":      float | None,
    "max_price":      float | None,
    "avg_price":      float | None,
    "num_stations":   int,
    "cheapest":       dict | None,  # {name, price}
}

And GlobalStats (__global__) = same structure but across all parishes, plus:
    "cheapest_parish": str   # parish where the cheapest price was found
"""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime, timedelta
from html.parser import HTMLParser

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    BASE_URL,
    DOMAIN,
    FUEL_IDS_UNVERIFIED,
    FUEL_TYPES,
    PARISHES,
)

_LOGGER = logging.getLogger(__name__)


# ── HTML Parser ──────────────────────────────────────────────────────────────

class _PriceParser(HTMLParser):
    """Recopila todos los textos de celdas/bloques del HTML de la API."""

    def __init__(self) -> None:
        super().__init__()
        self._in_block = False
        self._current = ""
        self._cells: list[str] = []

    _BLOCK_TAGS = {"td", "th", "li", "div", "span", "p", "h3", "h4", "strong", "b", "a"}

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            self._in_block = True
            self._current = ""

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._BLOCK_TAGS:
            text = self._current.strip()
            if text:
                self._cells.append(text)
            self._in_block = False
            self._current = ""

    def handle_data(self, data: str) -> None:
        if self._in_block:
            self._current += data

    # Textos a ignorar quan busquem el nom de l'estació cap enrere
    _SKIP_NAMES = {
        "navega", "variable", "bp", "elf", "shell", "cepsa", "repsol",
        "totalenergies", "total energies", "galp", "meroil", "gasopas",
        "q8", "agip", "campsa", "petronor",
    }

    def stations(self) -> list[dict]:
        """Devuelve lista de {name, price} encontrados.

        Estructura de l'API:
          [Nom estació] [Adreça] [Navega] [Marca] [preu €/l]

        "Variable" és una marca (Andorracing), no indica preu variable.
        Cal saltar marca, "Navega" i adreces per trobar el nom real.
        """
        result: list[dict] = []
        price_re = re.compile(r"(\d+[.,]\d+)\s*€/l", re.IGNORECASE)

        for i, cell in enumerate(self._cells):
            m = price_re.search(cell)
            if not m:
                continue
            try:
                price = round(float(m.group(1).replace(",", ".")), 4)
            except ValueError:
                continue

            # Buscar nom de l'estació cap enrere saltant marca/Navega/adreces
            name = ""
            for j in range(i - 1, max(i - 10, -1), -1):
                candidate = self._cells[j].strip()
                clow = candidate.lower()

                if clow in self._SKIP_NAMES:
                    continue
                if clow == "navega":
                    continue
                # Sembla una adreça (té coma)
                if "," in candidate:
                    continue
                # És un número o preu
                if price_re.search(candidate):
                    continue
                if re.match(r"^\d+[.,]?\d*$", candidate):
                    continue
                if len(candidate) < 3:
                    continue

                name = candidate
                break

            result.append({"name": name or "Desconeguda", "price": price})

        return result


def _parse(html: str) -> list[dict]:
    """Parsea HTML de la API y devuelve [{name, price}].

    Intenta primero con el parser de árbol; si no encuentra nada usa regex puro.
    """
    parser = _PriceParser()
    parser.feed(html)
    stations = parser.stations()
    if stations:
        return stations

    # Fallback regex
    price_re = re.compile(r"(\d+[.,]\d+)\s*€/l", re.IGNORECASE)
    for i, raw_price in enumerate(price_re.findall(html)):
        try:
            price = round(float(raw_price.replace(",", ".")), 4)
        except ValueError:
            continue
        stations.append({"name": f"Estació {i + 1}", "price": price})

    return stations


def _stats(stations: list[dict]) -> dict:
    """Calcula estadísticas a partir de la lista de estaciones."""
    valid = [s for s in stations if s.get("price") is not None]
    prices = [s["price"] for s in valid]
    cheapest = min(valid, key=lambda s: s["price"]) if valid else None
    return {
        "stations": stations,
        "min_price": min(prices) if prices else None,
        "max_price": max(prices) if prices else None,
        "avg_price": round(sum(prices) / len(prices), 4) if prices else None,
        "num_stations": len(valid),
        "cheapest": cheapest,
    }


# ── Coordinator ──────────────────────────────────────────────────────────────

class AndorraCarburantsCoordinator(DataUpdateCoordinator):
    """Coordinator que obtiene precios de los 7 parroquias en paralelo."""

    def __init__(
        self,
        hass: HomeAssistant,
        fuel_type_keys: list[str],
        scan_interval: int,
    ) -> None:
        self.fuel_type_keys = fuel_type_keys
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Obtener y parsear datos de todas las parroquias y combustibles."""
        today = datetime.now().strftime("%Y-%m-%d")
        date_param = f"{today} 23:59:59"

        result: dict = {}

        async with aiohttp.ClientSession() as session:
            for fuel_key in self.fuel_type_keys:
                product_id, fuel_name = FUEL_TYPES[fuel_key]

                # Construir tareas paralelas para las 7 parroquias
                async def _fetch(parish_name: str, parish_id: int) -> tuple[str, list[dict]]:
                    url = (
                        f"{BASE_URL}"
                        f"?idProducte={product_id}"
                        f"&data={date_param}"
                        f"&idParroquia={parish_id}"
                    )
                    try:
                        async with asyncio.timeout(20):
                            async with session.get(url) as resp:
                                resp.raise_for_status()
                                html = await resp.text()
                    except aiohttp.ClientError as err:
                        _LOGGER.warning(
                            "[%s/%s] Error HTTP: %s", fuel_key, parish_name, err
                        )
                        return parish_name, []

                    _LOGGER.debug(
                        "[%s/%s] HTML (2000c): %s",
                        fuel_key, parish_name, html[:2000]
                    )

                    stations = _parse(html)
                    if not stations and product_id in FUEL_IDS_UNVERIFIED:
                        _LOGGER.warning(
                            "[%s/%s] 0 estaciones — idProducte=%d podría ser incorrecto. "
                            "Activa DEBUG para ver el HTML crudo.",
                            fuel_key, parish_name, product_id,
                        )
                    elif not stations:
                        _LOGGER.warning(
                            "[%s/%s] 0 estaciones en la respuesta. "
                            "Activa DEBUG para ver el HTML.",
                            fuel_key, parish_name,
                        )
                    return parish_name, stations

                tasks = [
                    _fetch(parish_name, parish_id)
                    for parish_name, parish_id in PARISHES.items()
                ]
                try:
                    parish_results: list[tuple[str, list[dict]]] = await asyncio.gather(*tasks)
                except Exception as err:
                    raise UpdateFailed(f"Error en la petición: {err}") from err

                fuel_data: dict = {}
                all_stations_global: list[dict] = []

                for parish_name, stations in parish_results:
                    fuel_data[parish_name] = _stats(stations)
                    # Para el ranking global, añadir parroquia a cada estación
                    for s in stations:
                        all_stations_global.append(
                            {"name": s["name"], "price": s["price"], "parish": parish_name}
                        )

                # Stats globales (todo el país)
                global_stats = _stats(
                    [{"name": s["name"], "price": s["price"]} for s in all_stations_global]
                )
                global_stats["all_stations"] = sorted(
                    all_stations_global,
                    key=lambda s: s["price"] if s["price"] is not None else 9999,
                )
                # Parroquia donde está la más barata
                cheapest_global = min(
                    all_stations_global,
                    key=lambda s: s["price"] if s["price"] is not None else 9999,
                    default=None,
                )
                global_stats["cheapest_parish"] = (
                    cheapest_global.get("parish") if cheapest_global else None
                )
                global_stats["fuel_name"] = fuel_name
                global_stats["date"] = today
                fuel_data["__global__"] = global_stats

                result[fuel_key] = fuel_data

        return result

    def get_station_price(self, station_name: str, fuel_key: str) -> float | None:
        """Devuelve el precio actual de una estación concreta (búsqueda parcial, case-insensitive)."""
        if not self.data or fuel_key not in self.data:
            return None
        global_data = self.data[fuel_key].get("__global__", {})
        all_stations = global_data.get("all_stations", [])
        name_lower = station_name.strip().lower()
        for s in all_stations:
            if name_lower in s["name"].lower():
                return s["price"]
        return None

    def get_all_station_names(self) -> list[str]:
        """Lista de todos los nombres de estaciones conocidos (para el config flow)."""
        if not self.data:
            return []
        names: set[str] = set()
        for fuel_key in self.fuel_type_keys:
            global_data = self.data.get(fuel_key, {}).get("__global__", {})
            for s in global_data.get("all_stations", []):
                if s.get("name") and s["name"] != "Desconeguda":
                    names.add(s["name"])
        return sorted(names)
        