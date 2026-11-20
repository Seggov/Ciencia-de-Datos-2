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


# Análisis de la demanda diaria y modelos de regresión logística

## 1. Análisis exploratorio de los datos

### 1.1. Descripción de la variable estudiada

La demanda diaria corresponde al número de prendas vendidas por día. Para este estudio, se dispone de datos correspondientes a un período de dos años, comprendido entre el 20 de septiembre de 2018 y el 22 de septiembre de 2020.

El objetivo de este análisis es estudiar la evolución de la demanda diaria, identificar posibles patrones temporales y determinar si las características del calendario permiten predecir los días de alta demanda.

### 1.2. Análisis de la demanda según las características del calendario

#### Gráfico 1. Mediana de la demanda diaria según el día del mes

<img width="1500" height="1050" alt="Mediana de la demanda diaria según el día del mes" src="https://github.com/user-attachments/assets/754175cb-f03d-4a70-a914-bfd2efbf61c5" />

Se observan variaciones relativamente pequeñas entre los distintos días del mes. No existe una tendencia claramente definida que permita identificar determinados días como sistemáticamente asociados a una mayor demanda.

Por este motivo, consideramos que el día del mes no constituye una variable suficientemente relevante para nuestro modelo de regresión logística y decidimos no incluirla entre las variables explicativas.

Este análisis se relaciona con el objetivo específico 1.

*Fuente: elaboración propia a partir de los cálculos realizados en KNIME con el dataset de H&M.*

#### Gráfico 2. Promedio de la demanda diaria según el mes

<img width="1500" height="1050" alt="Promedio de la demanda diaria según el mes" src="https://github.com/user-attachments/assets/1f7dc452-eb69-43a5-bde6-b41c817047d3" />

El gráfico muestra diferencias importantes en la demanda media según el mes del año.

En particular, se observa que:

- Junio presenta una demanda media especialmente elevada.
- Julio también registra un nivel de demanda importante.
- Abril y mayo muestran niveles de demanda relativamente altos.
- Diciembre presenta una demanda media más baja.

Estas diferencias sugieren la existencia de cierta estacionalidad en las ventas. Por lo tanto, decidimos conservar la variable correspondiente al mes del año para estudiar su capacidad predictiva respecto a los días de alta demanda.

Este análisis se relaciona con el objetivo específico 1.

*Fuente: elaboración propia a partir de los cálculos realizados en KNIME con el dataset de H&M.*

#### Gráfico 3. Distribución de la demanda diaria según el día de la semana

<img width="1500" height="1050" alt="Distribución de la demanda diaria según el día de la semana" src="https://github.com/user-attachments/assets/ea5414b2-9233-42d2-91b9-1953d708acf1" />

El diagrama de cajas permite observar diferencias en la distribución de la demanda diaria según el día de la semana.

En particular:

- El miércoles presenta una mediana relativamente elevada.
- El jueves y el sábado también muestran niveles de demanda importantes.
- El domingo presenta una mediana de demanda más baja.
- El lunes y el viernes muestran distribuciones relativamente similares.

Aunque las diferencias no son necesariamente suficientes para explicar por sí solas las variaciones de la demanda, estos resultados sugieren que el día de la semana podría aportar información útil para la predicción.

Por este motivo, decidimos conservar esta variable en nuestros modelos de regresión logística.

Este análisis se relaciona con el objetivo específico 1.

*Fuente: elaboración propia a partir de los cálculos realizados en KNIME con el dataset de H&M.*

#### Gráfico 4. Distribución de la demanda diaria

<img width="1500" height="1050" alt="Distribución de la demanda" src="https://github.com/user-attachments/assets/aa73ef8c-cb58-4c6a-95af-0f19e73a50dc" />

La distribución de la demanda diaria presenta una marcada asimetría positiva, es decir, una concentración de observaciones en los valores más bajos y una cola extendida hacia los valores elevados.

La mayoría de los días registra una demanda comprendida aproximadamente entre 30.000 y 50.000 prendas. Sin embargo, también se observan algunos días con valores excepcionalmente elevados, que pueden acercarse a las 200.000 prendas.

Esta distribución pone de manifiesto la presencia de valores extremos, que deben tenerse en cuenta al definir la variable objetivo de nuestro modelo.

Por este motivo, decidimos utilizar el percentil 75 para identificar los días de alta demanda. Este criterio permite seleccionar el 25 % de los días con mayor demanda, tomando como referencia la distribución observada en los datos de entrenamiento, y evita que la definición de la variable objetivo dependa de un umbral arbitrario.

Este análisis se relaciona con el objetivo específico 1.

*Fuente: elaboración propia a partir de los cálculos realizados en KNIME con el dataset de H&M. Nodo de expresión 38.*

#### Gráfico 5. Evolución de la demanda diaria durante el período estudiado

<img width="1500" height="1050" alt="Distribución de la demanda en función de los días" src="https://github.com/user-attachments/assets/17648844-74c4-4247-ae2b-774eaaabc9d8" />

Al observar la evolución de la demanda diaria durante los dos años estudiados, se aprecia que los días de demanda excepcionalmente elevada no parecen concentrarse exclusivamente en un período concreto.

También se identifican tendencias relativamente similares entre ambos años, aunque el nivel de demanda del primer año parece ser ligeramente superior al del segundo.

Esta observación justifica la utilización de una separación cronológica entre los datos de entrenamiento y los datos de prueba, con el fin de evaluar la capacidad del modelo para generalizar sus predicciones a un período posterior.

Este análisis se relaciona con el objetivo específico 1.

*Fuente: elaboración propia a partir de los cálculos realizados en KNIME con el dataset de H&M. Nodo de expresión 21.*

---

## 2. Construcción de los modelos de regresión logística

### 2.1. Definición de la variable objetivo

Para construir nuestros modelos, definimos una variable binaria denominada `alta_demanda`, que permite distinguir entre días de demanda normal y días de alta demanda.

Se establece como criterio de clasificación el percentil 75 de la demanda diaria. De este modo:

- **Alta demanda (1):** días cuya demanda diaria es igual o superior al percentil 75.
- **Demanda normal (0):** días cuya demanda diaria es inferior al percentil 75.

Es importante señalar que el percentil 75 se calcula únicamente a partir de los datos de entrenamiento. Posteriormente, se aplica el mismo umbral a los datos de prueba.

Esta metodología permite evitar la fuga de información (*data leakage*), ya que el modelo no utiliza información procedente del período de prueba para definir la variable que debe predecir.

### 2.2. Separación de los datos

Para evaluar la capacidad predictiva de los modelos, dividimos los datos cronológicamente en dos conjuntos:

- **Conjunto de entrenamiento:** primer año de observaciones.
- **Conjunto de prueba:** segundo año de observaciones.

Esta separación permite evaluar la capacidad del modelo para predecir la demanda en un período posterior al utilizado durante su entrenamiento.

A diferencia de una separación aleatoria, este procedimiento reproduce mejor una situación real de predicción, en la que se utilizan datos históricos para anticipar la demanda futura.

### 2.3. Variables explicativas y modelos desarrollados

A partir del análisis exploratorio, decidimos desarrollar tres modelos de regresión logística para estudiar la influencia de las características temporales sobre la probabilidad de registrar un día de alta demanda.

Las variables categóricas se transformaron mediante la técnica *One Hot Encoding*, con el objetivo de representar cada categoría mediante variables binarias.

Los tres modelos son los siguientes:

- **Modelo 1: mes del año.** Utiliza únicamente el mes como variable explicativa.
- **Modelo 2: día de la semana.** Utiliza únicamente el día de la semana como variable explicativa. Para este modelo se utiliza un umbral de clasificación de 0,30.
- **Modelo 3: mes y día de la semana.** Combina ambas variables para evaluar si su utilización conjunta mejora la capacidad predictiva.

## 3. Evaluación de los modelos

### 3.1. Matrices de confusión

Las matrices de confusión permiten comparar las predicciones realizadas por cada modelo con los valores reales de la variable `alta_demanda`.

Se utilizan para identificar cuatro situaciones:

- Verdaderos positivos: días de alta demanda correctamente identificados.
- Verdaderos negativos: días de demanda normal correctamente identificados.
- Falsos positivos: días de demanda normal clasificados incorrectamente como días de alta demanda.
- Falsos negativos: días de alta demanda que el modelo no consigue detectar.

**Modelo 1: regresión logística con la variable mes del año**

<img width="338" height="113" alt="matriz modelo1" src="https://github.com/user-attachments/assets/7bd30afe-2f59-44e7-8db1-f2803f28f31e" />

**Modelo 2: regresión logística con la variable día de la semana**

<img width="338" height="114" alt="matriz modelo2" src="https://github.com/user-attachments/assets/af378794-d9a3-4b9e-a1dd-56dcf94e6390" />

**Modelo 3: regresión logística con las variables mes y día de la semana**

<img width="340" height="110" alt="matriz modelo3" src="https://github.com/user-attachments/assets/2a1700ec-7969-4e22-9429-cba834219406" />

### 3.2. Comparación de los indicadores de rendimiento

Para comparar los resultados de los tres modelos, utilizamos tres indicadores principales: *Recall*, *Precision* y *F1-score*.

- **Recall:** mide la proporción de días de alta demanda que el modelo consigue identificar correctamente.
- **Precision:** mide la proporción de predicciones de alta demanda que son realmente correctas.
- **F1-score:** representa el equilibrio entre el Recall y la Precision.

Los resultados obtenidos son los siguientes:

| Modelo | Recall | Precision | F1-score |
|---|---:|---:|---:|
| Modelo 1: mes | 36 % | 28 % | 31 % |
| Modelo 2: día de la semana | 40 % | 18 % | 25 % |
| Modelo 3: mes + día de la semana | 30 % | 25 % | 27 % |

El modelo 1, basado únicamente en el mes, presenta el mejor F1-score, con un valor del 31 %. Esto indica que ofrece el mejor equilibrio entre la detección de los días de alta demanda y la fiabilidad de sus predicciones.

El modelo 2, basado en el día de la semana, obtiene el Recall más elevado, con un 40 %. Por lo tanto, consigue identificar una mayor proporción de los días de alta demanda. Sin embargo, su Precision es de tan solo un 18 %, lo que indica que genera un número importante de falsas alertas.

Por último, el modelo 3, que combina el mes y el día de la semana, obtiene un F1-score del 27 % y un Recall del 30 %. La combinación de ambas variables no permite mejorar los resultados respecto al modelo basado únicamente en el mes.

En conjunto, estos resultados muestran que los modelos tienen dificultades para identificar correctamente los días de alta demanda.

### 3.3. Análisis de las curvas ROC y del AUC

Para completar la evaluación, analizamos las curvas ROC (*Receiver Operating Characteristic*) de los tres modelos y calculamos el área bajo la curva (AUC).

La curva ROC representa la relación entre la tasa de verdaderos positivos y la tasa de falsos positivos para diferentes umbrales de clasificación.

Los resultados obtenidos son los siguientes:

| Modelo | Variables explicativas | AUC |
|---|---|---:|
| Modelo 1 | Mes | 0,662 |
| Modelo 2 | Día de la semana | 0,593 |
| Modelo 3 | Mes + día de la semana | 0,682 |

<img width="1500" height="1050" alt="ROC Curve modelo3" src="https://github.com/user-attachments/assets/449f2b5c-753c-4560-9b21-4f0f7c19e51e" /><img width="1500" height="1050" alt="ROC Curve modelo2" src="https://github.com/user-attachments/assets/c8c6c3c9-a3bc-4de3-ad4c-7c8b1e5ee543" />
<img width="1500" height="1050" alt="ROC Curve modelo1" src="https://github.com/user-attachments/assets/0d24b7a5-e239-475b-8bf7-6d5ccdcb0de4" />


Los resultados muestran que el modelo 3 obtiene el AUC más elevado, con un valor de 0,682. Esto indica que es el modelo con mayor capacidad para distinguir entre los días de alta demanda y los días de demanda normal, independientemente del umbral de clasificación.

El modelo 1 presenta un AUC de 0,662, mientras que el modelo 2 obtiene un valor de 0,593, siendo el menos discriminante de los tres.

Aunque los tres modelos presentan un rendimiento superior al de un clasificador aleatorio, sus capacidades de discriminación siguen siendo relativamente modestas.

Es importante distinguir entre el AUC y el F1-score: mientras que el primero evalúa la capacidad general de discriminación del modelo para distintos umbrales, el segundo mide el equilibrio entre precisión y sensibilidad para un umbral determinado.

Por lo tanto, el modelo 3 presenta la mejor capacidad global de discriminación, mientras que el modelo 1 obtiene el mejor equilibrio entre Recall y Precision según el umbral utilizado en la evaluación.

---

## 4. Conclusión general

El análisis realizado permite identificar determinadas tendencias temporales en la demanda diaria de prendas de H&M. En particular, el mes del año y el día de la semana presentan diferencias en los niveles de demanda, lo que justifica su utilización como variables explicativas en los modelos de regresión logística.

Sin embargo, los resultados obtenidos muestran que estas variables, utilizadas de forma aislada o conjunta, no permiten predecir con suficiente precisión los días de alta demanda.

El modelo basado en el mes obtiene el mejor F1-score (31 %), mientras que el modelo que combina el mes y el día de la semana presenta el AUC más elevado (0,682). Por su parte, el modelo basado únicamente en el día de la semana consigue el mayor Recall (40 %), aunque presenta una Precision particularmente baja.

En consecuencia, podemos concluir que las características del calendario contienen cierta información sobre la evolución de la demanda, pero no son suficientes para explicar por sí solas los episodios de alta demanda.
