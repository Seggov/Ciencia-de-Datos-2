# Taller 2: Análisis Estacional y Predicción de Alta Demanda

**Integrantes:**
* Pedro Segovia — RUT 21672694-4 — C2
* Aurelie Lorena Saliou — RUT ficticio 40017078-9 — C2

---

## Objetivos

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
