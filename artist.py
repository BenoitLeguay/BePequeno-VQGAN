import pandas as pd
import os
import numpy as np
import utils as ut
artists = None

def load_artists():
    global artists
    artists = pd.read_csv(os.path.join(ut.data_path, 'artists.csv'))['name'].values

def get_artists(n, use_artist):
    if not use_artist:
        return [None]*n

    global artists
    assert artists is not None, "load artist before getting one"
    artists = np.random.choice(artists, size=(n,), replace=False)
    return artists

def add_artiste_to_sentence(sentence, artist, weight=0.5):
    sentence = f"{sentence} | in the style of {artist}: {weight}"
