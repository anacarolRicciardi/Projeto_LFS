# PROJETO_LFS
Projeto para classificação e predição da Síndrome de Li-Fraumeni (LFS) com base em características clínicas.

## Estrutura
- data/: Dados brutos e processados.
- src/: Códigos-fonte.
- scripts/: Scripts para execução de tarefas.

##PROJETO_LFS/
│
├── venv/                    # Ambiente virtual (já criado)
│   ├── Scripts/             # Arquivos de ativação (activate, activate.bat, etc.)
│   └── ...
│
├── data/                    # Diretório para dados
│   ├── raw/                 # Dados brutos (ex.: dataset.csv)
│   │   └── dataset.csv
│   └── processed/           # Dados processados (ex.: pedigrees, classificações)
│       ├── pedigrees.csv
│       └── classifications.csv
│
├── src/                     # Diretório para os códigos-fonte
│   ├── __init__.py          # Torna src um módulo Python
│   ├── pedigree.py          # Código para caracterizar graus de parentesco
│   ├── chompret.py          # Código para classificar critérios de Chompret
│   ├── model.py             # Código para treinar e predizer LFS (futuro modelo de ML)
│   └── utils.py             # Funções utilitárias (ex.: carregamento de dados)
│
├── scripts/                 # Scripts para executar tarefas específicas
│   ├── process_pedigree.py  # Script para processar graus de parentesco
│   ├── classify_chompret.py # Script para classificar critérios de Chompret
│   └── train_predict.py     # Script para treinar e predizer LFS (futuro)
│
├── requirements.txt         # Dependências do projeto
└── README.md                # Documentação do projeto