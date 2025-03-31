import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.pedigree import build_partial_pedigree, classify_relatives


def main():
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        raw_data_path = os.path.join(base_dir, 'data', 'raw', 'dataset.csv')
        processed_data_dir = os.path.join(base_dir, 'data', 'processed')

        # Carregar o dataset
        data = pd.read_csv(raw_data_path)

        # Verificar se o diretório 'data/processed' existe, senão criar
        os.makedirs(processed_data_dir, exist_ok=True)

        # Processar cada paciente
        pedigrees = []
        all_relatives = []
        for record_id in data['record_id']:
            try:
                # Construir o pedigree
                pedigree = build_partial_pedigree(data, record_id)

                # Classificar parentescos até o quarto grau para o paciente (ID 1 no pedigree)
                result = classify_relatives(pedigree, 1)

                # Adicionar informações ao resultado
                pedigrees.append({
                    'record_id': record_id,
                    'pedigree': pedigree
                })
                all_relatives.append({
                    'record_id': record_id,
                    'first_degree': result['first_degree'],
                    'second_degree': result['second_degree'],
                    'third_degree': result['third_degree'],
                    'fourth_degree': result['fourth_degree']
                })
            except Exception as e:
                print(f"Erro ao processar o record_id {record_id}: {e}")
                continue

        # Salvar pedigrees
        if pedigrees:
            all_pedigrees = pd.concat([p['pedigree'] for p in pedigrees], ignore_index=True)
            all_pedigrees.to_csv(os.path.join(processed_data_dir, 'pedigrees.csv'), index=False)
            print(f"Pedigrees salvos em {processed_data_dir}/pedigrees.csv")
        else:
            print("Nenhum pedigree para salvar.")

        # Salvar parentescos de cada grau
        for degree, degree_name in [
            ('first_degree', 'first_degree_relatives'),
            ('second_degree', 'second_degree_relatives'),
            ('third_degree', 'third_degree_relatives'),
            ('fourth_degree', 'fourth_degree_relatives')
        ]:
            degree_relatives = []
            for rel in all_relatives:
                df = rel[degree].copy()
                if not df.empty:
                    df['record_id'] = rel['record_id']
                    degree_relatives.append(df)
            if degree_relatives:
                degree_df = pd.concat(degree_relatives, ignore_index=True)
                degree_df.to_csv(os.path.join(processed_data_dir, f'{degree_name}.csv'), index=False)
                print(f"Parentes de {degree_name.replace('_', ' ')} salvos em {processed_data_dir}/{degree_name}.csv")
            else:
                print(f"Nenhum parente de {degree_name.replace('_', ' ')} para salvar.")

    except Exception as e:
        print(f"Erro ao processar os dados: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
