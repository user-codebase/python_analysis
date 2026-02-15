import pandas as pd

data = pd.read_html('https://www.officialcharts.com/chart-news/the-best-selling-albums-of-all-time-on-the-official-uk-chart__15551/', header=0)

df = data[0]

# punk 1
df = df[['TITLE','ARTIST','YEAR','HIGH POSN']]
df.columns = ['TYTUŁ','ARTYSTA','ROK','MAX POZ']

# punk 2
liczba_artystow = df['ARTYSTA'].nunique()
print("Liczba unikalnych artystow:", liczba_artystow)

# punk 3
najczestsze_zespoly = df['ARTYSTA'].value_counts().head()
print("\nNajczesciej pojawiajace sie zespoly:")
print(najczestsze_zespoly)

# punk 4
print("\ndf.columns przed zmiana 'capitalize':", df.columns)
df.columns = [col.capitalize() for col in df.columns]
print("df.columns po zmianie 'capitalize'", df.columns)

# punk 5
print("\ndf.columns przed drop 'Max poz':", df.columns)
df = df.drop(columns=['Max poz'])
print("df.columns po drop 'Max poz':", df.columns)

# punk 6
rok_najwiecej_albumow = df['Rok'].value_counts().idxmax()
print("\nRok z największą liczbą albumów:", rok_najwiecej_albumow)

# punk 7
liczba_albumow_1960_1990 = df[(df['Rok'] >= 1960) & (df['Rok'] <= 1990)].shape[0]
print("Liczba albumow wydanych miedzy 1960 a 1990:", liczba_albumow_1960_1990)

# punk 8
najmlodszy_album = df['Rok'].max()
print("Najmlodszy album wydany w roku:", najmlodszy_album)

# punk 9
najwczesniejsze_albumy = df.loc[df.groupby('Artysta')['Rok'].idxmin()]

# punk 10
najwczesniejsze_albumy.to_csv("najwczesniejsze_albumy.csv", index=False)
print("\nLista najwczesniejszych albumow zostala zapisana do 'najwczesniejsze_albumy.csv'")