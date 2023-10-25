import argostranslate.package
import argostranslate.translate

class Translate:
    def __init__(self, from_code:str = 'he', to_code:str = 'en'):
        self.from_code = from_code
        self.to_code = to_code

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())


    def translate_he_to_en(self, text:str) -> str:
        return argostranslate.translate.translate(text, self.from_code, self.to_code)

    def translate_en_to_he(self, text:str) -> str:
        return argostranslate.translate.translate(text, "en", "he")




