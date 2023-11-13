import string
# from argostranslate import package, translate

class Translate:
    def __init__(self, from_code: str = "en", to_code: str = "he"):
        self.from_code = from_code
        self.to_code = to_code

        # TODO: replace with translate api init
        # installed_languages = translate.get_installed_languages()
        # print(str(installed_languages))
        # self.en_to_he = installed_languages[0].get_translation(installed_languages[1])
        # self.he_to_en = installed_languages[1].get_translation(installed_languages[0])

        # self.he_to_en.translate("מה הולךשדעגגדשחל")
        # self.en_to_he.translate("what are you talking about ?")
        # print(installed_languages)
        # print('self.he_to_en',self.he_to_en)
    
        # print('self.he_to_en',self.en_to_he)

    def translate_he_to_en(self, text: str) -> str:
        return 'stam lol' # TODO : http cal to taranslate self.he_to_en.translate(text)

    def translate_en_to_he(self, text: str) -> str:
        return  'סתם פיללר'# TODO : http cal to taranslate self.en_to_he.translate(text)
