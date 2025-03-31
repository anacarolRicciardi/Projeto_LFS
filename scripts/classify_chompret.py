import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.chompret import classify_lfs_criteria


def main():
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        raw_data_path = os.path.join(base_dir, 'data', 'raw', 'dataset.csv')
        processed_data_dir = os.path.join(base_dir, 'data', 'processed')
        classifications_output_path = os.path.join(processed_data_dir, 'classifications.csv')

        # Garantir existência do diretório processed
        os.makedirs(processed_data_dir, exist_ok=True)

        # Carregar o dataset
        data = pd.read_csv(raw_data_path)

        # Classificar
        classifications = classify_lfs_criteria(data)
        data_with_results = pd.concat([data[['record_id', 'nome_completo_paciente']], classifications], axis=1)

        # Salvar resultados
        data_with_results.to_csv(classifications_output_path, index=False)
        print(f"Classificações salvas em {classifications_output_path}")
        print(data_with_results.to_string(index=False))

    except Exception as e:
        print(f"Erro ao processar os dados: {e}")


if __name__ == "__main__":
    main()