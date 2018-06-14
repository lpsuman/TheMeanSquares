# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, './train/')

import string
import re
import emojilib #from https://github.com/fvancesco/emoji
from nltk.tokenize import TweetTokenizer



tknz = TweetTokenizer()
delete_hashtags=True

mapping = { '❤':'0' , '😍':'1' , '😂':'2' , '💕':'3' , '🔥':'4' , '😊':'5' , '😎':'6' , '✨':'7' , '💙':'8' , '😘':'9' , '📷':'10' , '🇺🇸':'11' , '☀':'12' , '💜':'13' , '😉':'14' , '💯':'15' , '😁':'16' , '🎄':'17' , '📸':'18' , '😜':'19'}

""" argument
arg[0] - path to tweet txt file
arg[1] - 0 for interpunction erasing, 1 otherwise
arg[2] - how many tweets to process
"""
def clean_text(text, argument=1):
    #remove links, anonymize user mentions
    clean = ""

    # uklanjanje linkova i zamjena imena u @user
    text_new = re.sub( '\s+', ' ', text).strip()
    for t in text_new.split(" "):
        if t.startswith('@') and len(t) > 1:
            clean += "@user "
        elif t.startswith('#') and len(t) > 1 and (delete_hashtags or argument==0):
            pass
        elif t.startswith('http'):
            pass
        else:
            clean += t + " "

    # uklanjanje nepotrebnog znaka
    clean = clean.replace(u'&amp;', "&")

    if argument==0:
        clean = clean.encode('utf-8').translate(None, string.punctuation)
        clean = clean
    elif argument==1:
        # uklanjanje repetitivnih interpunkcija
        clean = re.sub(r'([-+\\\\|()[\]{};:,<>/?@#$%^&*_~\'\"!])\1+', r'\1', clean)

        # tokeniziranje
        clean2 = tknz.tokenize(clean)

        # uklanjane hashtagova!
        if delete_hashtags:
            clean = ""
            for c in clean2:
                if c.startswith('#') and len(c) > 1:
                    pass
                else:
                    clean += c + " "
            clean = clean.rstrip()
        else:
            clean = ' '.join(clean2)

        # uklanjanje nepotrebnih interpunkcija koje u tekstu nemaju neku vaznost
        chars = [' # ',' + ',' * ',' _ ']
        for ch in chars:
            clean = clean.replace(ch, " ")

        # tknz.tokenize() rastavlja slozene emojie pa ih treba sastaviti u jedan
        clean = clean.replace("🇺 🇸", "🇺🇸")

    clean = clean.lower()
    return clean

def obrada_pocetnog_teksta(text_p):
    # uklanjanje svih unicode znakova koji nisu brojke, slova, interpunkcije i nasih 20 emojia
    text = re.sub(
        '[^\u0020-\u007E|\u2764|\U0001f60d|\U0001f602|\U0001f495|\U0001f525|\U0001f60a|\U0001f60e|\u2728|\U0001f499|\U0001f618|\U0001f4f7|\u2600|\U0001f49c|\U0001f609|\U0001f4af|\U0001f601|\U0001f384|\U0001f4f80|\U0001f61c|\U0001f1fa\U0001f1f8]', " ", text_p, re.U)

    # uklanjanje repetitivnih emojia + dodatno uklanjanje emojia "🇺🇸"
    text = re.sub(
        "([\u2764|\U0001f60d|\U0001f602|\U0001f495|\U0001f525|\U0001f60a|\U0001f60e|\u2728|\U0001f499|\U0001f618|\U0001f4f7|\u2600|\U0001f49c|\U0001f609|\U0001f4af|\U0001f601|\U0001f384|\U0001f4f80|\U0001f61c])\1+", r'\1', text, flags=re.UNICODE)
    text = re.sub("(\U0001f1fa\U0001f1f8)\1+", r'\1', text, flags=re.UNICODE)

    # stavljanje razmaka između emojia
    text_de = emojilib.demojize(text, delimiters = (" ~~", "~~ "))
    text = emojilib.emojize(text_de, delimiters = ("~~", "~~"))

    # trimanje duplih razmaka nakon obrade
    text = " ".join(text.split())
    text += " " # dodavanje razmak na kraju texta da regex moze biti primjenjen i na kraju

    # uklanjanje repetitivnih emojia koji su odvojeni razmakom, npr. "❤ ❤ ❤" u "❤"
    text = re.sub(
        "([\u2764|\U0001f60d|\U0001f602|\U0001f495|\U0001f525|\U0001f60a|\U0001f60e|\u2728|\U0001f499|\U0001f618|\U0001f4f7|\u2600|\U0001f49c|\U0001f609|\U0001f4af|\U0001f601|\U0001f384|\U0001f4f80|\U0001f61c]\s)\1+", r'\1', text, flags=re.UNICODE)
    text = re.sub("(\U0001f1fa\U0001f1f8\s)\1+", r'\1', text, flags=re.UNICODE)
    text = text.rstrip()
    return text



def process_tweet(tweet):
    emo_list = emojilib.emoji_list(tweet)

    # obrada pocetnog teksta
    text = obrada_pocetnog_teksta(tweet)
    ct = clean_text(text)

    ct = obrada_pocetnog_teksta(ct)
    ct_tokens = ct.split()

    # PROVJERA
    # - provjera da duljina teksta nije > 30 rijeci
    # - ako su unutar teksta emoji, njih ne uzimamo kao rijec
    if len(ct_tokens) > 30:
        ct_tokens_temp = ct_tokens[:31]
        ct_temp = " ".join(ct_tokens_temp)

        emo_list = emojilib.emoji_list(ct_temp)
        ct_length = 30 + len(emo_list)

        ct_tokens = ct_tokens[:ct_length]
        ct = " ".join(ct_tokens)

    emo_list = emojilib.emoji_list(ct)

    emo_set = [d['code'] for d in emo_list if 'code' in d]

    emo_location = [d['location'] for d in emo_list if 'location' in d]

    pos = 0
    br_emojies = 0
    locations = list("0000000000000000000000000000000")
    types = list("0000000000000000000000000000000")

    for tok in ct_tokens:
        pos += 1
        if tok in emo_set:
            emo = tok.encode('utf_8')
            types[pos - br_emojies - 1] = mapping[emo]
            locations[pos - br_emojies - 1] = '1'
            br_emojies += 1

    # Upis cistog teksta u datoteku
    ct_no_emoji = emojilib.replace_emoji(ct, replacement=' ')
    ct_no_emoji_new = ' '.join(ct_no_emoji.split())

    return ct_no_emoji_new