# Taller 2: Análisis Estacional y Predicción de Alta Demanda (H&M)

**Asignatura:** Ciencia de Datos 2  
**Integrantes:**
* Pedro Segovia — RUT 21672694-4 — C2
* Aurelie Lorena Saliou — RUT ficticio 40017078-9 — C2

---

## 1. Objetivos del Proyecto

### Objetivo General
Analizar los patrones estacionales de las compras y estimar, mediante **regresión logística**, la probabilidad de que un día sea de alta demanda según sus características de calendario.

### Objetivos Específicos
1. **Agrupación y Análisis Temporal:** Agrupar las transacciones por fecha y analizar el comportamiento de la demanda diaria según el día de la semana, el día del mes y el mes del año.
2. **Definición de la Variable Objetivo:** Definir una variable binaria formal que identifique de manera estadísticamente fundamentada los días de alta demanda.
3. **Modelado Predictivo e Interpretación:** Entrenar y evaluar un modelo de regresión logística con variables predictoras de calendario e interpretar los patrones estacionales y razones de momios (*odds ratios*) encontrados.

---

## 2. Decisiones Metodológicas Clave

Para abordar este taller de manera rigurosa, se definieron dos decisiones metodológicas centrales:

### Decisión A: Clasificación Binaria mediante el Percentil 75 ($Q_3$) MACRO (Global)

Para etiquetar la variable objetivo binaria (`alta_demanda`), se optó por un umbral **MACRO** basado en el **Percentil 75 ($Q_3$)** del volumen histórico de compras diarias:

$$\text{alta\_demanda} = \begin{cases} 1 & \text{si } \text{demanda\_diaria} \ge 47.447,50 \text{ compras} \\ 0 & \text{si } \text{demanda\_diaria} < 47.447,50 \text{ compras} \end{cases}$$

**Métricas empíricas obtenidas del dataset (734 días analizados, 31.788.324 transacciones):**
* **Mínimo:** 12.760 compras/día
* **Mediana ($P_{50}$):** 39.515,50 compras/día
* **Promedio ($\mu$):** 43.308,34 compras/día
* **Percentil 75 ($Q_3$):** **47.447,50 compras/día** (Umbral establecido)
* **Máximo:** 198.622 compras/día *(evidencia clara del efecto outlier como Black Friday/Cyber Days)*
* **Balance de clases:** Clase 0 (Normal): 550 días (74,9%) | Clase 1 (Alta demanda): 184 días (25,1%)

**Justificación de esta elección:**
1. **Robustez ante valores atípicos (*Outliers*):** En el comercio minorista de moda (*retail*), existen picos extraordinarios de consumo como *Black Friday*, *Cyber Monday* o liquidaciones de cambio de temporada. La media aritmética se ve fuertemente sesgada al alza por estos eventos extremos. El percentil 75, al ser una medida de posición no paramétrica, es inmune a distorsiones por valores atípicos y delimita de forma precisa la frontera de alta demanda.
2. **Representatividad de Negocio:** Desde una perspectiva operativa, si usáramos la media o la mediana, prácticamente la mitad de los días del año serían calificados como "alta demanda". El percentil 75 aísla con fidelidad el **cuartil superior (el 25% de los días con mayor presión operativa)**, reflejando momentos en los que la empresa requiere reforzar personal, inventario y logística.
3. **Salud del Balance de Clases para la Regresión Logística:** Garantiza una distribución natural de ~75% de días normales (clase 0) y ~25% de días de alta demanda (clase 1), permitiendo al modelo aprender los pesos de las variables de calendario sin sufrir desbalances extremos.
4. **Por qué MACRO y no MICRO para el modelo:** El umbral se calcula sobre la distribución total global. Si se aplicara un umbral micro (por ejemplo, definir alta demanda según el promedio de cada día de la semana por separado), se eliminaría artificialmente la estacionalidad que el modelo de regresión logística necesita aprender.

---

### Decisión B: Rol de los Promedios MICRO (Estacionales / Condicionales)

Si bien la variable dependiente del modelo se define a nivel macro, los **promedios MICRO** (promedio condicionado a un día de la semana específico, a una quincena o a un mes) cumplen un rol analítico clave:

1. **Análisis Exploratorio de Datos (EDA) e Hipótesis:** Permiten comprobar si existen efectos multiplicadores e interacciones. Por ejemplo, al evaluar si un sábado cercano al día 30 (fecha de pago) supera con creces el promedio histórico micro de los demás sábados.
2. **Fundamentación e Interpretación de Coeficientes:** Cuando la regresión logística arroje coeficientes positivos para ciertas fechas o meses (ej. noviembre o diciembre), los promedios micro permiten fundamentar cualitativamente en las conclusiones del informe *por qué* ese mes o día específico incrementa las probabilidades de venta en el negocio.

---

## 3. Estructura del Repositorio

```text
Ciencia-de-Datos-2/
├── .gitignore               # Excluye datasets crudos pesados (>100MB) y archivos temporales
├── README.md                # Documentación metodológica y objetivos del proyecto
├── OBJETIVO GENERAL.pdf     # Documento formal con la pauta de evaluación
├── data/
│   ├── raw/                 # transactions_train.csv (3.5 GB, ignorado por Git)
│   └── processed/           # demanda_diaria.csv (~734 filas, listo para KNIME y versionado en Git)
└── scripts/
    └── preprocesar.py       # Script en Python para agregación diaria y extracción de calendario
```

---

## 4. Flujo de Trabajo y Tecnologías

1. **Preprocesamiento Rápido (Python / Pandas):**
   * Agrupa las más de 31.7 millones de compras de `transactions_train.csv` en una serie temporal compacta de ~734 registros (`demanda_diaria.csv`).
   * Extrae las variables de calendario: `dia_semana_nombre`, `dia_semana_num`, `dia_mes`, `mes`, `es_fin_de_semana`.
   * Calcula el Percentil 75 y genera la columna binaria `alta_demanda`.
2. **Modelado y Visualización (KNIME Analytics Platform):**
   * Carga del archivo limpio `data/processed/demanda_diaria.csv`.
   * Partición de datos (entrenamiento / prueba).
   * Entrenamiento del modelo con `Logistic Regression Learner`.
   * Evaluación de desempeño con `Logistic Regression Predictor` y `Scorer`.
