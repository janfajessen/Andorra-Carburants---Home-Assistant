"""Sensors for Andorra Preus Carburants.

Sensors created
───────────────
1. Global (1 per fuel):
     sensor.andorra_<fuel>_preu_minim
     State = cheapest price in the country

2. Per-parish (1 per fuel × 7 parishes, if enabled):
     sensor.parroquia_<parish>_<fuel>_preu_minim
     State = cheapest price in that parish

3. Favorites (1 per station × 1 per fuel configured):
     sensor.<station_slug>_<fuel>
     State  = official price
     Attrs  = preu_amb_descompte, estalvi_per_litre, estalvi_diposit_50l
"""
from __future__ import annotations

import logging
import re

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_FAVORITES,
    CONF_FUEL_TYPES,
    CONF_SHOW_PARISHES,
    DISCOUNT_CENTS,
    DISCOUNT_NONE,
    DISCOUNT_PERCENT,
    DOMAIN,
    FAV_DISCOUNT_TYPE,
    FAV_DISCOUNT_VALUE,
    FAV_STATION_NAME,
    FUEL_ICONS,
    FUEL_TYPES,
    PARISHES,
)
from .coordinator import AndorraCarburantsCoordinator

_LOGGER = logging.getLogger(__name__)

UNIT = "EUR/L"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: AndorraCarburantsCoordinator = hass.data[DOMAIN][entry.entry_id]
    fuel_keys: list[str] = entry.data.get(CONF_FUEL_TYPES, [])
    show_parishes: bool = entry.data.get(CONF_SHOW_PARISHES, True)
    favorites: list[dict] = entry.data.get(CONF_FAVORITES, [])

    entities: list[SensorEntity] = []

    for fuel_key in fuel_keys:
        entities.append(GlobalMinSensor(coordinator, entry.entry_id, fuel_key))

        if show_parishes:
            for parish_name in PARISHES:
                entities.append(
                    ParishMinSensor(coordinator, entry.entry_id, fuel_key, parish_name)
                )

    # Un sensor per estació favorita × combustible configurat
    for fav in favorites:
        for fuel_key in fuel_keys:
            entities.append(
                FavoriteStationSensor(coordinator, entry.entry_id, fav, fuel_key)
            )

    async_add_entities(entities)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _device(entry_id: str) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry_id)},
        name="Andorra Preus Carburants",
        manufacturer="Govern d'Andorra",
        model="sig.govern.ad/IPE",
        configuration_url="https://sig.govern.ad/IPE/PreusCarburants",
    )


def _slug(text: str) -> str:
    text = text.lower().strip()
    for src, dst in [
        ("àáâãä", "a"), ("èéêë", "e"), ("ìíîï", "i"),
        ("òóôõö", "o"), ("ùúûü", "u"), ("ñ", "n"), ("ç", "c"),
    ]:
        for ch in src:
            text = text.replace(ch, dst)
    text = re.sub(r"[·\-\s]+", "_", text)
    text = re.sub(r"[^a-z0-9_]", "", text)
    return text.strip("_")


# ── Base ────────────────────────────────────────────────────────────────────────

class _FuelBase(CoordinatorEntity[AndorraCarburantsCoordinator], SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UNIT

    def __init__(self, coordinator, entry_id, fuel_key):
        super().__init__(coordinator)
        self._fuel_key = fuel_key
        self._attr_device_info = _device(entry_id)
        self._attr_icon = FUEL_ICONS.get(fuel_key, "mdi:gas-station")

    @property
    def _fuel_name(self) -> str:
        return FUEL_TYPES[self._fuel_key][1]


# ── 1. Global ──────────────────────────────────────────────────────────────────

class GlobalMinSensor(_FuelBase):
    """Preu mínim al conjunt del país per a un combustible."""

    def __init__(self, coordinator, entry_id, fuel_key):
        super().__init__(coordinator, entry_id, fuel_key)
        self._attr_unique_id = f"{DOMAIN}_{fuel_key}_global_min"
        self._attr_name = f"Andorra {self._fuel_name} preu mínim"

    @property
    def _g(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._fuel_key, {}).get("__global__", {})

    @property
    def native_value(self) -> float | None:
        return self._g.get("min_price")

    @property
    def extra_state_attributes(self) -> dict:
        g = self._g
        cheapest = g.get("cheapest")
        return {
            "estacio_mes_barata":   cheapest.get("name") if cheapest else None,
            "parroquia_mes_barata": g.get("cheapest_parish"),
            "preu_mes_car":         g.get("max_price"),
            "preu_mig":             g.get("avg_price"),
            "num_estacions":        g.get("num_stations", 0),
            "carburant":            self._fuel_name,
            "data_actualitzacio":   g.get("date"),
            "top10_mes_barates":    g.get("all_stations", [])[:10],
            "totes_les_estacions":  g.get("all_stations", []),
        }


# ── 2. Per parroquia ───────────────────────────────────────────────────────────

class ParishMinSensor(_FuelBase):
    """Preu mínim d'un combustible en una parròquia.
    El nom comença sempre per 'Parròquia' per agrupar-los junts a la UI.
    """

    def __init__(self, coordinator, entry_id, fuel_key, parish_name):
        super().__init__(coordinator, entry_id, fuel_key)
        self._parish = parish_name
        parish_s = _slug(parish_name)
        self._attr_unique_id = f"{DOMAIN}_parroquia_{parish_s}_{fuel_key}_min"
        self._attr_name = f"Parròquia {parish_name} {self._fuel_name} preu mínim"

    @property
    def _pd(self) -> dict:
        if not self.coordinator.data:
            return {}
        return self.coordinator.data.get(self._fuel_key, {}).get(self._parish, {})

    @property
    def native_value(self) -> float | None:
        return self._pd.get("min_price")

    @property
    def extra_state_attributes(self) -> dict:
        d = self._pd
        cheapest = d.get("cheapest")
        return {
            "estacio_mes_barata": cheapest.get("name") if cheapest else None,
            "preu_mes_car":       d.get("max_price"),
            "preu_mig":           d.get("avg_price"),
            "num_estacions":      d.get("num_stations", 0),
            "parroquia":          self._parish,
            "carburant":          self._fuel_name,
            "estacions":          sorted(
                d.get("stations", []),
                key=lambda s: s.get("price") or 9999,
            ),
        }


# ── 3. Gasolinera favorita ─────────────────────────────────────────────────────

class FavoriteStationSensor(
    CoordinatorEntity[AndorraCarburantsCoordinator], SensorEntity
):
    """Preu oficial i preu amb descompte d'una gasolinera concreta.

    Es crea un sensor per cada combinació estació × combustible configurat.
    Estat = preu oficial (€/L).
    El preu amb descompte s'exposa com a atribut.
    """

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UNIT

    def __init__(self, coordinator, entry_id, fav: dict, fuel_key: str):
        super().__init__(coordinator)
        self._fav = fav
        self._fuel_key = fuel_key
        station = fav[FAV_STATION_NAME]
        station_s = _slug(station)
        fuel_s = _slug(fuel_key)
        self._attr_unique_id = f"{DOMAIN}_fav_{station_s}_{fuel_s}"
        self._attr_name = f"{station} {FUEL_TYPES[fuel_key][1]}"
        self._attr_icon = FUEL_ICONS.get(fuel_key, "mdi:gas-station")
        self._attr_device_info = _device(entry_id)

    # ── Precio oficial ─────────────────────────────────────────────────────────

    @property
    def _official_price(self) -> float | None:
        """Busca el precio de la estación en el coordinator.

        Búsqueda exacta primero, luego parcial (case-insensitive).
        """
        if not self.coordinator.data:
            return None
        global_data = self.coordinator.data.get(self._fuel_key, {}).get("__global__", {})
        all_stations = global_data.get("all_stations", [])
        station_name = self._fav[FAV_STATION_NAME]
        name_lower = station_name.strip().lower()

        # 1. Coincidencia exacta
        for s in all_stations:
            if s["name"].strip().lower() == name_lower:
                return s["price"]

        # 2. Coincidencia parcial
        for s in all_stations:
            if name_lower in s["name"].strip().lower():
                return s["price"]

        _LOGGER.debug(
            "Estació '%s' no trobada per al combustible '%s'. "
            "Estacions disponibles: %s",
            station_name,
            self._fuel_key,
            [s["name"] for s in all_stations[:10]],
        )
        return None

    # ── Precio con descuento ───────────────────────────────────────────────────

    def _apply_discount(self, price: float) -> float:
        d_type = self._fav.get(FAV_DISCOUNT_TYPE, DISCOUNT_NONE)
        d_value = float(self._fav.get(FAV_DISCOUNT_VALUE, 0.0))
        if d_type == DISCOUNT_CENTS and d_value > 0:
            return round(price - d_value / 100, 4)
        if d_type == DISCOUNT_PERCENT and d_value > 0:
            return round(price * (1 - d_value / 100), 4)
        return price

    # ── HA properties ──────────────────────────────────────────────────────────

    @property
    def native_value(self) -> float | None:
        """Estat = preu amb descompte aplicat (o oficial si no hi ha descompte)."""
        official = self._official_price
        if official is None:
            return None
        return self._apply_discount(official)

    @property
    def extra_state_attributes(self) -> dict:
        official = self._official_price
        d_type = self._fav.get(FAV_DISCOUNT_TYPE, DISCOUNT_NONE)
        d_value = float(self._fav.get(FAV_DISCOUNT_VALUE, 0.0))

        discounted = self._apply_discount(official) if official is not None else None
        saving_l = round(official - discounted, 4) if (official and discounted) else 0.0
        saving_50l = round(saving_l * 50, 2) if saving_l else 0.0

        discount_label = {
            DISCOUNT_NONE:    "Sense descompte",
            DISCOUNT_CENTS:   f"−{d_value} ct/L",
            DISCOUNT_PERCENT: f"−{d_value}%",
        }.get(d_type, "")

        # Parroquia de la estación
        parish = None
        if self.coordinator.data:
            g = self.coordinator.data.get(self._fuel_key, {}).get("__global__", {})
            name_lower = self._fav[FAV_STATION_NAME].strip().lower()
            for s in g.get("all_stations", []):
                if s["name"].strip().lower() == name_lower or name_lower in s["name"].strip().lower():
                    parish = s.get("parish")
                    break

        return {
            "preu_oficial":        official,
            "preu_amb_descompte":  discounted,
            "estalvi_per_litre":   saving_l,
            "estalvi_diposit_50l": saving_50l,
            "descompte":           discount_label,
            "estacio":             self._fav[FAV_STATION_NAME],
            "parroquia":           parish,
            "carburant":           FUEL_TYPES[self._fuel_key][1],
        }
        