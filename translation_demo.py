#translation demo script using MBart 


import argostranslate.package
import argostranslate.translate
from bidi.algorithm import get_display # for correct display of Hebrew

from_code = "he"
to_code = "en"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("אני רוצה לאכול פאי תפוחים ולשתות תה חם", from_code, to_code)
# print(get_display(translatedText))
print(translatedText)
