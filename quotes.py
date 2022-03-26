import pandas as pd
import json
import utils as ut 
import os
quotes = None


def preprocess_quotes():
    with open(os.path.join(ut.data_path, 'quotes.json')) as f:
        quotes_json = json.load(f)
    quotes = pd.DataFrame(quotes_json)

    quotes.drop(columns=['Tags', 'Category'], inplace=True)
    quotes.drop_duplicates(subset=['Quote', 'Author'], inplace=True)

    quotes['lenght'] = quotes.Quote.apply(lambda x: len(x)) + quotes.Author.apply(lambda x: len(x))
    quotes['has_been_used'] = False
    
    auth_work = quotes.Author.apply(ut.split_auth_work)
    auth_work = pd.DataFrame([[auth, work] for auth, work in auth_work.values], columns=['Author', 'Work'], index=quotes.index).fillna('Unknown')
    quotes = pd.concat([auth_work, quotes.drop(columns='Author')], axis=1)

    quotes.to_csv(os.path.join(ut.data_path, 'quotes.csv'))


def load_quotes():
    global quotes
    quotes = pd.read_csv(os.path.join(ut.data_path, 'quotes.csv'), index_col=0)


def get_quotes(n, use_gpt3):
    max_lenght = 170 if use_gpt3 else 220

    global quotes
    assert quotes is not None, "Load quotes before getting one"

    chosen_quote= quotes.loc[(quotes.lenght < max_lenght) & (~quotes.has_been_used)].sample(n)
    assert len(chosen_quote) > 0, 'no quote left'

    quotes.loc[chosen_quote.index, 'has_been_used'] = True
    quotes.to_csv(os.path.join(ut.data_path, 'quotes.csv'))

    return chosen_quote[['Quote', 'Work', 'Author']].to_dict(orient='records')