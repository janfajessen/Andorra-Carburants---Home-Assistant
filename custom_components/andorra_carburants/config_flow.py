"""Config Flow for Andorra Preus Carburants — HA 2026 compatible."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_FAVORITES,
    CONF_FUEL_TYPES,
    CONF_SCAN_INTERVAL,
    CONF_SHOW_PARISHES,
    DEFAULT_SCAN_INTERVAL,
    DISCOUNT_CENTS,
    DISCOUNT_NONE,
    DISCOUNT_PERCENT,
    DOMAIN,
    FAV_DISCOUNT_TYPE,
    FAV_DISCOUNT_VALUE,
    FAV_STATION_NAME,
    FUEL_TYPES,
    KNOWN_DISCOUNTS,
)
from .coordinator import AndorraCarburantsCoordinator

_LOGGER = logging.getLogger(__name__)

ALL_FUEL_KEYS = list(FUEL_TYPES.keys())
DEFAULT_FUEL_KEYS = ["sp95", "sp98", "gasoil"]


def _fuel_schema(
    default_fuels=None,
    default_parishes: bool = True,
    default_interval: int = DEFAULT_SCAN_INTERVAL,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_FUEL_TYPES, default=default_fuels or DEFAULT_FUEL_KEYS):
                SelectSelector(SelectSelectorConfig(
                    options=ALL_FUEL_KEYS,
                    multiple=True,
                    mode=SelectSelectorMode.LIST,
                )),
            vol.Optional(CONF_SHOW_PARISHES, default=default_parishes):
                BooleanSelector(),
            vol.Optional(CONF_SCAN_INTERVAL, default=default_interval):
                NumberSelector(NumberSelectorConfig(
                    min=3600, max=604800, step=3600, mode=NumberSelectorMode.BOX,
                )),
        }
    )


def _favorites_schema(station_list: list[str], current_favs: list[dict]) -> vol.Schema:
    """Schema del paso 2: solo selección de estaciones.

    El descuento se aplica automáticamente según el nombre (KNOWN_DISCOUNTS).
    """
    current_selected = [f[FAV_STATION_NAME] for f in current_favs]

    # Añadir ★ a las estaciones con descuento conocido
    options = []
    for s in station_list:
        hint = _discount_hint(s)
        options.append({"value": s, "label": f"{s}{hint}"})

    if not options:
        # Si la API no devolvió datos todavía, campo vacío
        return vol.Schema({
            vol.Optional("selected_stations", default=[]): SelectSelector(
                SelectSelectorConfig(options=[], multiple=True, mode=SelectSelectorMode.LIST)
            ),
            vol.Optional("discount_mypyri_pay", default=True): BooleanSelector(),
            vol.Optional("discount_mypyri", default=False): BooleanSelector(),
        })

    return vol.Schema({
        vol.Optional("selected_stations", default=current_selected):
            SelectSelector(SelectSelectorConfig(
                options=options,
                multiple=True,
                mode=SelectSelectorMode.LIST,
            )),
        vol.Optional("discount_mypyri_pay", default=True): BooleanSelector(),
        vol.Optional("discount_mypyri", default=False): BooleanSelector(),
    })


# ── Config Flow ───────────────────────────────────────────────────────────────

class AndorraCarburantsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow en 2 pasos."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}
        self._station_list: list[str] = []

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            fuel_types = user_input.get(CONF_FUEL_TYPES, [])
            if not fuel_types:
                errors[CONF_FUEL_TYPES] = "fuel_types_empty"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()

                user_input[CONF_SCAN_INTERVAL] = int(
                    user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
                self._data = user_input

                try:
                    coordinator = AndorraCarburantsCoordinator(
                        self.hass, fuel_types, user_input[CONF_SCAN_INTERVAL],
                    )
                    await coordinator.async_refresh()
                    self._station_list = coordinator.get_all_station_names()
                except Exception:  # noqa: BLE001
                    _LOGGER.warning("No se pudo precargar la lista de estaciones.")

                if self._station_list:
                    return await self.async_step_favorites()

                return self.async_create_entry(
                    title="Andorra Preus Carburants",
                    data={**self._data, CONF_FAVORITES: []},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_fuel_schema(),
            errors=errors,
        )

    async def async_step_favorites(self, user_input: dict | None = None) -> FlowResult:
        if user_input is not None:
            favorites = _build_favorites(
                user_input.get("selected_stations", []),
                user_input.get("discount_mypyri_pay", True),
                user_input.get("discount_mypyri", False),
            )
            return self.async_create_entry(
                title="Andorra Preus Carburants",
                data={**self._data, CONF_FAVORITES: favorites},
            )

        return self.async_show_form(
            step_id="favorites",
            data_schema=_favorites_schema(self._station_list, []),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AndorraCarburantsOptionsFlow()


# ── Options Flow — HA 2026: NO recibe config_entry en __init__ ────────────────

class AndorraCarburantsOptionsFlow(config_entries.OptionsFlow):
    """Options flow. En HA 2024+ self.config_entry se inyecta automáticamente."""

    def __init__(self) -> None:
        self._new_data: dict = {}
        self._station_list: list[str] = []

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            fuel_types = user_input.get(CONF_FUEL_TYPES, [])
            if not fuel_types:
                errors[CONF_FUEL_TYPES] = "fuel_types_empty"
            else:
                user_input[CONF_SCAN_INTERVAL] = int(
                    user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
                )
                self._new_data = user_input

                # Obtener lista de estaciones actual del coordinator
                coordinator: AndorraCarburantsCoordinator | None = (
                    self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
                )
                if coordinator:
                    self._station_list = coordinator.get_all_station_names()

                return await self.async_step_favorites()

        current_fuels = self.config_entry.data.get(CONF_FUEL_TYPES, DEFAULT_FUEL_KEYS)
        current_parishes = self.config_entry.data.get(CONF_SHOW_PARISHES, True)
        current_interval = self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=_fuel_schema(current_fuels, current_parishes, current_interval),
            errors=errors,
        )

    async def async_step_favorites(self, user_input: dict | None = None) -> FlowResult:
        current_favs = self.config_entry.data.get(CONF_FAVORITES, [])

        if user_input is not None:
            favorites = _build_favorites(
                user_input.get("selected_stations", []),
                user_input.get("discount_mypyri_pay", True),
                user_input.get("discount_mypyri", False),
            )
            return self.async_create_entry(
                title="",
                data={**self._new_data, CONF_FAVORITES: favorites},
            )

        return self.async_show_form(
            step_id="favorites",
            data_schema=_favorites_schema(self._station_list, current_favs),
        )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _discount_hint(station_name: str) -> str:
    """Añade ★ y el descuento si la estación tiene descuento conocido."""
    name_upper = station_name.upper()
    for key, info in KNOWN_DISCOUNTS.items():
        if key.upper() in name_upper:
            unit = "ct/L" if info["type"] == DISCOUNT_CENTS else "%"
            return f"  ★ −{info['value']}{unit}"
    return ""


def _build_favorites(
    selected: list[str],
    apply_mypyri_pay: bool,
    apply_mypyri: bool,
) -> list[dict]:
    """Construye la lista de favoritas aplicando descuentos automáticos por nombre."""
    favorites = []
    for station in selected:
        discount_type = DISCOUNT_NONE
        discount_value = 0.0
        station_upper = station.upper()

        if apply_mypyri_pay:
            for key, info in KNOWN_DISCOUNTS.items():
                if key.upper() in station_upper and info["card"] == "My Pyri Pay":
                    discount_type = info["type"]
                    discount_value = info["value"]
                    break

        if discount_type == DISCOUNT_NONE and apply_mypyri:
            for key, info in KNOWN_DISCOUNTS.items():
                if key.upper() in station_upper and "My Pyri" in info["card"]:
                    discount_type = info["type"]
                    discount_value = info["value"]
                    break

        favorites.append({
            FAV_STATION_NAME:   station,
            FAV_DISCOUNT_TYPE:  discount_type,
            FAV_DISCOUNT_VALUE: discount_value,
        })
    return favorites
    