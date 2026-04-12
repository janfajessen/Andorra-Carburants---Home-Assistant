# Andorra Fuel Prices — Custom Component for Home Assistant

###### Andorra Preus Carburants — Integració nativa per a Home Assistant
###### Andorra Precio Carburantes — Integración nativa para Home Assistant
###### Andorra Prix des Carburants — Intégration native pour Home Assistant
###### Andorra Preços dos Combustíveis — Integração nativa para Home Assistant

SP95 · SP98 · Gasoil · Gasoil Millorat · Calefacció botiga · Calefacció domicili

---

<details>
<summary>🇪🇸 Español</summary>

## Descripción

Integración nativa para Home Assistant que obtiene los precios de todos los combustibles de todas las parroquias de Andorra, sin scripts ni `command_line`.  
Fuente de datos: [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

## Instalación

### HACS (recomendado)
1. HACS → Integraciones → ⋮ → Repositorios personalizados
2. URL del repositorio · Categoría: **Integración**
3. Instala "Andorra Preus Carburants" y reinicia HA

### Manual
Copia `custom_components/andorra_carburants/` a `<config>/custom_components/` y reinicia.

## Configuración

**Configuración → Dispositivos y servicios → + Añadir → "Andorra Preus Carburants"**

### Paso 1 — Combustibles
| Campo | Descripción |
|-------|-------------|
| Combustibles | SP95 · SP98 · Gasoil · Gasoil Millorat · Calefacción botiga · Calefacción domicilio |
| Sensores por parroquia | Activa sensores para Canillo, Encamp, Ordino… (7 parroquias × combustible) |
| Intervalo (s) | Mínimo 3600. Por defecto 86400 (1 día) |

### Paso 2 — Gasolineras favoritas (opcional)
La integración hace una primera llamada a la API y muestra la lista real de estaciones disponibles. Puedes seleccionar tus gasolineras habituales y configurar descuentos.

**Descuentos conocidos pre-configurados:**
| Tarjeta | Gasolineras | Descuento |
|---------|------------|-----------|
| **My Pyri Pay** (Pyrénées) | Todas las **TotalEnergies** de Andorra | −4,8 ct/L |
| **My Pyri** (compra >50€ en Pyrénées) | **BP** y **Total** | −5% |
| **miBP** (app BP) | **BP** Andorra | Ver app |

Fuentes: [mypyri.ad/beneficis/total-energies](https://mypyri.ad/beneficis/total-energies)

## Sensores creados

**Sensores globales** `sensor.andorra_<combustible>_preu_minim`  
Estado = precio mínimo en todo el país (€/L).  
Atributos: `estacio_mes_barata` · `parroquia_mes_barata` · `preu_mig` · `top10_mes_barates` · `totes_les_estacions` · `data_actualitzacio`

**Sensores por parroquia** (si activados) `sensor.<parroquia>_<combustible>_preu_minim`  
Estado = precio mínimo de la parroquia.

**Sensores gasolinera favorita** `sensor.<nombre_estacion>_<combustible>`  
Estado = precio oficial (€/L).  
Atributos: `preu_amb_descompte` · `estalvi_per_litre` · `estalvi_diposit_50l` · `descompte` · `estacio` · `parroquia`

## IDs de producto de la API

| Clave | idProducte | Nombre | Verificado |
|-------|-----------|--------|-----------|
| sp95 | 4 | Gasolina 95 | ✅ |
| sp98 | 5 | Gasolina 98 | ✅ |
| gasoil | 6 | Gasoil | ✅ |
| gasoil_millorat | 7 | Gasoil Millorat | ⚠️ estimado |
| calefaccio_botiga | 8 | Calefacción botiga | ⚠️ estimado |
| calefaccio_domicili | 9 | Calefacción domicilio | ⚠️ estimado |

Los IDs marcados como estimados se han inferido por secuencia. Si un sensor queda `unavailable`, activa DEBUG en `configuration.yaml` y comprueba el HTML recibido para ajustar `const.py`.

## Depuración

```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

</details>

<details>
<summary>🇫🇷 Français</summary>

## Description

Intégration native pour Home Assistant qui récupère les prix de tous les carburants dans toutes les paroisses d'Andorre, sans scripts ni `command_line`.  
Source : [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

## Installation

### HACS (recommandé)
1. HACS → Intégrations → ⋮ → Dépôts personnalisés
2. URL du dépôt · Catégorie : **Intégration**
3. Installer « Andorra Preus Carburants » et redémarrer HA

### Manuel
Copiez `custom_components/andorra_carburants/` dans `<config>/custom_components/` et redémarrez.

## Configuration

**Paramètres → Appareils et services → + Ajouter → « Andorra Preus Carburants »**

### Étape 1 — Carburants
| Champ | Description |
|-------|-------------|
| Carburants | SP95 · SP98 · Gasoil · Gasoil Amélioré · Chauffage boutique · Chauffage domicile |
| Capteurs par paroisse | Active les capteurs pour Canillo, Encamp, Ordino… (7 paroisses × carburant) |
| Intervalle (s) | Minimum 3600. Par défaut 86400 (1 jour) |

### Étape 2 — Stations favorites (optionnel)
L'intégration effectue un premier appel à l'API et affiche la liste réelle des stations. Vous pouvez sélectionner vos stations habituelles et configurer des remises.

**Remises connues pré-configurées :**
| Carte | Stations | Remise |
|-------|---------|--------|
| **My Pyri Pay** (Pyrénées) | Toutes les **TotalEnergies** d'Andorre | −4,8 ct/L |
| **My Pyri** (achat >50€ aux Pyrénées) | **BP** et **Total** | −5% |
| **miBP** (app BP) | **BP** Andorre | Voir app |

## Capteurs créés

**Capteurs globaux** `sensor.andorra_<carburant>_preu_minim`  
État = prix minimum dans tout le pays (€/L).  
Attributs : `estacio_mes_barata` · `parroquia_mes_barata` · `preu_mig` · `top10_mes_barates` · `totes_les_estacions` · `data_actualitzacio`

**Capteurs par paroisse** (si activés) `sensor.<paroisse>_<carburant>_preu_minim`

**Capteurs station favorite** `sensor.<nom_station>_<carburant>`  
État = prix officiel (€/L).  
Attributs : `preu_amb_descompte` · `estalvi_per_litre` · `estalvi_diposit_50l` · `descompte` · `estacio` · `parroquia`

## Débogage

```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

</details>

<details>
<summary>🇬🇧 English</summary>

## Description

Native Home Assistant integration that fetches fuel prices for all fuel types across all parishes of Andorra. No scripts, no `command_line`.  
Data source: [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

## Installation

### HACS (recommended)
1. HACS → Integrations → ⋮ → Custom repositories
2. Repo URL · Category: **Integration**
3. Install "Andorra Preus Carburants" and restart HA

### Manual
Copy `custom_components/andorra_carburants/` to `<config>/custom_components/` and restart.

## Configuration

**Settings → Devices & services → + Add integration → "Andorra Preus Carburants"**

### Step 1 — Fuel types
| Field | Description |
|-------|-------------|
| Fuel types | SP95 · SP98 · Diesel · Premium Diesel · Heating oil (shop) · Heating oil (home) |
| Per-parish sensors | Enable sensors for Canillo, Encamp, Ordino… (7 parishes × fuel type) |
| Interval (s) | Minimum 3600. Default 86400 (1 day) |

### Step 2 — Favorite stations (optional)
The integration makes an initial API call and displays the real list of available stations. Select your usual stations and configure discounts.

**Pre-configured known discounts:**
| Card | Stations | Discount |
|------|---------|---------|
| **My Pyri Pay** (Pyrénées) | All **TotalEnergies** in Andorra | −4.8 ct/L |
| **My Pyri** (purchase >€50 at Pyrénées) | **BP** and **Total** | −5% |
| **miBP** (BP app) | **BP** Andorra | See app |

Sources: [mypyri.ad/beneficis/total-energies](https://mypyri.ad/beneficis/total-energies)

## Sensors created

**Global sensors** `sensor.andorra_<fuel>_preu_minim`  
State = cheapest price in the country (€/L).  
Attributes: `cheapest_station` · `cheapest_parish` · `avg_price` · `top10_cheapest` · `all_stations` · `date`

**Per-parish sensors** (if enabled) `sensor.<parish>_<fuel>_preu_minim`  
State = cheapest price in that parish.

**Favorite station sensors** `sensor.<station_name>_<fuel>`  
State = official price (€/L).  
Attributes: `price_with_discount` · `saving_per_litre` · `saving_50l_tank` · `discount` · `station` · `parish`

## API product IDs

| Key | idProducte | Name | Verified |
|-----|-----------|------|---------|
| sp95 | 4 | Unleaded 95 | ✅ |
| sp98 | 5 | Unleaded 98 | ✅ |
| gasoil | 6 | Diesel | ✅ |
| gasoil_millorat | 7 | Premium Diesel | ⚠️ estimated |
| calefaccio_botiga | 8 | Heating oil (shop) | ⚠️ estimated |
| calefaccio_domicili | 9 | Heating oil (home) | ⚠️ estimated |

## Debug

```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

</details>

<details>
<summary>🇵🇹 Português</summary>

## Descrição

Integração nativa para o Home Assistant que obtém os preços de todos os combustíveis em todas as paróquias de Andorra, sem scripts nem `command_line`.  
Fonte de dados: [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

## Instalação

### HACS (recomendado)
1. HACS → Integrações → ⋮ → Repositórios personalizados
2. URL do repositório · Categoria: **Integração**
3. Instalar "Andorra Preus Carburants" e reiniciar o HA

### Manual
Copiar `custom_components/andorra_carburants/` para `<config>/custom_components/` e reiniciar.

## Configuração

**Definições → Dispositivos e serviços → + Adicionar → "Andorra Preus Carburants"**

### Passo 1 — Combustíveis
| Campo | Descrição |
|-------|-----------|
| Combustíveis | SP95 · SP98 · Gasoil · Gasoil Melhorado · Aquecimento loja · Aquecimento domicílio |
| Sensores por paróquia | Ativa sensores para Canillo, Encamp, Ordino… (7 paróquias × combustível) |
| Intervalo (s) | Mínimo 3600. Por defeito 86400 (1 dia) |

### Passo 2 — Postos favoritos (opcional)
A integração faz uma primeira chamada à API e mostra a lista real de postos disponíveis. Pode selecionar os seus postos habituais e configurar descontos.

**Descontos conhecidos pré-configurados:**
| Cartão | Postos | Desconto |
|--------|-------|---------|
| **My Pyri Pay** (Pyrénées) | Todos os **TotalEnergies** de Andorra | −4,8 ct/L |
| **My Pyri** (compra >50€ nos Pyrénées) | **BP** e **Total** | −5% |
| **miBP** (app BP) | **BP** Andorra | Ver app |

## Sensores criados

**Sensores globais** `sensor.andorra_<combustivel>_preu_minim`  
Estado = preço mínimo no país (€/L).  
Atributos: `posto_mais_barato` · `paróquia_mais_barata` · `preço_médio` · `top10` · `todos_os_postos` · `data`

**Sensores por paróquia** (se ativados) `sensor.<paróquia>_<combustivel>_preu_minim`

**Sensores de posto favorito** `sensor.<nome_posto>_<combustivel>`  
Estado = preço oficial (€/L).  
Atributos: `preço_com_desconto` · `poupança_por_litro` · `poupança_depósito_50l` · `desconto` · `posto` · `paróquia`

## Depuração

```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

</details>

---

## Català

### Descripció

Integració nativa per a Home Assistant que obté els preus de tots els carburants de totes les parròquies d'Andorra. Sense scripts, sense `command_line`.

Font de dades: [sig.govern.ad/IPE/PreusCarburants](https://sig.govern.ad/IPE/PreusCarburants)

### Instal·lació

**Via HACS (recomanat)**
1. HACS → Integracions → ⋮ → Repositoris personalitzats
2. URL del repositori · Categoria: **Integració**
3. Instal·la "Andorra Preus Carburants" i reinicia HA

**Manual:** copia `custom_components/andorra_carburants/` a `<config>/custom_components/` i reinicia.

### Configuració

**Configuració → Dispositius i serveis → + Afegir → "Andorra Preus Carburants"**

**Pas 1 — Combustibles**

| Camp | Descripció |
|------|-----------|
| Combustibles | SP95 · SP98 · Gasoil · Gasoil Millorat · Calefacció botiga · Calefacció domicili |
| Sensors per parròquia | Activa sensors per Canillo, Encamp, Ordino… (7 parròquies × combustible) |
| Interval (s) | Mínim 3600. Per defecte 86400 (1 dia) |

**Pas 2 — Gasolineres favorites (opcional)**

La integració fa una primera crida a l'API i mostra la llista real d'estacions. Pots seleccionar les teves gasolineres habituals i configurar descomptes.

**Descomptes coneguts pre-configurats:**
| Targeta | Gasolineres | Descompte |
|---------|------------|-----------|
| **My Pyri Pay** (Pyrénées) | Totes les **TotalEnergies** d'Andorra | −4,8 ct/L |
| **My Pyri** (compra >50€ a Pyrénées) | **BP** i **Total** | −5% |
| **miBP** (app BP) | **BP** Andorra | Veure app |

Fonts: [mypyri.ad/beneficis/total-energies](https://mypyri.ad/beneficis/total-energies) · [ara.ad](https://www.ara.ad/economia/mypyri-tambe-pas-casa_1_4509681.html)

### Sensors creats

**Sensors globals** `sensor.andorra_<combustible>_preu_minim`  
Estat = preu mínim al país (€/L).  
Atributs: `estacio_mes_barata` · `parroquia_mes_barata` · `preu_mig` · `top10_mes_barates` · `totes_les_estacions` · `data_actualitzacio`

**Sensors per parròquia** (si activats) `sensor.<parroquia>_<combustible>_preu_minim`  
Estat = preu mínim de la parròquia.

**Sensors gasolinera favorita** `sensor.<nom_estacio>_<combustible>`  
Estat = preu oficial (€/L).

Exemple d'atributs:
```yaml
preu_oficial: 1.374
preu_amb_descompte: 1.326
estalvi_per_litre: 0.048
estalvi_diposit_50l: 2.40
descompte: "-4.8 ct/L"
estacio: "TotalEnergies - ARTAL 1"
parroquia: "Escaldes-Engordany"
carburant: "Gasolina 95"
```

### IDs de producte de l'API

| Clau | idProducte | Nom | Verificat |
|------|-----------|-----|-----------|
| sp95 | 4 | Gasolina 95 | ✅ |
| sp98 | 5 | Gasolina 98 | ✅ |
| gasoil | 6 | Gasoil | ✅ |
| gasoil_millorat | 7 | Gasoil Millorat | ⚠️ estimat |
| calefaccio_botiga | 8 | Calefacció botiga | ⚠️ estimat |
| calefaccio_domicili | 9 | Calefacció domicili | ⚠️ estimat |

Els IDs marcats com a estimats s'han inferit per seqüència. Si un sensor queda `unavailable`, activa DEBUG per veure el HTML retornat i ajusta `const.py`.

### Depuració
```yaml
logger:
  default: warning
  logs:
    custom_components.andorra_carburants: debug
```

### Exemple targeta Lovelace
```yaml
type: entities
title: Carburants Andorra
entities:
  - entity: sensor.andorra_gasolina_95_preu_minim
    name: SP95 mínim país
  - entity: sensor.andorra_gasoil_preu_minim
    name: Gasoil mínim país
  - entity: sensor.totalenergies_artal_1_gasolina_95
    name: TotalEnergies Artal (My Pyri Pay)
  - entity: sensor.bp_encamp_centre_gasolina_95
    name: BP Encamp (My Pyri)
```

### Crèdits

Basat en la integració `command_line` original de [@janfajessen](https://github.com/janfajessen), amb agraïments a *maniattico* del canal de Telegram [Domoticaencasa.es](https://t.me/domoticaencasa) pel descobriment de l'endpoint de l'API.
