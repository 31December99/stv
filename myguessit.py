#!/usr/bin/env python3.9
# -*- coding: utf-8 -*-
import guessit

from titoli import Saniteze


class MyGuessit:

    def __init__(self, title: str):
        saniteze = Saniteze()
        self.sanitized = saniteze.extract(title)
        new_title = (f"{self.sanitized.get('title')} {self.sanitized.get('year')}"
                     f" {self.sanitized.get('tags')} {self.sanitized.get('keywords')}")
        self.guess = guessit.guessit(new_title)  # per il momento sospeso

    @staticmethod
    def new_title(self):
        return self.guess

    @property
    def noguess(self):
        return self.sanitized.get('title')

    @property
    def title(self):
        return ''.join(map(str, self.guess.get('title', '')))

    @property
    def series(self):
        return ''.join(map(str, self.guess.get('series', '')))

    @property
    def alternative_title(self):
        return ''.join(map(str, self.guess.get('alternative_title', '')))

    @property
    def year(self):
        return ''.join(map(str, str(self.guess.get('year', ''))))

    @property
    def release_group(self):
        return self.guess.get('release_group', '')
