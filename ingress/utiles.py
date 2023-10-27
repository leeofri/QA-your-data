import argostranslate.package
import argostranslate.translate

class Translate:
    def __init__(self, from_code:str = 'en', to_code:str = 'he'):
        self.from_code = from_code
        self.to_code = to_code

        # Download and install Argos Translate package
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        print(available_packages)
        package_to_install = next(
            filter(
                lambda x: (
                    print(x.from_code,x.to_code),
                    x.from_code in ['en','he'] and x.to_code in ['en','he']
                    ), available_packages)
        )

        print(package_to_install)
        
        argostranslate.package.install_from_path(package_to_install.download())


    def translate_he_to_en(self, text:str) -> str:
        return argostranslate.translate.translate(text,'he', 'en')

    def translate_en_to_he(self, text:str) -> str:
        return argostranslate.translate.translate(text, 'en', 'he')




Translate().translate_en_to_he("I want to eat apple pie and drink hot tea")
