# -*- coding: utf-8 -*-

import re


class Saniteze:

    def __init__(self):
        pass

    def extract(self, string: str):
        string = string.lower()
        # Rimuove new line
        string = string.replace('\n', ' ')
        # Rimuove emoji e '()' di alcune date
        string = re.sub(u'[📆📚🎬🖋⭐]', ' ', string, re.IGNORECASE)
        # Ottengo e salvo l'anno di pubblicazione/uscita ( italia serie e cartoon )
        years = re.findall(r'(?<!\d)\d{4,7}(?!\d)', string, re.IGNORECASE)
        new_string = re.sub(r'(?<!\d)\d{4,7}(?!\d)', ' ', string, re.IGNORECASE)
        year = ''
        if years:
            year = years[0]
        string = new_string
        # Divido #hastag dal titolo e creo un elenco
        string, keyword_list = self.identify_hash(string)
        # Cerca info descrittivi del video nelle parentesi quadre ( dvd,rip ecc)
        search_in_bracket = re.finditer(r'(?<=\[)(.*?)(?=\])', string, re.IGNORECASE)
        tag_list = []
        for sub_str in search_in_bracket:
            string_no_tag, tags = self.identify_tag(sub_str.group())
            # esiste ?
            if tags:
                tag_list.append(sub_str.group())
            string = string[:sub_str.start(0) - 1].strip()

        # Rimuove 'Trama' fino a fine stringa
        string = re.sub(r'\btrama(.*)$', '', string, re.IGNORECASE)
        # Rimuove 'Imdb' fino a fine stringa
        string = re.sub(r'\bimdb(.*)$', '', string, re.IGNORECASE)
        # Rimuove 'Durata' fino a fine stringa
        string = re.sub(r'\bdurata(.*)$', '', string, re.IGNORECASE)
        # Rimuove 'Anno' fino a fine stringa
        string = re.sub(r'\banno:(.*)$', '', string, re.IGNORECASE)

        # ------------------------------------------------------------------------------
        # Cartoons zone
        #
        # Rimuove 'Episodi' fino a fine stringa
        string = re.sub(r'\bepisod(.*)$', '', string, re.IGNORECASE)
        # Rimuove 'Epiisodi' fino a fine stringa
        string = re.sub(r'\bepiisod(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo '(' e ')' ( informazioni già estratte sopra)
        string = re.sub(r'(?=\()(.*?)(?=\))(.*)$', '', string, re.IGNORECASE)
        # Rimuovo anno di uscita in italia ( Plex considera l'anno originale)
        string = re.sub(r'\bin italia(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo '–' ( informazioni già estratte sopra).Compreso '?' special char
        # string = re.sub(r' – (.*)$', '', string, re.IGNORECASE)
        # SOSPESO (test con del_div)
        # Rimuovo tutti i riferimenti alle raccolte
        string = re.sub(r'\braccolta(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo 'Stagione' ( informazioni già estratte sopra)
        string = re.sub(r'\bstagione(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo 'Genere' ( informazioni già estratte sopra)
        string = re.sub(r'\bgenere(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo 'Voto' ( informazioni già estratte sopra)
        # string = re.sub(r'\bvoto(.*)$', '', string, re.IGNORECASE)
        # Rimuove tutto le info dopo 'collection' ( informazioni già estratte sopra)
        string = re.sub(r'\bcollection(.*)$', '', string, re.IGNORECASE)
        # Rimuove descrizione degli episodi nel titolo.....1
        string = re.sub(r' ep\d+(.*)$', '', string, re.IGNORECASE)
        # Rimuove descrizione degli episodi nel titolo.....2
        string = re.sub(r' ep \d+(.*)$', '', string, re.IGNORECASE)
        # Rimuove descrizione part 1 2 3.. nel titolo.....
        string = re.sub(r' part \d+(.*)$', '', string, re.IGNORECASE)

        # In test : Elimina la parte di titolo dal secondo character
        # Solitamente dopo il primo character viene inserita la seconda parte del titolo

        string = self.del_div(string, '-')
        string = self.del_div(string, '–')
        string = string.replace('(', '')
        string = string.replace(')', '')

        # Rigenero la stringa di uscita
        tokens = string.split(' ')
        string = ' '.join(new_string.strip() for new_string in tokens if new_string.strip())

        return {'title': string, 'year': year, 'tags': tag_list, 'keywords': keyword_list}

    def identify_hash(self, string):
        word_list = string.lower().strip().split(' ')
        tag_list = []
        locandina = ""
        for word in word_list:
            if self.hashtag(word) or '[sub-ita]' in word:
                tag_list.append(word)
            if not self.hashtag(word):
                # Se non esiste ricrea la string
                # ma priva di #tag
                if '#' not in word:
                    locandina += word + ' '
        locandina = locandina.strip()
        return locandina, tag_list

    def del_div(self, string, character):
        # In test : Elimina la parte di titolo dal secondo character
        # Solitamente dopo il primo character '-' viene inserita la seconda parte del titolo
        # TEST 03/04/2022 - devo escludere dall'eliminazione i titoli come 'yu-gi-ho'
        # Quindi non elimnina più la parte di titolo dal secondo '-'.
        # ma dal terzo '-'.
        # esempio:
        # 'Yu-Gi-Oh! - Capsule Monsters-ciao-bye'
        # span = [2, 5, 10, 28, 33] ovvero dove sono i caratteri '-'
        # conserva stringa da span[2]+1 a span[3] ovvero con un indice da 10+1 a 28 (chars)
        # il resto non viene considerato come titolo e lo scarta quindi -> 'yu-gi-oh! - capsule monsters'
        span = [m.start() for m in re.finditer(character, string)]
        tag_name = self.tagintitle(string)
        if tag_name:
            if len(span) > 3:
                chars = (string[span[2] + 1:span[3]]).strip()
                # Devo eliminare i '-' se non ci sono stringhe delimitate es. 'x-man -  -'
                if not chars:
                    # Non cancello tutte le '-'. Conservo tag_name e lo aggiungo dopo
                    string = string.replace(tag_name, '').strip()
                    string = string.replace(character, '').strip()
                    string = f'{tag_name} {string}'
                else:
                    string = string[:span[3]].strip()
                    print(string)
        else:
            # Nel caso di titoli ove non occorre conservare nomi con all'interno '-'
            # span = [m.start() for m in re.finditer(character, string)]
            if len(span) > 1:
                # Se tra i due divisorii rimane solo spazio li elimina entrambi
                # altrimenti strip solo la stringa
                chars = (string[span[0] + 1:span[1]]).strip()
                if not chars:
                    string = string.replace(character, '').strip()
                else:
                    string = string[:span[1]].strip()
        # Clean : Si assicura che character non sia l'ultimo carattere della stringa
        string = string.strip()
        if string:
            while string[-1] == character:
                string = string[:-1].strip()
        else:
            string = 'nessun titolo'
        return string

    def tagintitle(self, stringa):
        word_list = stringa.lower().strip().split(' ')

        lista = [
            "yu-gi-oh!",
            "yu-gi-oh",
            "spider-man",
            "spider-man:",
            "super-man",
            "scooby-doo!",
            "scooby-doo",
            "9-1-1",
            "9-1-1:",
            "week-end",
            "x-man",
            "sg-1",  # Stargate SG-1
            "kick-ass",
            "five-0",  # Hawaii Five-0
            "ant-man",
            "a-team",
            "punch-drunk",
            "so-called",  # so-called life
            "non-stop",
            "semi-pro",
            "blow-up",
            "five-year",  # The Five-Year Engagement (2012)
            "butt-head",  # Beavis and Butt-Head (1993–2011)
            "psycho-Pass",
            "hi-de-hi!",
            "monster-in-law"
            "3-d",  # jaws 3-d
            "k-19",  # K-19: The Widowmaker (2002)
            "g-force",
            "two-lane",  # two-Lane Blacktop (1971)
            "he-man",
            "she-ra",
            "sac_2045",  # ghost in the shelll
        ]

        for word in word_list:
            if word in lista:
                return word

    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    #
    #
    def hashtag(self, stringa):
        """
        :param stringa: Elenco TAG descrittivi del video presenti in stringa
         rimossi durante la ricerca ma reintegrati alla fine
        :return: bool
        """
        lista = [
            "#animazione",
            "#anime",
            "#avventura",
            "#azione",
            "#backstage",
            "#cartone",
            "#cartoni",
            "#classic",
            "#cofanetto",
            "#collection",
            "#collezione",
            "#colonne",
            "#commedia",
            "#corto",
            "#cortometraggio",
            "#cortometraggi",
            "#crew",
            "#crime",
            "#documentario",
            "#dramma",
            "#drama",
            "#drammatico",
            "#famiglia",
            "#fantascienza",
            "#fantastico",
            "#fantasy",
            "#film",
            "#mistero",
            "#musicale",
            "#parodia",
            "#poliziesco",
            "#reality",
            "#realitytv",
            "#religioso",
            "#satira",
            "#sci-fi",
            "#sentimentale",
            "#storia",
            "#guerra",
            "#thriller",
            "#umorismonero",
            "#western",
        ]
        # se esiste ritorna True
        return stringa.lower() in lista

    # ....................................................................................................................
    # identifica tag descrittivi
    #

    def identify_tag(self, string):
        word_list = string.lower().strip().split(' ')
        tag_list = []
        locandina = ""
        for word in word_list:
            if self.tag(word):
                tag_list.append(word)
            if not self.tag(word):
                locandina += word + ' '
        locandina = locandina.strip()
        return locandina, tag_list

    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Elenco TAG descrittivi del video presenti in stringa rimossi durante la ricerca ma reintegrati alla fine
    #
    def tag(self, stringa):
        lista = [
            "1080p",
            "720p",
            "aac",
            "ac3",
            "bdrip",
            "brrip",
            "blmux",
            "brmux",
            "cam",
            "completa",
            "dd",
            "deluxe",
            "divx",
            "dl",
            "dlmux",
            "dsp",
            "dsp2",
            "dttrip",
            "dts",
            "dv",
            "dvb",
            "dvbrip",
            "dvd",
            "dvd5",
            "dvd9",
            "dvdmux",
            "dvdrip",
            "dvdscr",
            "eng",
            "ep.",
            "extra",
            "fullhd",
            "hardsub",
            "hd",
            "ita",
            "italian",
            "jap",
            "ld",
            "md",
            "minidv",
            "movie",
            "mp3",
            "multi",
            "mux",
            "oav",
            "pdtv",
            "pilot",
            "r3",
            "r4",
            "r5",
            "r6",
            "ripsat",
            "rip",
            "dvb-s",
            "tc",
            "ts",
            "satrip",
            "sbs",
            "screener",
            "serie",
            "webserie",
            "sigle",
            "sitcom",
            "softsub",
            "sonore",
            "sub",
            "sub-ita",
            "tvrip",
            "vhsrip",
            "vhsscr",
            "vu",
            "webrip",
            "web",
            "wp",
            "x264",
            "x265",
            "xvid",
        ]
        # se esiste ritorna True
        return stringa.lower() in lista
