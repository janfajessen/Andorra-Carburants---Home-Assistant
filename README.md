<div align="center">

# Andorra Fuel Prices <br> Home Assistant Integration

<img src="brands/icon@2x.png" width="250"/>

![Version](https://img.shields.io/badge/version-1.5.24-blue?style=for-the-badge)
![HA](https://img.shields.io/badge/Home%20Assistant-2024.1+-orange?style=for-the-badge&logo=home-assistant)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)
![HACS](https://img.shields.io/badge/HACS-Custom-41BDF5?style=for-the-badge&logo=homeassistantcommunitystore&logoColor=white)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-yellow?style=for-the-badge&logo=buymeacoffee)](https://www.buymeacoffee.com/janfajessen)
[![Patreon](https://img.shields.io/badge/Patreon-Support-red?style=for-the-badge&logo=patreon)](https://www.patreon.com/janfajessen)
<!--[![Ko-Fi](https://img.shields.io/badge/Ko--Fi-Support-teal?style=for-the-badge&logo=ko-fi)](https://ko-fi.com/janfajessen)
[![GitHub Sponsors](https://img.shields.io/badge/GitHub%20Sponsors-Support-pink?style=for-the-badge&logo=githubsponsors)](https://github.com/sponsors/janfajessen)
[![PayPal](https://img.shields.io/badge/PayPal-Donate-blue?style=for-the-badge&logo=paypal)](https://paypal.me/janfajessen)-->


**Seguiment en temps real dels preus de carburants de totes les estacions de servei del Principat d'Andorra.**  
Sense scripts, sense `command_line`. Integració nativa amb Config Flow, dispositius i sensors.

Font oficial: [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

</div>

---

<details>
<summary>🇪🇸 &nbsp;<b>Español</b></summary>

## Descripción

Integración nativa para Home Assistant que obtiene los precios de **todos los combustibles** de **todas las parroquias** de Andorra en tiempo real. Sin scripts ni `command_line`.

Permite configurar **gasolineras favoritas con descuentos personalizados** — con soporte automático para My Pyri Pay (TotalEnergies) y My Pyri/miBP (BP).

## Instalación

### HACS (recomendado)
1. HACS → Integraciones → ⋮ → Repositorios personalizados
2. Pega la URL del repositorio · Categoría: **Integración**
3. Instala "Andorra Preus Carburants" y reinicia Home Assistant
<img src="brands/icon@2x.png" width="100"/> 

### Manual
Copia la carpeta `custom_components/andorra_carburants/` a `<config>/custom_components/` y reinicia.

## Configuración

**Ajustes → Dispositivos y servicios → + Añadir → "Andorra Preus Carburants"**

### Paso 1 — Combustibles
| Campo | Descripción | Por defecto |
|-------|-------------|-------------|
| Combustibles | SP95 · SP98 · Gasoil · Gasoil Millorat · Calefacción botiga · Calefacción domicilio | SP95, SP98, Gasoil |
| Sensores por parroquia | Crea sensores individuales para cada una de las 7 parroquias | Activado |
| Intervalo (s) | Cada cuántos segundos actualizar (mínimo 3600 = 1h) | 86400 (1 día) |

### Paso 2 — Gasolineras favoritas
La integración hace una primera llamada a la API y muestra la **lista real** de estaciones disponibles. Puedes seleccionar varias y el sistema aplica automáticamente los descuentos conocidos.

### Descuentos conocidos
| Tarjeta | Gasolineras | Descuento |
|---------|------------|-----------|
| **My Pyri Pay** | Todas las **TotalEnergies** de Andorra | −4,8 ct/L |
| **My Pyri** | **BP** y **Total** | −5% |

## Sensores

| Sensor | Estado | Descripción |
|--------|--------|-------------|
| `sensor.andorra_<combustible>_preu_minim` | €/L | Precio mínimo en todo el país |
| `sensor.parroquia_<parroquia>_<combustible>_preu_minim` | €/L | Precio mínimo por parroquia |
| `sensor.<estacion>_<combustible>` | €/L | Precio con descuento de gasolinera favorita |

## Automatizaciones de ejemplo

### Notificación cuando el SP95 baje de umbral
```yaml
automation:
  - alias: "Alerta SP95 barato"
    trigger:
      - platform: numeric_state
        entity_id: sensor.andorra_gasolina_95_preu_minim
        below: 1.35
    action:
      - service: notify.telegram_jan
        data:
          message: >
            ⛽ SP95 a {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L
            a {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
            ({{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'parroquia_mes_barata') }})
```

### Informe diario de precios por Telegram
```yaml
automation:
  - alias: "Informe diari carburants"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.telegram_jan
        data:
          message: >
            ⛽ Preus carburants Andorra avui:
            • SP95: {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L
            • SP98: {{ states('sensor.andorra_gasolina_98_preu_minim') }} €/L
            • Gasoil: {{ states('sensor.andorra_gasoil_preu_minim') }} €/L
            📍 Més barata: {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
```

</details>

---

<details>
<summary>🇫🇷 &nbsp;<b>Français</b></summary>

## Description

Intégration native pour Home Assistant qui récupère les prix de **tous les carburants** dans **toutes les paroisses** d'Andorre en temps réel. Sans scripts ni `command_line`.

Permet de configurer des **stations favorites avec des remises personnalisées** — avec support automatique pour My Pyri Pay (TotalEnergies) et My Pyri/miBP (BP).

## Installation

### HACS (recommandé)
1. HACS → Intégrations → ⋮ → Dépôts personnalisés
2. Collez l'URL du dépôt · Catégorie : **Intégration**
3. Installez « Andorra Preus Carburants » et redémarrez Home Assistant
<img src="brands/icon@2x.png" width="100"/> 

### Manuel
Copiez le dossier `custom_components/andorra_carburants/` dans `<config>/custom_components/` et redémarrez.

## Configuration

**Paramètres → Appareils et services → + Ajouter → « Andorra Preus Carburants »**

### Étape 1 — Carburants
| Champ | Description | Par défaut |
|-------|-------------|-----------|
| Carburants | SP95 · SP98 · Gasoil · Gasoil Amélioré · Chauffage boutique · Chauffage domicile | SP95, SP98, Gasoil |
| Capteurs par paroisse | Crée des capteurs individuels pour chacune des 7 paroisses | Activé |
| Intervalle (s) | Fréquence de mise à jour (minimum 3600 = 1h) | 86400 (1 jour) |

### Étape 2 — Stations favorites
L'intégration effectue un premier appel à l'API et affiche la **liste réelle** des stations. Sélectionnez vos habituelles et les remises connues sont appliquées automatiquement.

### Remises connues
| Carte | Stations | Remise |
|-------|---------|--------|
| **My Pyri Pay** | Toutes les **TotalEnergies** d'Andorre | −4,8 ct/L |
| **My Pyri** | **BP** et **Total** | −5% |

## Capteurs

| Capteur | État | Description |
|---------|------|-------------|
| `sensor.andorra_<carburant>_preu_minim` | €/L | Prix minimum dans tout le pays |
| `sensor.parroquia_<paroisse>_<carburant>_preu_minim` | €/L | Prix minimum par paroisse |
| `sensor.<station>_<carburant>` | €/L | Prix avec remise de la station favorite |

## Exemple d'automatisation — Alerte prix bas

```yaml
automation:
  - alias: "Alerte SP95 bas"
    trigger:
      - platform: numeric_state
        entity_id: sensor.andorra_gasolina_95_preu_minim
        below: 1.35
    action:
      - service: notify.mobile_app
        data:
          message: >
            ⛽ SP95 à {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L
            à {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
```

</details>

---

<details>
<summary>🇬🇧 &nbsp;<b>English</b></summary>

## Description

Native Home Assistant integration that fetches **all fuel prices** from **all parishes** in Andorra in real time. No scripts, no `command_line`.

Supports **favorite gas stations with custom discounts** — with automatic support for My Pyri Pay (TotalEnergies) and My Pyri/miBP (BP).

## Installation

### HACS (recommended)
1. HACS → Integrations → ⋮ → Custom repositories
2. Paste the repository URL · Category: **Integration**
3. Install "Andorra Preus Carburants" and restart Home Assistant
<img src="brands/icon@2x.png" width="100"/> 

### Manual
Copy the `custom_components/andorra_carburants/` folder to `<config>/custom_components/` and restart.

## Configuration

**Settings → Devices & services → + Add integration → "Andorra Preus Carburants"**

### Step 1 — Fuel types
| Field | Description | Default |
|-------|-------------|---------|
| Fuel types | SP95 · SP98 · Diesel · Premium Diesel · Heating oil (shop) · Heating oil (home) | SP95, SP98, Diesel |
| Per-parish sensors | Creates individual sensors for each of the 7 parishes | Enabled |
| Interval (s) | Update frequency (minimum 3600 = 1h) | 86400 (1 day) |

### Step 2 — Favorite stations
The integration makes an initial API call and shows the **real list** of available stations. Select yours and known discounts are applied automatically.

### Known discounts
| Card | Stations | Discount |
|------|---------|---------|
| **My Pyri Pay** | All **TotalEnergies** in Andorra | −4.8 ct/L |
| **My Pyri** | **BP** and **Total** | −5% |

## Sensors

| Sensor | State | Description |
|--------|-------|-------------|
| `sensor.andorra_<fuel>_preu_minim` | €/L | Cheapest price in the country |
| `sensor.parroquia_<parish>_<fuel>_preu_minim` | €/L | Cheapest price per parish |
| `sensor.<station>_<fuel>` | €/L | Discounted price of favorite station |

## Example automation — Low price alert

```yaml
automation:
  - alias: "SP95 low price alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.andorra_gasolina_95_preu_minim
        below: 1.35
    action:
      - service: notify.mobile_app
        data:
          message: >
            ⛽ SP95 at {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L
            at {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
            ({{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'parroquia_mes_barata') }})
```

## Debugging

```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

</details>

---

<details>
<summary>🇵🇹 &nbsp;<b>Português</b></summary>

## Descrição

Integração nativa para Home Assistant que obtém os preços de **todos os combustíveis** em **todas as paróquias** de Andorra em tempo real. Sem scripts nem `command_line`.

Permite configurar **postos favoritos com descontos personalizados** — com suporte automático para My Pyri Pay (TotalEnergies) e My Pyri/miBP (BP).

## Instalação

### HACS (recomendado)
1. HACS → Integrações → ⋮ → Repositórios personalizados
2. Cole o URL do repositório · Categoria: **Integração**
3. Instale "Andorra Preus Carburants" e reinicie o Home Assistant
<img src="brands/icon@2x.png" width="100"/> 

### Manual
Copie a pasta `custom_components/andorra_carburants/` para `<config>/custom_components/` e reinicie.

## Configuração

**Definições → Dispositivos e serviços → + Adicionar → "Andorra Preus Carburants"**

### Passo 1 — Combustíveis
| Campo | Descrição | Padrão |
|-------|-----------|--------|
| Combustíveis | SP95 · SP98 · Gasoil · Gasoil Melhorado · Aquecimento loja · Aquecimento domicílio | SP95, SP98, Gasoil |
| Sensores por paróquia | Cria sensores individuais para cada uma das 7 paróquias | Ativado |
| Intervalo (s) | Frequência de atualização (mínimo 3600 = 1h) | 86400 (1 dia) |

### Passo 2 — Postos favoritos
A integração faz uma primeira chamada à API e mostra a **lista real** de postos disponíveis. Selecione os seus e os descontos conhecidos são aplicados automaticamente.

### Descontos conhecidos
| Cartão | Postos | Desconto |
|--------|-------|---------|
| **My Pyri Pay** | Todos os **TotalEnergies** de Andorra | −4,8 ct/L |
| **My Pyri** | **BP** e **Total** | −5% |

## Sensores

| Sensor | Estado | Descrição |
|--------|--------|-----------|
| `sensor.andorra_<combustivel>_preu_minim` | €/L | Preço mínimo no país |
| `sensor.parroquia_<paroquia>_<combustivel>_preu_minim` | €/L | Preço mínimo por paróquia |
| `sensor.<posto>_<combustivel>` | €/L | Preço com desconto do posto favorito |

</details>

---

## Descripció

Integració nativa per a Home Assistant que obté els preus de **tots els carburants** de **totes les parròquies** d'Andorra en temps real. Sense scripts, sense `command_line`. Integració completa amb Config Flow, dispositiu únic i sensors individuals per parròquia i per estació.

## Instal·lació

### Via HACS (recomanat)

1. HACS → Integracions → ⋮ → Repositoris personalitzats
2. Enganxa la URL del repositori · Categoria: **Integració**
3. Instal·la "Andorra Preus Carburants" i reinicia Home Assistant
<img src="brands/icon@2x.png" width="100"/> 

### Manual

Copia la carpeta `custom_components/andorra_carburants/` a `<config>/custom_components/` i reinicia.

---

## Configuració

**Configuració → Dispositius i serveis → + Afegir → "Andorra Preus Carburants"**

### Pas 1 — Combustibles

| Camp | Descripció | Per defecte |
|------|-----------|-------------|
| Combustibles | SP95 · SP98 · Gasoil · Gasoil Millorat · Calefacció botiga · Calefacció domicili | SP95, SP98, Gasoil |
| Sensors per parròquia | Crea sensors individuals per a cadascuna de les 7 parròquies | Activat |
| Interval (s) | Cada quants segons actualitzar (mínim 3600 = 1h) | 86400 (1 dia) |

### Pas 2 — Gasolineres favorites

La integració fa una primera crida a la API i mostra la **llista real** d'estacions disponibles al país. Selecciona les teves habituals i el sistema aplica automàticament els descomptes coneguts (indicats amb ★).

### Descomptes coneguts pre-configurats

| Targeta | Gasolineres | Descompte | Font |
|---------|------------|-----------|------|
| **My Pyri Pay** (Pyrénées) | Totes les **TotalEnergies** d'Andorra | −4,8 ct/L | [mypyri.ad](https://mypyri.ad/beneficis/total-energies) |
| **My Pyri** (compra >50€) | **BP** i **Total** | −5% | [ara.ad](https://www.ara.ad/economia/mypyri-tambe-pas-casa_1_4509681.html) |

---

## Sensors creats

### Sensors globals (1 per combustible)

`sensor.andorra_<combustible>_preu_minim`

| Atribut | Descripció |
|---------|-----------|
| `estacio_mes_barata` | Nom de l'estació amb el preu més baix |
| `parroquia_mes_barata` | Parròquia on es troba |
| `preu_mes_car` | Preu màxim del dia |
| `preu_mig` | Mitjana de totes les estacions |
| `num_estacions` | Nombre d'estacions amb dades |
| `top10_mes_barates` | Llista de les 10 més barates (amb parròquia) |
| `totes_les_estacions` | Llista completa ordenada per preu |
| `data_actualitzacio` | Data de les dades |

### Sensors per parròquia (si activats)

`sensor.parroquia_<parroquia>_<combustible>_preu_minim`

Disponibles per a: Canillo · Encamp · Ordino · La Massana · Andorra la Vella · Sant Julià de Lòria · Escaldes-Engordany

### Sensors gasolinera favorita

`sensor.<nom_estacio>_<combustible>`

| Atribut | Descripció |
|---------|-----------|
| `preu_oficial` | Preu publicat a la API (€/L) |
| `preu_amb_descompte` | Preu real aplicant el descompte (€/L) |
| `estalvi_per_litre` | Estalvi per litre (€) |
| `estalvi_diposit_50l` | Estalvi estimat per a un dipòsit de 50L (€) |
| `descompte` | Descripció del descompte aplicat |
| `estacio` | Nom de l'estació |
| `parroquia` | Parròquia de l'estació |
| `carburant` | Tipus de combustible |

---

## IDs de producte de la API

| Clau | `idProducte` | Nom | Verificat |
|------|-------------|-----|-----------|
| `sp95` | 4 | Gasolina sense plom 95 octans | ✅ |
| `sp98` | 5 | Gasolina sense plom 98 octans | ✅ |
| `gasoil` | 6 | Gasoil de locomoció | ✅ |
| `gasoil_millorat` | 7 | Gasoil de locomoció millorat | ⚠️ estimat |
| `calefaccio_botiga` | 8 | Gasoil calefacció botiga | ⚠️ estimat |
| `calefaccio_domicili` | 9 | Gasoil calefacció domicili | ⚠️ estimat |

> Els IDs marcats com a estimats s'han inferit per seqüència. Si un sensor queda `unavailable`, activa DEBUG i comprova el HTML retornat per ajustar `const.py`.

---

## Targetes Lovelace

### Resum nacional — Entities card

```yaml
type: entities
title: ⛽ Carburants Andorra
icon: mdi:gas-station
entities:
  - entity: sensor.andorra_gasolina_95_preu_minim
    name: SP95 — mínim país
    icon: mdi:gas-station
  - entity: sensor.andorra_gasolina_98_preu_minim
    name: SP98 — mínim país
    icon: mdi:gas-station
  - entity: sensor.andorra_gasoil_preu_minim
    name: Gasoil — mínim país
    icon: mdi:gas-station
  - type: attribute
    entity: sensor.andorra_gasolina_95_preu_minim
    attribute: estacio_mes_barata
    name: Estació més barata (SP95)
    icon: mdi:map-marker
  - type: attribute
    entity: sensor.andorra_gasolina_95_preu_minim
    attribute: parroquia_mes_barata
    name: Parròquia
    icon: mdi:map
```

---

### Les meves gasolineres — amb descompte

```yaml
type: entities
title: 🏷️ Les meves gasolineres
entities:
  - entity: sensor.totalenergies_artal_1_gasolina_95
    name: TotalEnergies Artal (My Pyri Pay)
    icon: mdi:gas-station
  - type: attribute
    entity: sensor.totalenergies_artal_1_gasolina_95
    attribute: preu_oficial
    name: Preu oficial
  - type: attribute
    entity: sensor.totalenergies_artal_1_gasolina_95
    attribute: descompte
    name: Descompte aplicat
  - type: attribute
    entity: sensor.totalenergies_artal_1_gasolina_95
    attribute: estalvi_diposit_50l
    name: Estalvi dipòsit 50L
    icon: mdi:piggy-bank
  - entity: sensor.andorracing_experience_gasolina_95
    name: Andorracing Experience
    icon: mdi:gas-station
```

---

### Per parròquia — Glance card

```yaml
type: glance
title: 🗺️ SP95 per parròquia
columns: 3
entities:
  - entity: sensor.parroquia_andorra_la_vella_gasolina_95_preu_minim
    name: And. la Vella
  - entity: sensor.parroquia_escaldes_engordany_gasolina_95_preu_minim
    name: Escaldes
  - entity: sensor.parroquia_encamp_gasolina_95_preu_minim
    name: Encamp
  - entity: sensor.parroquia_la_massana_gasolina_95_preu_minim
    name: La Massana
  - entity: sensor.parroquia_ordino_gasolina_95_preu_minim
    name: Ordino
  - entity: sensor.parroquia_canillo_gasolina_95_preu_minim
    name: Canillo
  - entity: sensor.parroquia_sant_julia_de_loria_gasolina_95_preu_minim
    name: Sant Julià
```

---

### Top 10 més barates — Markdown card

```yaml
type: markdown
title: 🏆 Top 10 SP95 més barates avui
content: >
  {% set top = state_attr('sensor.andorra_gasolina_95_preu_minim', 'top10_mes_barates') %}
  {% if top %}
  | # | Estació | Parròquia | €/L |
  |---|---------|-----------|-----|
  {% for s in top %}
  | {{ loop.index }} | {{ s.name }} | {{ s.parish }} | **{{ s.price }}** |
  {% endfor %}
  {% else %}
  Sense dades
  {% endif %}
```

---

### Estalvi repostar — Markdown card

```yaml
type: markdown
title: 💰 Estalvi repostant amb descompte
content: >
  {% set oficial = state_attr('sensor.totalenergies_artal_1_gasolina_95', 'preu_oficial') %}
  {% set descompte = states('sensor.totalenergies_artal_1_gasolina_95') | float(0) %}
  {% set desc_label = state_attr('sensor.totalenergies_artal_1_gasolina_95', 'descompte') %}
  {% if oficial %}

  **TotalEnergies Artal 1 — SP95**

  | | €/L |
  |-|-----|
  | Preu oficial | {{ oficial }} |
  | Preu amb {{ desc_label }} | **{{ descompte }}** |
  | Estalvi 40L | {{ ((oficial - descompte) * 40) | round(2) }} € |
  | Estalvi 60L | {{ ((oficial - descompte) * 60) | round(2) }} € |

  {% endif %}
```

---

## Automatitzacions

### Alerta quan el SP95 baixi de preu

```yaml
automation:
  - alias: "⛽ Alerta SP95 barat"
    description: "Notifica quan el SP95 baixa d'un preu determinat"
    trigger:
      - platform: numeric_state
        entity_id: sensor.andorra_gasolina_95_preu_minim
        below: 1.35
    action:
      - service: notify.telegram_jan
        data:
          message: >
            ⛽ El SP95 ha baixat a {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L!

            📍 Estació més barata:
            {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
            ({{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'parroquia_mes_barata') }})

            📊 Preu mig: {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'preu_mig') }} €/L
```

---

### Informe matinal de preus per Telegram

```yaml
automation:
  - alias: "📊 Informe diari carburants"
    description: "Envia un resum de preus cada matí"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.telegram_jan
        data:
          message: >
            ⛽ Preus carburants Andorra — {{ now().strftime('%d/%m/%Y') }}

            🟢 SP95:   {{ states('sensor.andorra_gasolina_95_preu_minim') }} €/L
            🔵 SP98:   {{ states('sensor.andorra_gasolina_98_preu_minim') }} €/L
            🟡 Gasoil: {{ states('sensor.andorra_gasoil_preu_minim') }} €/L

            📍 Més barata SP95:
            {{ state_attr('sensor.andorra_gasolina_95_preu_minim', 'estacio_mes_barata') }}
            ({{ state_attr('sensor.andorra_gasolina_95_
```


### Crèdits

Basat en la integració `command_line` original de [@janfajessen](https://github.com/janfajessen), amb agraïments a *maniattico* del canal de Telegram [Domoticaencasa.es](https://t.me/domoticaencasa) pel descobriment de l'endpoint de l'API.
