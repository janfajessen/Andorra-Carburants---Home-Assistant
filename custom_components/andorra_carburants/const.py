"""Constants for Andorra Preus Carburants integration."""

DOMAIN = "andorra_carburants"

# Por defecto 1 vez al día (en segundos). Mínimo permitido: 3600 (1h)
DEFAULT_SCAN_INTERVAL = 86400

# API del Govern d'Andorra
# URL: https://sig.govern.ad/IPE/PreusCarburants/GetPreus?idProducte=X&data=YYYY-MM-DD 23:59:59&idParroquia=Y
BASE_URL = "https://sig.govern.ad/IPE/PreusCarburants/GetPreus"

# Parroquias: nombre → idParroquia
PARISHES = {
    "Canillo": 1,
    "Encamp": 2,
    "Ordino": 3,
    "La Massana": 4,
    "Andorra la Vella": 5,
    "Sant Julià de Lòria": 6,
    "Escaldes-Engordany": 7,
}

# Combustibles: clave interna → (idProducte, nombre visible)
# IDs 4, 5, 6 verificados. 7, 8, 9 estimados — el coordinator los marca como "unverified"
# y loguea un warning si no devuelven datos.
FUEL_TYPES = {
    "sp95":               (4, "Gasolina 95"),
    "sp98":               (5, "Gasolina 98"),
    "gasoil":             (6, "Gasoil"),
    "gasoil_millorat":    (7, "Gasoil Millorat"),
    "calefaccio_botiga":  (8, "Calefacció botiga"),
    "calefaccio_domicili":(9, "Calefacció domicili"),
}

FUEL_ICONS = {
    "sp95":               "mdi:gas-station",
    "sp98":               "mdi:gas-station",
    "gasoil":             "mdi:gas-station",
    "gasoil_millorat":    "mdi:gas-station",
    "calefaccio_botiga":  "mdi:home-thermometer-outline",
    "calefaccio_domicili":"mdi:home-thermometer",
}

# IDs no verificados — se loguea warning si no devuelven datos
FUEL_IDS_UNVERIFIED = {7, 8, 9}

# ── Descuentos conocidos ────────────────────────────────────────────────────
# Fuente: mypyri.ad/beneficis/total-energies + ara.ad
# Estructura: { "nombre_parcial_gasolinera": {"type": "cents", "value": X} }
# type: "cents"   → descuento en céntimos por litro (€/L × 0.01)
# type: "percent" → descuento en porcentaje del precio
KNOWN_DISCOUNTS: dict[str, dict] = {
    # My Pyri Pay: -4,8 ct/L en TODAS las TotalEnergies de Andorra
    "TotalEnergies": {"type": "cents",   "value": 4.8,  "card": "My Pyri Pay"},
    "Total":         {"type": "cents",   "value": 4.8,  "card": "My Pyri Pay"},
    # BP: -5% con My Pyri (compra >50€ en Pyrénées) o según miBP
    "BP":            {"type": "percent", "value": 5.0,  "card": "My Pyri / miBP"},
}

# ── Claves de configuración ─────────────────────────────────────────────────
CONF_FUEL_TYPES      = "fuel_types"
CONF_SCAN_INTERVAL   = "scan_interval"
CONF_SHOW_PARISHES   = "show_parish_sensors"
CONF_FAVORITES       = "favorites"   # lista de gasolineras favoritas con descuento

# Subcampos de cada favorita en CONF_FAVORITES
FAV_STATION_NAME     = "station"
FAV_DISCOUNT_TYPE    = "discount_type"   # "none" | "cents" | "percent"
FAV_DISCOUNT_VALUE   = "discount_value"  # float

DISCOUNT_NONE        = "none"
DISCOUNT_CENTS       = "cents"
DISCOUNT_PERCENT     = "percent"
