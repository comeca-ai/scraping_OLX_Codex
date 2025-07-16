# OLX Scraper

Este reposit\u00F3rio cont\u00E9m scripts em Python para extrair dados de im\u00F3veis do site [OLX](https://www.olx.com.br/imoveis/estado-pb/paraiba/joao-pessoa).
O objetivo \u00E9 gerar arquivos `JSON` e `CSV` contendo as informa\u00E7\u00F5es de cada an\u00FAncio e, ao final, montar um dashboard em HTML com m\u00E9tricas como n\u00FAmero de casas por bairro e pre\u00E7o m\u00E9dio.

## Requisitos

- Python 3.12+
- Depend\u00EAncias: `requests`, `beautifulsoup4`, `pandas`, `plotly`, `tqdm`

Instale as depend\u00EAncias com:

```bash
pip install -r requirements.txt
```

## Uso

1. Para realizar o scraping (pode demorar pois acessa v\u00E1rias p\u00E1ginas):

```bash
python src/scrape_olx.py
```

Ser\u00E3o gerados os arquivos `data/olx_properties.json` e `data/olx_properties.csv`.

2. Para criar o dashboard em HTML a partir dos dados extra\u00EDdos:

```bash
python src/generate_dashboard.py
```

O resultado ser\u00E1 salvo em `data/dashboard.html`.

## Observa\u00E7\u00F5es

- Os scripts dependem do formato atual do site da OLX e podem precisar de ajustes se o layout mudar.
- Para coletar mais p\u00E1ginas, ajuste o par\u00E2metro `max_pages` em `scrape_olx.py`.
