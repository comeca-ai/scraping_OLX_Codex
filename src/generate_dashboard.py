import json
from pathlib import Path

import pandas as pd
import plotly.express as px


DATA_DIR = Path("data")
OUTPUT_HTML = DATA_DIR / "dashboard.html"


def load_data() -> pd.DataFrame:
    json_path = DATA_DIR / "olx_properties.json"
    if not json_path.exists():
        raise FileNotFoundError("Run scrape_olx.py first to generate data")
    with json_path.open("r", encoding="utf-8") as jf:
        items = json.load(jf)
    return pd.DataFrame(items)


def build_dashboard(df: pd.DataFrame) -> str:
    # Clean columns
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")

    # Neighborhood from location field if possible
    if "location" in df.columns:
        df["neighborhood"] = df["location"].str.split(" - ").str[0]
    else:
        df["neighborhood"] = "N/A"

    charts = []
    # Number of houses by neighborhood
    count_series = df.groupby("neighborhood").size().reset_index(name="count")
    fig_count = px.bar(
        count_series,
        x="neighborhood",
        y="count",
        title="N\u00famero de casas por bairro",
    )
    charts.append(fig_count.to_html(full_html=False, include_plotlyjs="cdn"))

    # Average price by neighborhood
    if "price" in df.columns:
        avg_price = df.groupby("neighborhood")["price"].mean().reset_index()
        fig_price = px.bar(
            avg_price,
            x="neighborhood",
            y="price",
            title="Pre\u00e7o m\u00e9dio por bairro",
        )
        charts.append(fig_price.to_html(full_html=False, include_plotlyjs="cdn"))

    body = "\n".join(charts)
    html = f"""
<!DOCTYPE html>
<html lang='pt-BR'>
<head>
    <meta charset='utf-8'>
    <title>Dashboard OLX</title>
</head>
<body>
    <h1>Dashboard OLX Im\u00f3veis - Jo\u00e3o Pessoa</h1>
    {body}
</body>
</html>
"""
    return html


def main():
    df = load_data()
    html = build_dashboard(df)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Dashboard salvo em {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
