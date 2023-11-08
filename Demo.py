#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-

import asyncio

from stv import Database, MyChannel


async def main():
    # Connessione a Telegram
    stv = MyChannel()
    await stv.connect()

    # Connessione al database
    database = Database("stv.db")
    await database.connect()

    # Crea tabella se non presente
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
