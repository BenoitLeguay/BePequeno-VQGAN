import argparse
import utils as ut
import artist as art
import vqgan
import gpt3
import numpy as np
import logging


def get_locations(tweepy_api, n_tweets):
    available_location_trends = tweepy_api.available_trends()
    if select_best_locations:
        chosen_locations = available_location_trends[:n_tweets]
    else:
        chosen_locations = np.random.choice(available_location_trends, size=(n_tweets,), replace=False)
    return chosen_locations


def get_trends(tweepy_api, n_trends):
    available_trends = tweepy_api.get_place_trends(location['woeid'], exclude="hashtags")[0]
    if select_best_trends:
        chosen_trends = available_trends['trends'][:n_trends]
    else:
        chosen_trends = np.random.choice(available_trends['trends'], size=(n_trends,), replace=False)
    trends_name = [trend_['name'] for trend_ in chosen_trends]

    return trends_name


def get_sentence(trends, location, use_gpt3=True):
    logger = logging.getLogger("BePequenoVQGAN")
    if use_gpt3:
        gpt3_out_sentences = list()
        for idx, trend in enumerate(trends):
            
            gpt3_in_sentence = f"What do you think of {trend} ?" #, in {location}
            gpt3_out_sentences.append(gpt3.ask(gpt3_in_sentence))
            logger.info(f"sentence {idx+1}: {gpt3_out_sentences[idx]}")

        vqgan_in_sentence = "| ".join(gpt3_out_sentences)
    else:
        vqgan_in_sentence = "| ".join(trends)

    vqgan_in_sentence = vqgan.format_input(vqgan_in_sentence)
    logger.info(f"AFTER FORMAT: {vqgan_in_sentence}")

    return vqgan_in_sentence


def get_message(location_name, trends, vqgan_in_sentence, artist, use_gpt3):

    trends = [ut.hashtagify(trend) for trend in trends]

    message = f"trends in #{ut.hashtagify(location_name)}: "
    message += f"#{' and #'.join(trends)}\n"
    if use_gpt3:
        message += f"#GPT3 reacts: {'.'.join([s for s in vqgan_in_sentence.split('|')])}\n"

    if artist:
        message += f"#VQGAN pictures (with #{ut.hashtagify(artist)} inspiration):"
    else:
        message += "#VQGAN pictures:"

    return message


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--n-tweets', default=1, required=False, type=int)
    parser.add_argument('--n-trends', default=2, required=False, type=int)
    parser.add_argument('--seed', default=None, required=False, type=int)
    parser.add_argument('--iterations', default=600, required=False, type=int)
    parser.add_argument('--image-size', default=["400", "400"], required=False, nargs='+', type=str)

    parser.add_argument('--use-gpt3', default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument('--use-artist', default=True, action=argparse.BooleanOptionalAction)

    parser.add_argument('--select-random-locations', default=False, required=False, dest='select_best_locations', action='store_false')
    parser.add_argument('--select-best-locations', default=False, required=False, dest='select_best_locations', action='store_true')
    parser.set_defaults(select_best_locations=True)
    parser.add_argument('--select-random-trends', default=False, required=False, dest='select_best_trends', action='store_false')
    parser.add_argument('--select-best-trends', default=False, required=False, dest='select_best_trends', action='store_true')
    parser.set_defaults(select_best_trends=True)

    logger = ut.set_logger()
    args = parser.parse_args()

    n_tweets = args.n_tweets
    n_trends = args.n_trends
    seed = args.seed if args.seed else np.random.randint(1e10)
    iterations = args.iterations
    image_size = args.image_size
    use_gpt3 = args.use_gpt3
    use_artist = args.use_artist
    select_best_locations = args.select_best_locations
    select_best_trends = args.select_best_trends

    logger.info(f"""
    @bepequeno-vqgan about to tweet {n_tweets} time(s), 
    Painting descriptions:
      - idea code: {seed} (seed)
      - idea's quantity: {n_trends} (n_trends)
      - asking a friend: {use_gpt3} (use_gpt3)
      - paint's quantity: {iterations} (iterations)
      - canvas size: {image_size} (image_size)
      - choosing {'most trendy' if select_best_locations else 'random'} locations
      - choosing {'best' if select_best_trends else 'random'} trends
    """)

    tweepy_api = ut.get_tweepy_api()
    gpt3.set()
    art.load_artists()


    #TODO: add random among Europe, America, Asia etc .. : https://www.ezzeddinabdullah.com/posts/get-trending-tweets-python-tweepy 
    #TODO: remove tiret from hashtag 


    locations = get_locations(tweepy_api, n_tweets)
    artists = art.get_artists(n_tweets, use_artist)
        
    for location, artist in zip(locations, artists):
        location_name = location['name']
        trends = get_trends(tweepy_api, n_trends)
        logger.info(trends)

        vqgan_in_sentence = get_sentence(trends, location_name, use_gpt3=use_gpt3)

        message = get_message(location_name, trends, vqgan_in_sentence, artist, use_gpt3)

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





