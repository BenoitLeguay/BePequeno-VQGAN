from string import Template
import logging
import os
import re

vqgan_dir = '/home/bepequeno/work/VQGAN-CLIP'
image_name = 'image_to_tweet.png'
uncompatible_chars = [':', '“', '”', '"']
cli_template = Template('''
    python generate.py \\
        -p " $input_sentence" \\
        -sd $seed \\
        -i $i \\
        -o $image_name \\
        -s $image_size \\
        -se $se
''')


def format_input(sentence):
    global uncompatible_chars
    sentence = sentence.replace("\n", "")
    regex_uncompatible_chars = f'[{"".join(uncompatible_chars)}]'
    return re.sub(regex_uncompatible_chars, "", sentence)


def generate(cli_params):
    logger = logging.getLogger("BePequenoVQGAN")
    global vqgan_dir
    global cli_template
    cwd = os.getcwd()

    cli = cli_template.substitute(cli_params)

    os.chdir(vqgan_dir)
    logger.info("VQGAN takes its brushes out...")
    logger.info(cli)
    #subprocess.run(cli, cwd=vqgan_dir, shell=True) try check_call
    has_finished = os.system(cli)
    logger.info("VQGAN is done painting :)")
    os.chdir(cwd)

    return os.path.join(vqgan_dir, image_name)