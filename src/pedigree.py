import pandas as pd

def build_partial_pedigree(data, record_id):
    """
    Reconstrói um pedigree parcial para um paciente até a 4ª geração.
    
    Args:
        data (pd.DataFrame): Dataset com informações dos pacientes e familiares.
        record_id (int): ID do paciente a ser analisado.
    
    Returns:
        pd.DataFrame: Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
    """
    patient_row = data[data['record_id'] == record_id].iloc[0]
    pedigree = []
    current_id = 1
    
    # 1ª Geração: Paciente (proband)
    patient_id = current_id
    pedigree.append({'ID': patient_id, 'fID': None, 'mID': None, 'name': patient_row['nome_completo_paciente']})
    current_id += 1
    
    # 2ª Geração: Pais (primeiro grau ascendente)
    father_id, mother_id = None, None
    if patient_row['pai_teve_tem_ca'] == 1:
        father_id = current_id
        pedigree.append({'ID': father_id, 'fID': None, 'mID': None, 'name': 'Pai do paciente'})
        pedigree[0]['fID'] = father_id
        current_id += 1
    if patient_row['mae_teve_tem_ca'] == 1:
        mother_id = current_id
        pedigree.append({'ID': mother_id, 'fID': None, 'mID': None, 'name': 'Mãe do paciente'})
        pedigree[0]['mID'] = mother_id
        current_id += 1
    
    # 2ª Geração: Filhos (primeiro grau descendente)
    children_ids = []
    for i in range(1, 6):
        filho_key = f'nome_filho{i}'
        if pd.notna(patient_row.get(filho_key, '')) and patient_row[filho_key]:
            filho_id = current_id
            pedigree.append({
                'ID': filho_id,
                'fID': patient_id if patient_row['sexo'] == 'M' else (father_id if father_id else None),
                'mID': patient_id if patient_row['sexo'] == 'F' else (mother_id if mother_id else None),
                'name': patient_row[filho_key]
            })
            children_ids.append(filho_id)
            current_id += 1
    
    # 3ª Geração: Irmãos (segundo grau lateral)
    siblings_ids = []
    for i in range(1, 11):
        irmao_key = f'nome_ca_irmao{i}'
        if pd.notna(patient_row.get(irmao_key, '')) and patient_row[irmao_key]:
            irmao_id = current_id
            pedigree.append({
                'ID': irmao_id,
                'fID': father_id,
                'mID': mother_id,
                'name': patient_row[irmao_key]
            })
            siblings_ids.append(irmao_id)
            current_id += 1
    
    # 3ª Geração: Avós (segundo grau ascendente)
    paternal_grandfather_id, paternal_grandmother_id = None, None
    maternal_grandfather_id, maternal_grandmother_id = None, None
    for avo_key, avo_name, parent_id, parent_type in [
        ('avo_h_paterno_teve_tem_ca', 'Avô paterno', father_id, 'fID'),
        ('avo_m_paterno_teve_tem_ca', 'Avó paterna', father_id, 'mID'),
        ('avo_h_materno_teve_tem_ca', 'Avô materno', mother_id, 'fID'),
        ('avo_m_materno_teve_tem_ca', 'Avó materna', mother_id, 'mID')
    ]:
        if patient_row.get(avo_key, 0) == 1:
            avo_id = current_id
            pedigree.append({'ID': avo_id, 'fID': None, 'mID': None, 'name': avo_name})
            if parent_id:
                for p in pedigree:
                    if p['ID'] == parent_id:
                        p[parent_type] = avo_id
                        break
            if 'paterno' in avo_key and 'h_' in avo_key:
                paternal_grandfather_id = avo_id
            elif 'paterno' in avo_key:
                paternal_grandmother_id = avo_id
            elif 'materno' in avo_key and 'h_' in avo_key:
                maternal_grandfather_id = avo_id
            else:
                maternal_grandmother_id = avo_id
            current_id += 1
    
    # 3ª Geração: Netos (segundo grau descendente)
    # O dataset não tem essa informação diretamente, mas podemos inferir se houver dados adicionais
    grandchildren_ids = []
    for i in range(1, 6):
        filho_key = f'nome_filho{i}'
        if pd.notna(patient_row.get(filho_key, '')) and patient_row[filho_key]:
            filho_id = [p['ID'] for p in pedigree if p['name'] == patient_row[filho_key]][0]
            # Suponha que tenhamos colunas como 'nome_netoX_filhoY'
            for j in range(1, 6):
                neto_key = f'nome_neto{j}_filho{i}'
                if pd.notna(patient_row.get(neto_key, '')) and patient_row.get(neto_key, ''):
                    neto_id = current_id
                    pedigree.append({
                        'ID': neto_id,
                        'fID': filho_id if 'sexo_filho{i}' in patient_row and patient_row['sexo_filho{i}'] == 'M' else None,
                        'mID': filho_id if 'sexo_filho{i}' in patient_row and patient_row['sexo_filho{i}'] == 'F' else None,
                        'name': patient_row[neto_key]
                    })
                    grandchildren_ids.append(neto_id)
                    current_id += 1
    
    # 4ª Geração: Tios (terceiro grau lateral)
    paternal_uncles_ids, maternal_uncles_ids = [], []
    for i in range(1, 11):
        tio_paterno_key = f'nome_ca_tios_paternos{i}'
        tio_materno_key = f'nome_ca_tios_maternos{i}'
        if pd.notna(patient_row.get(tio_paterno_key, '')) and patient_row[tio_paterno_key]:
            tio_id = current_id
            pedigree.append({
                'ID': tio_id,
                'fID': paternal_grandfather_id,
                'mID': paternal_grandmother_id,
                'name': patient_row[tio_paterno_key]
            })
            paternal_uncles_ids.append(tio_id)
            current_id += 1
        if pd.notna(patient_row.get(tio_materno_key, '')) and patient_row[tio_materno_key]:
            tio_id = current_id
            pedigree.append({
                'ID': tio_id,
                'fID': maternal_grandfather_id,
                'mID': maternal_grandmother_id,
                'name': patient_row[tio_materno_key]
            })
            maternal_uncles_ids.append(tio_id)
            current_id += 1
    
    # 4ª Geração: Sobrinhos (terceiro grau lateral, filhos dos irmãos)
    nephews_ids = []
    for i in range(1, 11):
        irmao_key = f'nome_ca_irmao{i}'
        if pd.notna(patient_row.get(irmao_key, '')) and patient_row[irmao_key]:
            irmao_id = [p['ID'] for p in pedigree if p['name'] == patient_row[irmao_key]][0]
            for j in range(1, 6):
                sobrinho_key = f'nome_filho{j}_irmao{i}'
                if pd.notna(patient_row.get(sobrinho_key, '')) and patient_row.get(sobrinho_key, ''):
                    sobrinho_id = current_id
                    pedigree.append({
                        'ID': sobrinho_id,
                        'fID': irmao_id if 'sexo_irmao{i}' in patient_row and patient_row['sexo_irmao{i}'] == 'M' else None,
                        'mID': irmao_id if 'sexo_irmao{i}' in patient_row and patient_row['sexo_irmao{i}'] == 'F' else None,
                        'name': patient_row[sobrinho_key]
                    })
                    nephews_ids.append(sobrinho_id)
                    current_id += 1
    
    # 4ª Geração: Bisavós (terceiro grau ascendente)
    for avo_id, bisavo_key, bisavo_name, parent_type in [
        (paternal_grandfather_id, 'bisavo_h_paterno_teve_tem_ca', 'Bisavô paterno do avô paterno', 'fID'),
        (paternal_grandfather_id, 'bisavo_m_paterno_teve_tem_ca', 'Bisavó paterna do avô paterno', 'mID'),
        (paternal_grandmother_id, 'bisavo_h_paterno_m_teve_tem_ca', 'Bisavô paterno da avó paterna', 'fID'),
        (paternal_grandmother_id, 'bisavo_m_paterno_m_teve_tem_ca', 'Bisavó paterna da avó paterna', 'mID'),
        (maternal_grandfather_id, 'bisavo_h_materno_teve_tem_ca', 'Bisavô materno do avô materno', 'fID'),
        (maternal_grandfather_id, 'bisavo_m_materno_teve_tem_ca', 'Bisavó materna do avô materno', 'mID'),
        (maternal_grandmother_id, 'bisavo_h_materno_m_teve_tem_ca', 'Bisavô materno da avó materna', 'fID'),
        (maternal_grandmother_id, 'bisavo_m_materno_m_teve_tem_ca', 'Bisavó materna da avó materna', 'mID')
    ]:
        if avo_id and pd.notna(patient_row.get(bisavo_key, 0)) and patient_row.get(bisavo_key, 0) == 1:
            bisavo_id = current_id
            pedigree.append({'ID': bisavo_id, 'fID': None, 'mID': None, 'name': bisavo_name})
            for p in pedigree:
                if p['ID'] == avo_id:
                    p[parent_type] = bisavo_id
                    break
            current_id += 1
    
    # 4ª Geração: Bisnetos (terceiro grau descendente)
    great_grandchildren_ids = []
    for i in range(1, 6):
        filho_key = f'nome_filho{i}'
        if pd.notna(patient_row.get(filho_key, '')) and patient_row[filho_key]:
            filho_id = [p['ID'] for p in pedigree if p['name'] == patient_row[filho_key]][0]
            for j in range(1, 6):
                neto_key = f'nome_neto{j}_filho{i}'
                if pd.notna(patient_row.get(neto_key, '')) and patient_row[neto_key]:
                    neto_id = [p['ID'] for p in pedigree if p['name'] == patient_row[neto_key]][0]
                    for k in range(1, 6):
                        bisneto_key = f'nome_bisneto{k}_neto{j}_filho{i}'
                        if pd.notna(patient_row.get(bisneto_key, '')) and patient_row.get(bisneto_key, ''):
                            bisneto_id = current_id
                            pedigree.append({
                                'ID': bisneto_id,
                                'fID': neto_id if 'sexo_neto{j}_filho{i}' in patient_row and patient_row['sexo_neto{j}_filho{i}'] == 'M' else None,
                                'mID': neto_id if 'sexo_neto{j}_filho{i}' in patient_row and patient_row['sexo_neto{j}_filho{i}'] == 'F' else None,
                                'name': patient_row[bisneto_key]
                            })
                            great_grandchildren_ids.append(bisneto_id)
                            current_id += 1
    
    # 5ª Geração: Primos (quarto grau lateral, filhos dos tios)
    cousins_ids = []
    for tio_id in paternal_uncles_ids + maternal_uncles_ids:
        for j in range(1, 6):
            primo_key = f'nome_filho{j}_tio{tio_id}'
            if pd.notna(patient_row.get(primo_key, '')) and patient_row.get(primo_key, ''):
                primo_id = current_id
                pedigree.append({
                    'ID': primo_id,
                    'fID': tio_id if 'sexo_tio{tio_id}' in patient_row and patient_row[f'sexo_tio{tio_id}'] == 'M' else None,
                    'mID': tio_id if 'sexo_tio{tio_id}' in patient_row and patient_row[f'sexo_tio{tio_id}'] == 'F' else None,
                    'name': patient_row[primo_key]
                })
                cousins_ids.append(primo_id)
                current_id += 1
    
    # 5ª Geração: Tios-avôs (quarto grau lateral, irmãos dos avós)
    great_uncles_ids = []
    for avo_id, avo_parents in [
        (paternal_grandfather_id, (paternal_grandfather_id, paternal_grandmother_id)),
        (paternal_grandmother_id, (paternal_grandfather_id, paternal_grandmother_id)),
        (maternal_grandfather_id, (maternal_grandfather_id, maternal_grandmother_id)),
        (maternal_grandmother_id, (maternal_grandfather_id, maternal_grandmother_id))
    ]:
        if avo_id:
            for j in range(1, 6):
                tio_avo_key = f'nome_irmao{j}_avo{avo_id}'
                if pd.notna(patient_row.get(tio_avo_key, '')) and patient_row.get(tio_avo_key, ''):
                    tio_avo_id = current_id
                    pedigree.append({
                        'ID': tio_avo_id,
                        'fID': avo_parents[0],
                        'mID': avo_parents[1],
                        'name': patient_row[tio_avo_key]
                    })
                    great_uncles_ids.append(tio_avo_id)
                    current_id += 1
    
    # 5ª Geração: Sobrinhos-netos (quarto grau descendente, filhos dos sobrinhos)
    great_nephews_ids = []
    for sobrinho_id in nephews_ids:
        for j in range(1, 6):
            sobrinho_neto_key = f'nome_filho{j}_sobrinho{sobrinho_id}'
            if pd.notna(patient_row.get(sobrinho_neto_key, '')) and patient_row.get(sobrinho_neto_key, ''):
                sobrinho_neto_id = current_id
                pedigree.append({
                    'ID': sobrinho_neto_id,
                    'fID': sobrinho_id if 'sexo_sobrinho{sobrinho_id}' in patient_row and patient_row[f'sexo_sobrinho{sobrinho_id}'] == 'M' else None,
                    'mID': sobrinho_id if 'sexo_sobrinho{sobrinho_id}' in patient_row and patient_row[f'sexo_sobrinho{sobrinho_id}'] == 'F' else None,
                    'name': patient_row[sobrinho_neto_key]
                })
                great_nephews_ids.append(sobrinho_neto_id)
                current_id += 1
    
    # 5ª Geração: Trisavôs (quarto grau ascendente)
    for avo_id, trisavo_key, trisavo_name, parent_type in [
        (paternal_grandfather_id, 'trisavo_h_paterno_teve_tem_ca', 'Trisavô paterno do avô paterno', 'fID'),
        (paternal_grandfather_id, 'trisavo_m_paterno_teve_tem_ca', 'Trisavó paterna do avô paterno', 'mID'),
        (paternal_grandmother_id, 'trisavo_h_paterno_m_teve_tem_ca', 'Trisavô paterno da avó paterna', 'fID'),
        (paternal_grandmother_id, 'trisavo_m_paterno_m_teve_tem_ca', 'Trisavó paterna da avó paterna', 'mID'),
        (maternal_grandfather_id, 'trisavo_h_materno_teve_tem_ca', 'Trisavô materno do avô materno', 'fID'),
        (maternal_grandfather_id, 'trisavo_m_materno_teve_tem_ca', 'Trisavó materna do avô materno', 'mID'),
        (maternal_grandmother_id, 'trisavo_h_materno_m_teve_tem_ca', 'Trisavô materno da avó materna', 'fID'),
        (maternal_grandmother_id, 'trisavo_m_materno_m_teve_tem_ca', 'Trisavó materna da avó materna', 'mID')
    ]:
        if avo_id and pd.notna(patient_row.get(trisavo_key, 0)) and patient_row.get(trisavo_key, 0) == 1:
            trisavo_id = current_id
            pedigree.append({'ID': trisavo_id, 'fID': None, 'mID': None, 'name': trisavo_name})
            for p in pedigree:
                if p['ID'] == avo_id:
                    p[parent_type] = trisavo_id
                    break
            current_id += 1
    
    # 5ª Geração: Trinetos (quarto grau descendente)
    great_great_grandchildren_ids = []
    for neto_id in grandchildren_ids:
        for j in range(1, 6):
            bisneto_key = f'nome_bisneto{j}_neto{neto_id}'
            if pd.notna(patient_row.get(bisneto_key, '')) and patient_row.get(bisneto_key, ''):
                bisneto_id = [p['ID'] for p in pedigree if p['name'] == patient_row[bisneto_key]][0]
                for k in range(1, 6):
                    trineto_key = f'nome_trineto{k}_bisneto{j}_neto{neto_id}'
                    if pd.notna(patient_row.get(trineto_key, '')) and patient_row.get(trineto_key, ''):
                        trineto_id = current_id
                        pedigree.append({
                            'ID': trineto_id,
                            'fID': bisneto_id if 'sexo_bisneto{j}_neto{neto_id}' in patient_row and patient_row[f'sexo_bisneto{j}_neto{neto_id}'] == 'M' else None,
                            'mID': bisneto_id if 'sexo_bisneto{j}_neto{neto_id}' in patient_row and patient_row[f'sexo_bisneto{j}_neto{neto_id}'] == 'F' else None,
                            'name': patient_row[trineto_key]
                        })
                        great_great_grandchildren_ids.append(trineto_id)
                        current_id += 1
    
    return pd.DataFrame(pedigree)

def first_degree_relative(pedigree, ii):
    """
    Identifica parentes de primeiro grau (pai, mãe, filho, filha).
    
    Args:
        pedigree (pd.DataFrame): Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
        ii (int): Índice do indivíduo no pedigree.
    
    Returns:
        pd.DataFrame: Parentes de primeiro grau com colunas ['index', 'lineage'].
    """
    rlt = []
    num_samples = len(pedigree)
    pedigree = pedigree.copy()
    for i in range(num_samples):
        if pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'fID'] = -999
        if not pd.isna(pedigree.at[i, 'fID']) and pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'mID'] = -9999
    fID = pedigree.at[ii, 'fID']
    mID = pedigree.at[ii, 'mID']
    ID = pedigree.at[ii, 'ID']
    for i in range(num_samples):
        if i == ii:
            continue
        if pedigree.at[i, 'ID'] == fID and not pd.isna(pedigree.at[i, 'ID'] == fID):
            rlt.append({'index': i, 'lineage': 'F'})  # Pai
            continue
        if pedigree.at[i, 'ID'] == mID and not pd.isna(pedigree.at[i, 'ID'] == mID):
            rlt.append({'index': i, 'lineage': 'M'})  # Mãe
            continue
        if (pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID) and \
           not pd.isna(pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID):
            rlt.append({'index': i, 'lineage': 'C'})  # Filho/Filha
            continue
    return pd.DataFrame(rlt) if rlt else pd.DataFrame(columns=['index', 'lineage'])

def second_degree_relative(pedigree, ii):
    """
    Identifica parentes de segundo grau (irmão, irmã, avô, avó, neto, neta).
    
    Args:
        pedigree (pd.DataFrame): Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
        ii (int): Índice do indivíduo no pedigree.
    
    Returns:
        pd.DataFrame: Parentes de segundo grau com colunas ['index', 'lineage'].
    """
    num_samples = len(pedigree)
    pedigree = pedigree.copy()
    for i in range(num_samples):
        if pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'fID'] = -999
        if not pd.isna(pedigree.at[i, 'fID']) and pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'mID'] = -9999
    fID = pedigree.at[ii, 'fID']
    mID = pedigree.at[ii, 'mID']
    ID = pedigree.at[ii, 'ID']
    rlt = []
    
    # Irmãos (mesmos pais)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == fID and pedigree.at[i, 'mID'] == mID) and \
           not pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            rlt.append({'index': i, 'lineage': 'S'})  # Irmão/Irmã
    
    # Avós (pais dos pais)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'ID'] == fID or pedigree.at[i, 'ID'] == mID) and \
           not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'ID'] == parent_fID or pedigree.at[j, 'ID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'ID']):
                    rlt.append({'index': j, 'lineage': 'G'})  # Avô/Avó
    
    # Netos (filhos dos filhos)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID) and \
           not pd.isna(pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID):
            child_id = pedigree.at[i, 'ID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id) and \
                   not pd.isna(pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id):
                    rlt.append({'index': j, 'lineage': 'GC'})  # Neto/Neta
    
    return pd.DataFrame(rlt) if rlt else pd.DataFrame(columns=['index', 'lineage'])

def third_degree_relative(pedigree, ii):
    """
    Identifica parentes de terceiro grau (tio, tia, sobrinho, sobrinha, bisavô, bisavó, bisneto, bisneta).
    
    Args:
        pedigree (pd.DataFrame): Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
        ii (int): Índice do indivíduo no pedigree.
    
    Returns:
        pd.DataFrame: Parentes de terceiro grau com colunas ['index', 'lineage'].
    """
    num_samples = len(pedigree)
    pedigree = pedigree.copy()
    for i in range(num_samples):
        if pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'fID'] = -999
        if not pd.isna(pedigree.at[i, 'fID']) and pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'mID'] = -9999
    rlt = []
    
    # Tios (irmãos dos pais)
    fID = pedigree.at[ii, 'fID']
    mID = pedigree.at[ii, 'mID']
    for i in range(num_samples):
        if i == ii:
            continue
        parent_fID = None
        parent_mID = None
        if pedigree.at[i, 'ID'] == fID and not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
        elif pedigree.at[i, 'ID'] == mID and not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
        if parent_fID or parent_mID:
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == parent_fID and pedigree.at[j, 'mID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'fID']) and not pd.isna(pedigree.at[j, 'mID']):
                    rlt.append({'index': j, 'lineage': 'U'})  # Tio/Tia
    
    # Sobrinhos (filhos dos irmãos)
    ID = pedigree.at[ii, 'ID']
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == fID and pedigree.at[i, 'mID'] == mID) and \
           not pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            sibling_id = pedigree.at[i, 'ID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == sibling_id or pedigree.at[j, 'mID'] == sibling_id) and \
                   not pd.isna(pedigree.at[j, 'fID'] == sibling_id or pedigree.at[j, 'mID'] == sibling_id):
                    rlt.append({'index': j, 'lineage': 'N'})  # Sobrinho/Sobrinha
    
    # Bisavós (pais dos avós)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'ID'] == fID or pedigree.at[i, 'ID'] == mID) and \
           not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'ID'] == parent_fID or pedigree.at[j, 'ID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'ID']):
                    grandparent_fID = pedigree.at[j, 'fID']
                    grandparent_mID = pedigree.at[j, 'mID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'ID'] == grandparent_fID or pedigree.at[k, 'ID'] == grandparent_mID) and \
                           not pd.isna(pedigree.at[k, 'ID']):
                            rlt.append({'index': k, 'lineage': 'GG'})  # Bisavô/Bisavó
    
    # Bisnetos (filhos dos netos)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID) and \
           not pd.isna(pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID):
            child_id = pedigree.at[i, 'ID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id) and \
                   not pd.isna(pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id):
                    grandchild_id = pedigree.at[j, 'ID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'fID'] == grandchild_id or pedigree.at[k, 'mID'] == grandchild_id) and \
                           not pd.isna(pedigree.at[k, 'fID'] == grandchild_id or pedigree.at[k, 'mID'] == grandchild_id):
                            rlt.append({'index': k, 'lineage': 'GGC'})  # Bisneto/Bisneta
    
    return pd.DataFrame(rlt) if rlt else pd.DataFrame(columns=['index', 'lineage'])

def fourth_degree_relative(pedigree, ii):
    """
    Identifica parentes de quarto grau (primo, prima, tio-avô, tia-avó, sobrinho-neto, sobrinha-neta, trisavô, trisavó, trineto, trineta).
    
    Args:
        pedigree (pd.DataFrame): Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
        ii (int): Índice do indivíduo no pedigree.
    
    Returns:
        pd.DataFrame: Parentes de quarto grau com colunas ['index', 'lineage'].
    """
    num_samples = len(pedigree)
    pedigree = pedigree.copy()
    for i in range(num_samples):
        if pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'fID'] = -999
        if not pd.isna(pedigree.at[i, 'fID']) and pd.isna(pedigree.at[i, 'mID']):
            pedigree.at[i, 'mID'] = -9999
    rlt = []
    
    # Primos (filhos dos tios)
    fID = pedigree.at[ii, 'fID']
    mID = pedigree.at[ii, 'mID']
    for i in range(num_samples):
        if i == ii:
            continue
        parent_fID = None
        parent_mID = None
        if pedigree.at[i, 'ID'] == fID and not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
        elif pedigree.at[i, 'ID'] == mID and not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
        if parent_fID or parent_mID:
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == parent_fID and pedigree.at[j, 'mID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'fID']) and not pd.isna(pedigree.at[j, 'mID']):
                    uncle_id = pedigree.at[j, 'ID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'fID'] == uncle_id or pedigree.at[k, 'mID'] == uncle_id) and \
                           not pd.isna(pedigree.at[k, 'fID'] == uncle_id or pedigree.at[k, 'mID'] == uncle_id):
                            rlt.append({'index': k, 'lineage': 'C'})  # Primo/Prima
    
    # Tios-avôs (irmãos dos avós)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'ID'] == fID or pedigree.at[i, 'ID'] == mID) and \
           not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'ID'] == parent_fID or pedigree.at[j, 'ID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'ID']):
                    grandparent_fID = pedigree.at[j, 'fID']
                    grandparent_mID = pedigree.at[j, 'mID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'fID'] == grandparent_fID and pedigree.at[k, 'mID'] == grandparent_mID) and \
                           not pd.isna(pedigree.at[k, 'fID']) and not pd.isna(pedigree.at[k, 'mID']):
                            rlt.append({'index': k, 'lineage': 'GU'})  # Tio-avô/Tia-avó
    
    # Sobrinhos-netos (filhos dos sobrinhos)
    ID = pedigree.at[ii, 'ID']
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == fID and pedigree.at[i, 'mID'] == mID) and \
           not pd.isna(pedigree.at[i, 'fID']) and not pd.isna(pedigree.at[i, 'mID']):
            sibling_id = pedigree.at[i, 'ID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == sibling_id or pedigree.at[j, 'mID'] == sibling_id) and \
                   not pd.isna(pedigree.at[j, 'fID'] == sibling_id or pedigree.at[j, 'mID'] == sibling_id):
                    nephew_id = pedigree.at[j, 'ID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'fID'] == nephew_id or pedigree.at[k, 'mID'] == nephew_id) and \
                           not pd.isna(pedigree.at[k, 'fID'] == nephew_id or pedigree.at[k, 'mID'] == nephew_id):
                            rlt.append({'index': k, 'lineage': 'GN'})  # Sobrinho-neto/Sobrinha-neta
    
    # Trisavôs (pais dos bisavós)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'ID'] == fID or pedigree.at[i, 'ID'] == mID) and \
           not pd.isna(pedigree.at[i, 'ID']):
            parent_fID = pedigree.at[i, 'fID']
            parent_mID = pedigree.at[i, 'mID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'ID'] == parent_fID or pedigree.at[j, 'ID'] == parent_mID) and \
                   not pd.isna(pedigree.at[j, 'ID']):
                    grandparent_fID = pedigree.at[j, 'fID']
                    grandparent_mID = pedigree.at[j, 'mID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'ID'] == grandparent_fID or pedigree.at[k, 'ID'] == grandparent_mID) and \
                           not pd.isna(pedigree.at[k, 'ID']):
                            great_grandparent_fID = pedigree.at[k, 'fID']
                            great_grandparent_mID = pedigree.at[k, 'mID']
                            for l in range(num_samples):
                                if l == k or l == j or l == i or l == ii:
                                    continue
                                if (pedigree.at[l, 'ID'] == great_grandparent_fID or pedigree.at[l, 'ID'] == great_grandparent_mID) and \
                                   not pd.isna(pedigree.at[l, 'ID']):
                                    rlt.append({'index': l, 'lineage': 'GGG'})  # Trisavô/Trisavó
    
    # Trinetos (filhos dos bisnetos)
    for i in range(num_samples):
        if i == ii:
            continue
        if (pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID) and \
           not pd.isna(pedigree.at[i, 'fID'] == ID or pedigree.at[i, 'mID'] == ID):
            child_id = pedigree.at[i, 'ID']
            for j in range(num_samples):
                if j == i or j == ii:
                    continue
                if (pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id) and \
                   not pd.isna(pedigree.at[j, 'fID'] == child_id or pedigree.at[j, 'mID'] == child_id):
                    grandchild_id = pedigree.at[j, 'ID']
                    for k in range(num_samples):
                        if k == j or k == i or k == ii:
                            continue
                        if (pedigree.at[k, 'fID'] == grandchild_id or pedigree.at[k, 'mID'] == grandchild_id) and \
                           not pd.isna(pedigree.at[k, 'fID'] == grandchild_id or pedigree.at[k, 'mID'] == grandchild_id):
                            great_grandchild_id = pedigree.at[k, 'ID']
                            for l in range(num_samples):
                                if l == k or l == j or l == i or l == ii:
                                    continue
                                if (pedigree.at[l, 'fID'] == great_grandchild_id or pedigree.at[l, 'mID'] == great_grandchild_id) and \
                                   not pd.isna(pedigree.at[l, 'fID'] == great_grandchild_id or pedigree.at[l, 'mID'] == great_grandchild_id):
                                    rlt.append({'index': l, 'lineage': 'GGGC'})  # Trineto/Trineta
    
    return pd.DataFrame(rlt) if rlt else pd.DataFrame(columns=['index', 'lineage'])

def classify_relatives(pedigree, individual_id):
    """
    Classifica parentes de um indivíduo até o quarto grau.
    
    Args:
        pedigree (pd.DataFrame): Pedigree com colunas ['ID', 'fID', 'mID', 'name'].
        individual_id (int): ID do indivíduo a ser analisado.
    
    Returns:
        dict: Dicionário com parentes de primeiro, segundo, terceiro e quarto grau.
    """
    ii = pedigree.index[pedigree['ID'] == individual_id].tolist()
    if not ii:
        raise ValueError(f"ID {individual_id} não encontrado no pedigree.")
    ii = ii[0]
    
    # Primeiro Grau
    fd_relatives = first_degree_relative(pedigree, ii)
    if not fd_relatives.empty:
        fd_relatives['ID'] = pedigree.loc[fd_relatives['index'], 'ID'].values
        fd_relatives['name'] = pedigree.loc[fd_relatives['index'], 'name'].values
        fd_relatives['relationship'] = fd_relatives['lineage'].map({
            'F': 'Pai', 'M': 'Mãe', 'C': 'Filho/Filha'
        })
    else:
        fd_relatives = pd.DataFrame(columns=['ID', 'name', 'relationship'])
    
    # Segundo Grau
    sd_relatives = second_degree_relative(pedigree, ii)
    if not sd_relatives.empty:
        sd_relatives['ID'] = pedigree.loc[sd_relatives['index'], 'ID'].values
        sd_relatives['name'] = pedigree.loc[sd_relatives['index'], 'name'].values
        sd_relatives['relationship'] = sd_relatives['lineage'].map({
            'S': 'Irmão/Irmã', 'G': 'Avô/Avó', 'GC': 'Neto/Neta'
        })
    else:
        sd_relatives = pd.DataFrame(columns=['ID', 'name', 'relationship'])
    
    # Terceiro Grau
    td_relatives = third_degree_relative(pedigree, ii)
    if not td_relatives.empty:
        td_relatives['ID'] = pedigree.loc[td_relatives['index'], 'ID'].values
        td_relatives['name'] = pedigree.loc[td_relatives['index'], 'name'].values
        td_relatives['relationship'] = td_relatives['lineage'].map({
            'U': 'Tio/Tia', 'N': 'Sobrinho/Sobrinha', 'GG': 'Bisavô/Bisavó', 'GGC': 'Bisneto/Bisneta'
        })
    else:
        td_relatives = pd.DataFrame(columns=['ID', 'name', 'relationship'])
    
    # Quarto Grau
    fthd_relatives = fourth_degree_relative(pedigree, ii)
    if not fthd_relatives.empty:
        fthd_relatives['ID'] = pedigree.loc[fthd_relatives['index'], 'ID'].values
        fthd_relatives['name'] = pedigree.loc[fthd_relatives['index'], 'name'].values
        fthd_relatives['relationship'] = fthd_relatives['lineage'].map({
            'C': 'Primo/Prima', 'GU': 'Tio-avô/Tia-avó', 'GN': 'Sobrinho-neto/Sobrinha-neta',
            'GGG': 'Trisavô/Trisavó', 'GGGC': 'Trineto/Trineta'
        })
    else:
        fthd_relatives = pd.DataFrame(columns=['ID', 'name', 'relationship'])
    
    # Exibir resultados
    print(f"Classificação de parentescos para o indivíduo ID {individual_id} ({pedigree.at[ii, 'name']}):")
    print("\nParentes de Primeiro Grau:")
    if not fd_relatives.empty:
        print(fd_relatives[['ID', 'name', 'relationship']].to_string(index=False))
    else:
        print("Nenhum parente de primeiro grau encontrado.")
    print("\nParentes de Segundo Grau:")
    if not sd_relatives.empty:
        print(sd_relatives[['ID', 'name', 'relationship']].to_string(index=False))
    else:
        print("Nenhum parente de segundo grau encontrado.")
    print("\nParentes de Terceiro Grau:")
    if not td_relatives.empty:
        print(td_relatives[['ID', 'name', 'relationship']].to_string(index=False))
    else:
        print("Nenhum parente de terceiro grau encontrado.")
    print("\nParentes de Quarto Grau:")
    if not fthd_relatives.empty:
        print(fthd_relatives[['ID', 'name', 'relationship']].to_string(index=False))
    else:
        print("Nenhum parente de quarto grau encontrado.")
    
    return {
        'first_degree': fd_relatives,
        'second_degree': sd_relatives,
        'third_degree': td_relatives,
        'fourth_degree': fthd_relatives
    }