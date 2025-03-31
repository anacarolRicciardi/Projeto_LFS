import os
import pandas as pd
from src.model import prepare_features, train_model, predict_lfs


def handle_missing_columns(features, required_columns):
    for col in required_columns:
        if col not in features.columns:
            features[col] = 0  # Preenche com 0 se coluna faltar
    return features


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Definir caminhos corretos
    raw_data_path = os.path.join(base_dir, 'data', 'raw', 'dataset.csv')
    processed_data_dir = os.path.join(base_dir, 'data', 'processed')
    classifications_path = os.path.join(processed_data_dir, 'classifications.csv')
    model_path = os.path.join(base_dir, 'model.pkl')
    predictions_output_path = os.path.join(processed_data_dir, 'predictions.csv')

    # Carregar dados e classificações
    data = pd.read_csv(raw_data_path)
    classifications = pd.read_csv(classifications_path)

    # Carregar parentes de todos os graus
    relatives = {}
    for degree in ['first_degree', 'second_degree', 'third_degree', 'fourth_degree']:
        degree_path = os.path.join(processed_data_dir, f'{degree}_relatives.csv')
        if os.path.exists(degree_path):
            relatives[degree] = pd.read_csv(degree_path)
        else:
            relatives[degree] = pd.DataFrame(columns=['record_id', 'ID', 'name', 'relationship'])

    # Lista de colunas esperadas
    expected_columns = ['era_tipo_ca___15', 'algum_filho_teve_tem_ca', 'algum_irmao_teve_ca']

    # Preparar características
    X, y = prepare_features(data, classifications, relatives)

    # Lidar com colunas faltantes antes de treinar o modelo
    X = handle_missing_columns(X, expected_columns)

    # Treinar modelo
    model = train_model(X, y, model_path=model_path)

    # Fazer predições para todos os pacientes
    predictions = predict_lfs(model, X)
    data['LFS_Probability'] = predictions

    # Salvar resultados
    data[['record_id', 'nome_completo_paciente', 'LFS_Probability']].to_csv(predictions_output_path, index=False)
    print(f"Predições salvas em {predictions_output_path}")
    print(data[['record_id', 'nome_completo_paciente', 'LFS_Probability']].to_string(index=False))


if __name__ == "__main__":
    main()