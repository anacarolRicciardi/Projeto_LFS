# src/chompret.py

import pandas as pd

# Tipos de câncer do espectro LFS (baseado em Chompret)
LFS_TUMORS = {3, 7, 8, 9, 11, 12, 13, 14, 15}  # Mama, Plexo coroide, Adrenocortical, Leucemia, Pulmão, Sarcoma, Cérebro, Rabdóide, Osso

def check_chompret_2015(row):
    proband_cancers = {i for i in range(1, 16) if row.get(f'era_tipo_ca___{i}', 0) == 1}
    proband_ages = {
        1: row.get('idade_dx_ca_ovario'), 2: row.get('idade_dx_ca_pele'), 3: row.get('idade_dx_ca_mama'),
        4: row.get('idade_dx_ca_prostata'), 10: row.get('idade_dx_ca_outro')
    }
    proband_multi_tumors = len(proband_cancers) > 1
    proband_lfs_tumor = bool(proband_cancers & LFS_TUMORS)
    # Garantir que a idade seja um número ou float('inf') para comparações seguras
    proband_lfs_age = any(
        (age if age is not None else float('inf')) < 46
        for t in proband_cancers & LFS_TUMORS
        for age in [proband_ages.get(t, float('inf'))]
    )
    proband_breast_age = (proband_ages.get(3) or float('inf')) < 31
    
    family_cancers = []
    family_ages = []
    for rel, rel_key, age_key in [
        ('pai', 'tipo_ca_pai___', 'idade_ca_'), ('mae', 'tipo_ca_mae___', 'idade_ca_'),
        ('filho', 'tipo_ca_filho1___', 'idade_ca_filho1'), ('irmao', 'tipo_ca_irmao1___', 'idade_ca_irmao1'),
        ('avo_paterno', 'tipo_ca_avo_h_paterno___', 'idade_ca_'), ('avo_paterna', 'tipo_ca_avo_m_paterno___', 'idade_ca_'),
        ('avo_materno', 'tipo_ca_avo_h_materno___', 'idade_ca_'), ('avo_materna', 'tipo_ca_avo_m_materno___', 'idade_ca_'),
        ('tio_paterno', 'tipo_ca_tios_paternos1___', 'idade_ca_tios_paternos1'),
        ('tio_materno', 'tipo_ca_tios_maternos1___', 'idade_ca_tios_maternos1')
    ]:
        if row.get(f'{rel}_teve_tem_ca', 0) == 1 or (rel in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] and row.get(f'algum_{rel}_teve_ca', 0) == 1):
            rel_cancers = {i for i in range(1, 16) if row.get(f'{rel_key}{i}', 0) == 1}
            rel_age = row.get(age_key if rel not in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] else age_key, float('inf'))
            family_cancers.extend(rel_cancers)
            family_ages.append(rel_age)
    family_lfs_tumor = bool(set(family_cancers) & LFS_TUMORS)
    family_lfs_age = any(age < 56 for age in family_ages if age is not None)
    
    crit1 = proband_lfs_tumor and proband_lfs_age and family_lfs_tumor and family_lfs_age
    crit2 = proband_multi_tumors and proband_lfs_tumor and proband_lfs_age
    crit3 = 7 in proband_cancers or 8 in proband_cancers or 14 in proband_cancers  # Plexo coroide, Adrenocortical, Rabdóide
    crit4 = proband_breast_age
    
    return crit1 or crit2 or crit3 or crit4

def check_chompret_2009(row):
    proband_cancers = {i for i in range(1, 16) if row.get(f'era_tipo_ca___{i}', 0) == 1}
    proband_ages = {
        1: row.get('idade_dx_ca_ovario'), 2: row.get('idade_dx_ca_pele'), 3: row.get('idade_dx_ca_mama'),
        4: row.get('idade_dx_ca_prostata'), 10: row.get('idade_dx_ca_outro')
    }
    proband_multi_tumors = len(proband_cancers) > 1
    proband_lfs_tumor = bool(proband_cancers & LFS_TUMORS)
    proband_lfs_age = any(
        (age if age is not None else float('inf')) < 46
        for t in proband_cancers & LFS_TUMORS
        for age in [proband_ages.get(t, float('inf'))]
    )
    
    family_cancers = []
    family_ages = []
    for rel, rel_key, age_key in [
        ('pai', 'tipo_ca_pai___', 'idade_ca_'), ('mae', 'tipo_ca_mae___', 'idade_ca_'),
        ('filho', 'tipo_ca_filho1___', 'idade_ca_filho1'), ('irmao', 'tipo_ca_irmao1___', 'idade_ca_irmao1'),
        ('avo_paterno', 'tipo_ca_avo_h_paterno___', 'idade_ca_'), ('avo_paterna', 'tipo_ca_avo_m_paterno___', 'idade_ca_'),
        ('avo_materno', 'tipo_ca_avo_h_materno___', 'idade_ca_'), ('avo_materna', 'tipo_ca_avo_m_materno___', 'idade_ca_'),
        ('tio_paterno', 'tipo_ca_tios_paternos1___', 'idade_ca_tios_paternos1'),
        ('tio_materno', 'tipo_ca_tios_maternos1___', 'idade_ca_tios_maternos1')
    ]:
        if row.get(f'{rel}_teve_tem_ca', 0) == 1 or (rel in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] and row.get(f'algum_{rel}_teve_ca', 0) == 1):
            rel_cancers = {i for i in range(1, 16) if row.get(f'{rel_key}{i}', 0) == 1}
            rel_age = row.get(age_key if rel not in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] else age_key, float('inf'))
            family_cancers.extend(rel_cancers)
            family_ages.append(rel_age)
    family_lfs_tumor = bool(set(family_cancers) & LFS_TUMORS)
    family_lfs_age = any(age < 56 for age in family_ages if age is not None)
    
    crit1 = proband_lfs_tumor and proband_lfs_age and family_lfs_tumor and family_lfs_age
    crit2 = proband_multi_tumors and proband_lfs_tumor and proband_lfs_age
    crit3 = 7 in proband_cancers or 8 in proband_cancers  # Plexo coroide, Adrenocortical
    
    return crit1 or crit2 or crit3

def check_classic(row):
    proband_cancers = {i for i in range(1, 16) if row.get(f'era_tipo_ca___{i}', 0) == 1}
    proband_ages = {
        1: row.get('idade_dx_ca_ovario'), 2: row.get('idade_dx_ca_pele'), 3: row.get('idade_dx_ca_mama'),
        4: row.get('idade_dx_ca_prostata'), 10: row.get('idade_dx_ca_outro')
    }
    sarcoma = 12 in proband_cancers or 15 in proband_cancers  # Sarcoma ou Osteossarcoma
    sarcoma_age = any(
        (age if age is not None else float('inf')) < 45
        for t in {12, 15} & proband_cancers
        for age in [proband_ages.get(t, float('inf'))]
    )
    
    first_degree = []
    second_degree = []
    for rel, rel_key, age_key in [
        ('pai', 'tipo_ca_pai___', 'idade_ca_'), ('mae', 'tipo_ca_mae___', 'idade_ca_'),
        ('filho', 'tipo_ca_filho1___', 'idade_ca_filho1'), ('irmao', 'tipo_ca_irmao1___', 'idade_ca_irmao1'),
        ('avo_paterno', 'tipo_ca_avo_h_paterno___', 'idade_ca_'), ('avo_paterna', 'tipo_ca_avo_m_paterno___', 'idade_ca_'),
        ('avo_materno', 'tipo_ca_avo_h_materno___', 'idade_ca_'), ('avo_materna', 'tipo_ca_avo_m_materno___', 'idade_ca_'),
        ('tio_paterno', 'tipo_ca_tios_paternos1___', 'idade_ca_tios_paternos1'),
        ('tio_materno', 'tipo_ca_tios_maternos1___', 'idade_ca_tios_maternos1')
    ]:
        if row.get(f'{rel}_teve_tem_ca', 0) == 1 or (rel in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] and row.get(f'algum_{rel}_teve_ca', 0) == 1):
            rel_cancers = {i for i in range(1, 16) if row.get(f'{rel_key}{i}', 0) == 1}
            rel_age = row.get(age_key if rel not in ['filho', 'irmao', 'tio_paterno', 'tio_materno'] else age_key, float('inf'))
            if rel in ['pai', 'mae', 'filho', 'irmao']:
                first_degree.append((rel_cancers, rel_age))
            else:
                second_degree.append((rel_cancers, rel_age))
    
    first_degree_cancer = any(age < 45 for _, age in first_degree if age is not None)
    second_degree_cancer = any(age < 45 or 12 in cancers or 15 in cancers for cancers, age in second_degree if age is not None)
    
    return sarcoma and sarcoma_age and first_degree_cancer and second_degree_cancer

def classify_lfs_criteria(data):
    results = pd.DataFrame(index=data.index, columns=['Chompret_2015', 'Chompret_2009', 'Classic'])
    for idx, row in data.iterrows():
        results.loc[idx, 'Chompret_2015'] = check_chompret_2015(row)
        results.loc[idx, 'Chompret_2009'] = check_chompret_2009(row)
        results.loc[idx, 'Classic'] = check_classic(row)
    return results