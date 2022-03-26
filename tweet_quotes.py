import argparse
import utils as ut
import quotes as quo
import artist as art
import vqgan
import gpt3
import numpy as np
import logging


def get_sentence(quote, use_gpt3):
    logger = logging.getLogger("BePequenoVQGAN")
    if use_gpt3:
        gpt3_in_sentence = f"What do you think of {quote} ?"
        vqgan_in_sentence = gpt3.ask(gpt3_in_sentence)
    else:
        vqgan_in_sentence = quote

    vqgan_in_sentence = vqgan.format_input(vqgan_in_sentence)
    logger.info(f"AFTER FORMAT: {vqgan_in_sentence}")

    return vqgan_in_sentence


def get_message(author, quote, work, vqgan_in_sentence, use_gpt3, artist):

    message = f"Quote from #{ut.hashtagify(author)}{f' ({work})' if work != 'Unknown' else ''}: {quote}\n"

    if use_gpt3:
        message += f"#GPT3 reacts: {vqgan_in_sentence}\n"

    if artist:
        message += f"#VQGAN pictures (with #{ut.hashtagify(artist)} inspiration):"
    else:
        message += "#VQGAN pictures:"

    return message


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-tweets', default=1, required=False, type=int)
    parser.add_argument('--seed', default=None, required=False, type=int)
    parser.add_argument('--iterations', default=600, required=False, type=int)
    parser.add_argument('--image-size', default=["400", "400"], required=False, nargs='+', type=str)
    parser.add_argument('--use-gpt3', default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument('--use-artist', default=False, action=argparse.BooleanOptionalAction)


    logger = ut.set_logger()
    args = parser.parse_args()

    n_tweets = args.n_tweets
    seed = args.seed if args.seed else np.random.randint(1e10)
    iterations = args.iterations
    image_size = args.image_size
    use_gpt3 = args.use_gpt3
    use_artist = args.use_artist

    logger.info(f"""
    @bepequeno-vqgan about to tweet {n_tweets} time(s), 
    Painting descriptions:
      - idea code: {seed} (seed)
      - asking a friend: {use_gpt3} (use_gpt3)
      - paint's quantity: {iterations} (iterations)
      - canvas size: {image_size} (image_size)
    """)

    tweepy_api = ut.get_tweepy_api()
    gpt3.set()
    quo.load_quotes()
    art.load_artists()


    #TODO: add random among Europe, America, Asia etc .. : https://www.ezzeddinabdullah.com/posts/get-trending-tweets-python-tweepy 
    #TODO: remove tiret from hashtag 


    chosen_quotes = quo.get_quotes(n_tweets, use_gpt3)
    artists = art.get_artists(n_tweets, use_artist)
        
    for artist, chosen_quote in zip(artists, chosen_quotes):
        quote, work, author = chosen_quote['Quote'], chosen_quote['Work'], chosen_quote['Author']

        vqgan_in_sentence = get_sentence(quote, use_gpt3)
        message = get_message(author, quote, work, vqgan_in_sentence, use_gpt3, artist)
        if artist:
            vqgan_in_sentence += f"|in the style of {artist}:0.5"
        
        logger.info(f"tweet message:\n{message}")

        cli_params = {
            'input_sentence': vqgan_in_sentence,
            'seed': seed,
            'i': iterations,
            'image_name': vqgan.image_name,
            'image_size': ' '.join(image_size),
            'se': iterations - 1
        }
        image_path = vqgan.generate(cli_params)

        tweepy_api.update_status_with_media(status=message, filename=image_path)
        logger.info("@bepequeno-vgan tweeted")





