import argostranslate.package
import argostranslate.translate


class Translate:
    def __init__(self, from_code: str = "en", to_code: str = "he"):
        self.from_code = from_code
        self.to_code = to_code

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        print(available_packages)
        package_to_install = next(
            filter(
                lambda x: (x.from_code in ["en", "he"] and x.to_code in ["en", "he"]),
                available_packages,
            )
        )

        argostranslate.package.install_from_path(package_to_install.download())
        installed_languages = argostranslate.translate.get_installed_languages()
        print(installed_languages)
        to_en = list(filter(lambda x: x.code == from_code, installed_languages))[0]
        to_he = list(filter(lambda x: x.code == to_code, installed_languages))[0]
        self.he_to_en = to_he.get_translation(to_en)
        print('self.he_to_en',self.he_to_en)
        
        self.en_to_he = to_en.get_translation(to_he)
        print('self.he_to_en',self.en_to_he)

    def translate_he_to_en(self, text: str) -> str:
        return self.he_to_en(text)

    def translate_en_to_he(self, text: str) -> str:
        return self.en_to_he(text)
