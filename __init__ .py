# Copyright 2017, Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Now migrated, testes and working in Python3

from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.skills.context import adds_context, removes_context
from mycroft.util import play_mp3


from os.path import dirname, abspath, join
import requests
import os
import sys
import time

from mtranslate import translate
from unidecode import unidecode
import unicodedata


__author__ = 'jcasoft'


class TranslateSkill(MycroftSkill):

    def __init__(self):
        super(TranslateSkill, self).__init__('TranslateSkill')
        self.language = self.lang

    def initialize(self):

        intent = IntentBuilder('HowUseIntent')\
            .require('HowUseKeyword') \
            .require('SkillNameKeyword') \
            .build()
        self.register_intent(intent, self.handle_how_use)

    @intent_handler(IntentBuilder("TranslateIntent").require("TranslateKeyword")
                    .require('LanguageNameKeyword')
                    .require('phrase')
                    .build())
    @adds_context("TranslateContext")
    def handle_translate_intent(self, message):
        word = message.data.get("TranslateKeyword")
        lang = message.data.get("LanguageNameKeyword")
        sentence = message.data.get("phrase")

        """
        try:
            sentence.decode('ascii')
        except BaseException:
            sentence = unicodedata.normalize(
                'NFKD', sentence).encode(
                'ascii', 'ignore')
        """

        translated = translate(sentence, lang)

        """
        sentence = unicodedata.normalize(
            'NFKD', translated).encode(
            'ascii', 'ignore')
        """

        self.say(sentence, lang)

    @intent_handler(IntentBuilder("TranslateToIntent")
                    .require("TranslateKeyword")
                    .require('translate')
                    .require('ToKeyword')
                    .require('LanguageNameKeyword')
                    .build())
    @adds_context("TranslateContext")
    def handle_translate_to_intent(self, message):
        lang = message.data.get("LanguageNameKeyword")
        sentence = message.data.get("translate")
        to = message.data.get("ToKeyword")

        """
        try:
            sentence.decode('ascii')
        except BaseException:
            sentence = unicodedata.normalize(
                'NFKD', sentence).encode(
                'ascii', 'ignore')
        """

        translated = translate(sentence, lang)

        """
        sentence = unicodedata.normalize(
            'NFKD', translated).encode(
            'ascii', 'ignore')
        """

        self.say(sentence, lang)

    @intent_handler(IntentBuilder("RepeatTranslate") .require(
        'RepeatKeyword').require("TranslateContext").build())
    def handle_repeat_translate(self, message):
        self.emitter.emit(Message('recognizer_loop:mute_mic'))
        self.emitter.emit(Message('recognizer_loop:audio_output_start'))
        time.sleep(1)

        p = play_mp3("/tmp/translated.mp3")
        p.communicate()

        self.emitter.emit(Message('recognizer_loop:unmute_mic'))
        self.emitter.emit(Message('recognizer_loop:audio_output_end'))

    @intent_handler(IntentBuilder("OthersLanguagesIntent")
                    .require("SpeakKeyword")
                    .require("LanguageKeyword")
                    .build())
    @adds_context("OthersLanguagesContext")
    def handle_others_languages(self, message):
        data = None
        self.speak_dialog("yes.ask", data, expect_response=True)

    @intent_handler(IntentBuilder("OtherLanguageTranslateIntent").require(
        "OthersLanguagesContext").build())
    def handle_other_language_translate(self, message):
        resp = message.data.get("utterance")

        langs = [
            "en",
            "es",
            "it",
            "fr",
            "pt",
            "nl",
            "de",
            "pl",
            "sv",
            "no",
            "hu",
            "da",
            "ca",
            "ro",
            "zh-CN",
            "ja",
            "sk"]
        language = self.language

        self.emitter.emit(Message('recognizer_loop:mute_mic'))
        i = 0
        for i in range(0, len(langs)):
            lang = langs[i]
            if lang == language:
                print("*****Skip language.....")
            else:
                translated = str(translate(resp, lang))

                """
                translated = unicodedata.normalize(
                    'NFKD', translated).encode(
                    'ascii', 'ignore')
                """

                self.say(translated, lang)

            i = i + 1

        self.emitter.emit(Message('recognizer_loop:unmute_mic'))
        self.emitter.emit(Message('recognizer_loop:audio_output_end'))

    def handle_how_use(self, message):
        self.speak_dialog("how.use")

    def say(self, sentence, lang):
        self.emitter.emit(Message('recognizer_loop:mute_mic'))

        get_sentence = 'wget -q -U Mozilla -O /tmp/translated.mp3 "https://translate.google.com/translate_tts?tl=' + \
            str(lang) + '&q=' + str(sentence) + '&client=tw-ob' + '"'
        os.system(get_sentence)

        p = play_mp3("/tmp/translated.mp3")
        p.communicate()

        time.sleep(0.2)
        self.emitter.emit(Message('recognizer_loop:unmute_mic'))


def create_skill():
    return TranslateSkill()
