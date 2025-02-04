from datasetsforecast.m3 import M3
from cardtale.cards.builder import CardsBuilder

df, *_ = M3.load('./assets', group='Monthly')

freq = 'ME'
uid = 'M1080'

series_df = df.query(f'unique_id=="{uid}"').reset_index(drop=True)

tcard = CardsBuilder(series_df, freq)
tcard.build_cards()
tcard.get_pdf(path='notebooks/cards/example.pdf')
