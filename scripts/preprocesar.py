import os
import pandas as pd
import numpy as np

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "transactions_train.csv")
    output_path = os.path.join(base_dir, "data", "processed", "demanda_diaria.csv")

    print(f"Leyendo transacciones desde: {raw_path}...")
    if not os.path.exists(raw_path):
        raise FileNotFoundError(f"No se encontró el archivo: {raw_path}")

    # Leemos solo la columna de fecha para optimizar memoria RAM
    df_raw = pd.read_csv(raw_path, usecols=['t_dat'])
    print(f"Total de transacciones cargadas: {len(df_raw):,}")

    # Agrupamos por fecha para obtener la demanda diaria
    print("Agrupando por fecha...")
    df_diario = df_raw.groupby('t_dat').size().reset_index(name='demanda_diaria')
    df_diario.rename(columns={'t_dat': 'fecha'}, inplace=True)

    # Convertimos a formato datetime
    df_diario['fecha'] = pd.to_datetime(df_diario['fecha'])
    df_diario = df_diario.sort_values('fecha').reset_index(drop=True)

    # Extracción de variables de calendario
    # dayofweek en pandas: 0=Lunes, 6=Domingo -> Mapeamos a 1=Lunes, 7=Domingo para legibilidad
    dias_es = {0: 'Lunes', 1: 'Martes', 2: 'Miercoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sabado', 6: 'Domingo'}
    df_diario['dia_semana_num'] = df_diario['fecha'].dt.dayofweek + 1
    df_diario['dia_semana_nombre'] = df_diario['fecha'].dt.dayofweek.map(dias_es)
    df_diario['dia_mes'] = df_diario['fecha'].dt.day
    df_diario['mes'] = df_diario['fecha'].dt.month
    df_diario['es_fin_de_semana'] = df_diario['dia_semana_num'].apply(lambda x: 1 if x in [6, 7] else 0)

    # Estadísticas descriptivas de la demanda diaria
    demanda = df_diario['demanda_diaria']
    media = demanda.mean()
    mediana = demanda.median()
    p75 = np.percentile(demanda, 75)
    p80 = np.percentile(demanda, 80)
    p90 = np.percentile(demanda, 90)

    print("\n--- Estadísticas Descriptivas (Demanda Diaria) ---")
    print(f"Total de días analizados: {len(df_diario)}")
    print(f"Mínimo: {demanda.min():,}")
    print(f"Promedio (Media): {media:,.2f}")
    print(f"Mediana (P50): {mediana:,.2f}")
    print(f"Percentil 75 (Q3): {p75:,.2f}")
    print(f"Percentil 80: {p80:,.2f}")
    print(f"Percentil 90: {p90:,.2f}")
    print(f"Máximo: {demanda.max():,}")

    # Definición de la variable binaria con Percentil 75 (Macro)
    df_diario['alta_demanda'] = (df_diario['demanda_diaria'] >= p75).astype(int)

    dist_clases = df_diario['alta_demanda'].value_counts()
    print("\n--- Distribución de Clases (alta_demanda) ---")
    print(f"Clase 0 (Demanda Normal): {dist_clases.get(0, 0)} días ({dist_clases.get(0, 0)/len(df_diario):.1%})")
    print(f"Clase 1 (Alta Demanda):   {dist_clases.get(1, 0)} días ({dist_clases.get(1, 0)/len(df_diario):.1%})")

    # Guardar archivo limpio y listo para KNIME
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_diario.to_csv(output_path, index=False)
    print(f"\n¡Dataset procesado guardado exitosamente en:\n{output_path} (filas: {len(df_diario)})!")

if __name__ == "__main__":
    main()
