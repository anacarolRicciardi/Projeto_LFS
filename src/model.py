import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
#importar outros classificadores

from sklearn.metrics import classification_report
import pickle

def prepare_features(data, classifications, relatives):
    # Combinar dados clínicos com classificações
    features = data.copy()
    features['Chompret_2015'] = classifications['Chompret_2015']
    features['Chompret_2009'] = classifications['Chompret_2009']
    features['Classic'] = classifications['Classic']
    
    # Adicionar características de parentes de 1º, 2º, 3º e 4º graus
    for degree in ['first_degree', 'second_degree', 'third_degree', 'fourth_degree']:
        rel_df = relatives[degree]
        for record_id in features['record_id']:
            rel_subset = rel_df[rel_df['record_id'] == record_id]
            # Definir os tipos de parentes esperados para cada grau
            rel_types = []
            if degree == 'first_degree':
                rel_types = ['Pai', 'Mãe', 'Filho_Filha']
            elif degree == 'second_degree':
                rel_types = ['Irmão_Irmã', 'Avô_Avó', 'Neto_Neta']
            elif degree == 'third_degree':
                rel_types = ['Tio_Tia', 'Sobrinho_Sobrinha', 'Bisavô_Bisavó', 'Bisneto_Bisneta']
            elif degree == 'fourth_degree':
                rel_types = ['Primo_Prima', 'Tio-avô_Tia-avó', 'Sobrinho-neto_Sobrinha-neta', 'Trisavô_Trisavó', 'Trineto_Trineta']
            
            for rel_type in rel_types:
                has_rel = any(rel_subset['relationship'].str.replace('/', '_') == rel_type)
                features.loc[features['record_id'] == record_id, f'has_{rel_type}_{degree}'] = int(has_rel)
    
    # Selecionar características relevantes
    feature_cols = [
        'idade',  # Idade do paciente
        'era_tipo_ca___3',  # Câncer de mama
        'era_tipo_ca___12',  # Sarcoma
        'era_tipo_ca___15',  # Osteossarcoma
        'pai_teve_tem_ca', 'mae_teve_tem_ca',  # Câncer nos pais
        'algum_filho_teve_tem_ca', 'algum_irmao_teve_ca',  # Câncer em filhos e irmãos
        'Chompret_2015', 'Chompret_2009', 'Classic'  # Resultados dos critérios
    ]
    
    # Adicionar características de todos os graus
    for degree in ['first_degree', 'second_degree', 'third_degree', 'fourth_degree']:
        if degree == 'first_degree':
            rel_types = ['Pai', 'Mãe', 'Filho_Filha']
        elif degree == 'second_degree':
            rel_types = ['Irmão_Irmã', 'Avô_Avó', 'Neto_Neta']
        elif degree == 'third_degree':
            rel_types = ['Tio_Tia', 'Sobrinho_Sobrinha', 'Bisavô_Bisavó', 'Bisneto_Bisneta']
        elif degree == 'fourth_degree':
            rel_types = ['Primo_Prima', 'Tio-avô_Tia-avó', 'Sobrinho-neto_Sobrinha-neta', 'Trisavô_Trisavó', 'Trineto_Trineta']
        for rel_type in rel_types:
            feature_cols.append(f'has_{rel_type}_{degree}')
    
    # Tratar valores ausentes
    X = features[feature_cols].fillna(0)
    # Rótulo: 1 se atender a qualquer critério, 0 caso contrário
    y = (classifications['Chompret_2015'] | classifications['Chompret_2009'] | classifications['Classic']).astype(int)
    
    return X, y

def train_model(X, y, model_path='model.pkl'):
    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Treinar modelo
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Avaliar modelo
    y_pred = model.predict(X_test)
    print("Relatório de Classificação:")
    print(classification_report(y_test, y_pred))
    
    # Salvar modelo
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Modelo salvo em {model_path}")
    
    return model

def predict_lfs(model, X):
    # Fazer predições
    predictions = model.predict_proba(X)[:, 1]  # Probabilidade da classe 1 (LFS)
    return predictions