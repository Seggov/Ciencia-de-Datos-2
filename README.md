# Taller 2: Análisis Estacional y Predicción de Alta Demanda

**Integrantes:**
* Pedro Segovia — RUT 21672694-4 — C2
* Aurelie Lorena Saliou — RUT ficticio 40017078-9 — C2

---

## Transformación de Datos: Archivo Antiguo (3.5 GB) vs Archivo Nuevo (35 KB)

En el archivo original de 3.5 GB cada fila correspondía a una prenda comprada, por lo que un solo día se repetía entre 40.000 y 50.000 veces. Para el objetivo del taller, se condensaron todas las compras de cada día en **1 sola fila resumen** con las características de calendario y la demanda diaria.

Ejemplo real con el día **20 de octubre de 2018 (`2018-10-20`)**:

### 1. Cómo se veía en el archivo antiguo de 3.5 GB (`transactions_train.csv`)
Para ese solo día habían **40.517 filas repetidas** como estas:

| t_dat | customer_id | article_id | price | sales_channel_id |
| :---: | :---: | :---: | :---: | :---: |
| `2018-10-20` | `000058a12d...` | `0663713001` | 0.0508 | 2 |
| `2018-10-20` | `000058a12d...` | `0541518023` | 0.0304 | 2 |
| `2018-10-20` | `00007d2de8...` | `0505221004` | 0.0152 | 2 |
| `2018-10-20` | `00083cda04...` | `0688873012` | 0.0304 | 1 |
| ... *(así 40.517 veces hacia abajo)* | ... | ... | ... | ... |

*(Tener 40.000 filas diciendo lo mismo sobre el calendario congelaría KNIME y distorsionaría el modelo).*

---

### 2. Cómo quedó en el archivo nuevo de 35 KB (`demanda_diaria.csv`)
Esas 40.517 filas se condensaron en **1 sola fila resumen**:

| fecha | demanda_diaria | dia_semana_num | dia_semana_nombre | dia_mes | mes | es_fin_de_semana | alta_demanda |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`2018-10-20`** | **`40517`** | `6` | `Sabado` | `20` | `10` | `1` | **`0`** |

* **`demanda_diaria = 40517`**: Es el conteo exacto de todas las compras ocurridas ese día.
* **`dia_semana_nombre = Sabado`** y **`dia_semana_num = 6`**: Extraído de la fecha.
* **`dia_mes = 20`**: Día 20 del mes.
* **`mes = 10`**: Octubre.
* **`es_fin_de_semana = 1`**: Porque fue sábado.
* **`alta_demanda = 0`**: Porque 40.517 estuvo por debajo del percentil 75 ($47.447,50$).

---

## Objetivos del Proyecto

### Objetivo general:
Analizar los patrones estacionales de las compras y estimar, mediante regresión logística, la probabilidad de que un día sea de alta demanda según sus características de calendario.

### Objetivos específicos:
1. Agrupar las transacciones por fecha y analizar la demanda diaria según el día de la semana, el día del mes y el mes del año.
2. Definir una variable binaria que identifique los días de alta demanda.
3. Entrenar y evaluar un modelo de regresión logística con variables de calendario e interpretar los patrones estacionales encontrados.

---

## Ubicación de los Datos

* **Data Original (Antigua):** `data/raw/transactions_train.csv` *(31.7M de compras, 3.5 GB - No se sube a GitHub por límite de tamaño)*
* **Data Procesada (Nueva para KNIME):** `data/processed/demanda_diaria.csv` *(734 días, 35 KB - Lista para usar en el flujo)*

---

## Encabezados: Antiguo vs Nuevo

| Dataset Antiguo (`transactions_train.csv`) | Dataset Nuevo (`demanda_diaria.csv`) | Descripción del cambio |
| :--- | :--- | :--- |
| `t_dat` | `fecha` | Fecha única agrupada por día. |
| *(conteo de filas por día)* | `demanda_diaria` | Total de compras/transacciones ocurridas ese día. |
| *(no existía)* | `dia_semana_num` | Día de la semana en número (1 = Lunes, ..., 7 = Domingo). |
| *(no existía)* | `dia_semana_nombre` | Nombre del día (Lunes, Martes, ..., Domingo). |
| *(no existía)* | `dia_mes` | Día del mes (1 al 31). |
| *(no existía)* | `mes` | Mes del año (1 al 12). |
| *(no existía)* | `es_fin_de_semana` | Variable binaria (1 si es Sábado/Domingo, 0 si no). |
| *(no existía)* | `alta_demanda` | Variable objetivo binaria (1 = Alta Demanda, 0 = Normal). |
| `customer_id` | *(eliminado)* | No se requiere para análisis de demanda diaria. |
| `article_id` | *(eliminado)* | No se requiere para análisis de demanda diaria. |
| `price` | *(eliminado)* | No se requiere para el recuento de compras. |
| `sales_channel_id` | *(eliminado)* | No se requiere para demanda global. |

---

## Clasificación Binaria (`alta_demanda`)

La clasificación de alta demanda se realizó mediante el **Percentil 75 ($Q_3$)** sobre la demanda diaria de todo el dataset:

* **Umbral:** $47.447,50$ transacciones.
  * **`1` (Alta Demanda):** Días con $47.448$ o más compras $\rightarrow$ **184 días (25,1%)**.
  * **`0` (Demanda Normal):** Días por debajo del umbral $\rightarrow$ **550 días (74,9%)**.

**¿Por qué se eligió el percentil?**
* **Inmune a outliers:** En retail existen eventos de venta extrema (*Black Friday*, *Cyber Monday*, que alcanzaron hasta 198.622 compras) que distorsionan e inflan el promedio. El percentil no se ve afectado por estos valores extremos.
* **Balance para el modelo:** Aísla el 25% de los días con mayor volumen comercial, generando una proporción adecuada (75% / 25%) para que la regresión logística aprenda a predecir la alta demanda sin desbalances excesivos.
