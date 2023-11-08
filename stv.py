#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import asyncio
import re

import mytelegram
from mytelegram import MyTelegram
from myguessit import MyGuessit
from database import Database

import logging

# LOG
logging.basicConfig(level=logging.DEBUG)


class MyChannel:
    mime_type_list = [
        "video/x-matroska",  # .mkv .mk3d .mka .mks
        "video/mpeg",  # .mpg, .mpeg, .mp2, .mp3
        "video/x-mpeg",  #
        "video/mp4",  # .mp4, .m4a, .m4p, .m4b, .m4r .m4v
    ]

    def __init__(self):
        """
         Estrae ogni singolo file dividendolo dalla locandine
        """
        self.botstv = None
        self.telegram = MyTelegram()
        self.media = None
        self.media_poster = []
        self.media_file = []

    async def connect(self):
        """
        :return: Telegram login e collegamento al canale
        """
        await self.telegram.login()
        print(f"-> [INVITE LINK] {mytelegram.INVITE_LINK}")
        print(f"-> [CHANNEL ID]  {self.telegram.channel.channel_id}")
        print(f"-> [CONNECT OBJ] {self.telegram.takeout}")
        self.botstv = await self.telegram.takeout.get_input_entity('https://t.me/SerietvFilms_Bot')
        print(f"-> [CONNESSO... Italia Serie bot {self.botstv}\n")

    async def request(self, str_url, pause=1):
        """
        :param str_url: Oltre un certo numero di episodi ricevuto in "un solo invio"
                        il bot si fa una pausa , occorre impostare un loop controllo ogni secondo
        :param pause:
        :return:
        """

        # Inizio dialogo con Bot
        # Svuota la chat con il bot da eventuali precedenti messaggi
        await self.telegram.takeout.delete_dialog(self.botstv)
        await asyncio.sleep(1)
        async for chat_list in self.telegram.takeout.iter_messages(self.botstv):
            # Se la chat è vuota termino e passo al prossimo step
            if not chat_list:
                break
            await self.telegram.takeout.delete_dialog(self.botstv)
            await asyncio.sleep(1)

        # invio al bot
        print("ATTENDI RISPOSTA DEL BOT !")
        await self.telegram.takeout.send_message(entity='SerietvFilms_Bot', message='/start ' + str_url)

        # Attendo fine trasmissione da bot
        reply_markup = False
        pause_cont = 0
        while reply_markup is False:
            await asyncio.sleep(pause)
            pause_cont = pause_cont + 1
            print('.' * pause_cont)
            async for episode in self.telegram.takeout.iter_messages(self.botstv, reverse=True):
                if episode.reply_markup:
                    reply_markup = True

        # Al termine legge i video
        await self.struttura(0, True)

    async def struttura(self, last_id: int, channel=False) -> list:
        """
        :return: ritorna un elenco di oggetti MyMedia pronti per il download
        per stv non ci sono file media nel canale ma occorre comunicare con il loro bot
        """
        channel = self.telegram.channel.channel_id if not channel else self.botstv
        async for message in self.telegram.takeout.iter_messages(entity=channel, limit=None, reverse=True, wait_time=1,
                                                                 min_id=last_id, max_id=0):
            # Si accerta che sia un messaggio
            if message:
                # Eslcude gli sticker
                if not message.sticker:
                    # Si accerta che esista un documento di media
                    if message.media:
                        if hasattr(message.media, 'document'):
                            if message.media.document.mime_type in self.mime_type_list:
                                # esclude messaggi senza file name("pubblcità")
                                if not message.file.name:
                                    continue
                                # Memorizza per ogni documento media filename e ID del messaggio
                                self.media = mytelegram.MyMedia()
                                self.media.ids = message.id
                                self.media.filename = message.file.name
                                self.media_file.append(self.media)
                                logging.info(self.media.filename)

                        else:
                            # Se media è già stato istanziato abbiamo raggiunto qui la prossima locandina
                            # Se filemedia non è empty lo salva nella lista media_list.
                            # Al termine passa ad un'altra locandina.

                            # Si assicura che sia una foto
                            if hasattr(message.photo, 'id'):
                                logging.info("Ffotrotototo")
                                if self.media:
                                    self.media_poster.append(self.media)
                                # Ottiene il testo della Locandina
                                poster = message.message
                                # Filtra il testo quindi lo passa a guessit
                                self.media = mytelegram.MyMedia()
                                self.media.title = MyGuessit(poster).noguess
                                self.media.posterid = message.id
                                # Ottengo il link per il bot
                                button = re.search("_Bot\\?start=(.+?)\'\\)", str(message.reply_markup))
                                if button:
                                    url = button.group(1)
                                    self.media.bot_url = url
                                    logging.info(f":[BOT_URL] https://t.me/SerietvFilms_Bot?start={self.media.bot_url}")
                                    logging.info(f":[{self.media.posterid}] ---------------------> {self.media.title}")

        media_list = [media for media in self.media_poster]
        return media_list


async def main():
    # Connessione a Telegram
    stv = MyChannel()
    await stv.connect()

    # Connessione al database
    database = Database("stv.db")
    await database.connect()

    # Crea tabealla se non presente
    await database.create_table("stv")
    last_message_id = await database.load_last_id("stv")

    # Scansiona canale
    media_list = await stv.struttura(last_id=last_message_id)

    # Salva il risultato della scansione nel database
    for media in media_list:
        print(media.title, media.posterid, media.ids)
        await database.insert_video("stv", media.title, media.posterid, media.bot_url)
    await database.db.commit()

    ##################
    # Demo ###########
    # Invio Url al Bot per ogni locandina del canale
    media_list = await database.load_table()
    await database.close()

    # RICHIESTE
    for title, str_url in media_list:
        # Messaggio di start
        print(title.upper())
        # Richiede al bot il prossimo video
        await stv.request(str_url=str_url)

        # DOWNLOAD..
        input("Premi un pulsante per far partire il download.. ")
        print(title.upper())
        await stv.telegram.stv_downloader(stv.media_file, stv.botstv)
    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        task_start = loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Fine..")
