import pandas as pd

print("=== INSPECTING filmes.xls ===")
try:
    xls = pd.ExcelFile('filmes.xls')
    print("Sheets:", xls.sheet_names)
    for sheet in xls.sheet_names:
        df = pd.read_excel('filmes.xls', sheet_name=sheet)
        print(f"\nSheet: {sheet}")
        print("Columns:", list(df.columns))
        print(df.head(2))
except Exception as e:
    print("Error filmes.xls:", e)

print("\n=== INSPECTING usa_deaths.csv ===")
try:
    df_usa = pd.read_csv('usa_deaths.csv')
    print("Columns:", list(df_usa.columns))
    print(df_usa.head(2))
except Exception as e:
    print("Error usa_deaths.csv:", e)

print("\n=== INSPECTING world_deaths.csv ===")
try:
    df_world = pd.read_csv('world_deaths.csv')
    print("Columns:", list(df_world.columns[:10]), "... total columns:", len(df_world.columns))
    print(df_world.head(2))
except Exception as e:
    print("Error world_deaths.csv:", e)
