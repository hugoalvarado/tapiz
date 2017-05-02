import os
import sys
import random
import subprocess
import pickle

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


FONT = 'fonts/Ubuntu-B.ttf'
PICKLE_FILE = 'data.pickle'
QUOTES_FILE = 'quotes.txt'
SOURCE_INDICATOR = '~'


def load_quotes_from_file(file):
    with open(file, 'r') as f:
        quotes = f.readlines()

    return quotes



def get_desktop_environment():
    # From http://stackoverflow.com/questions/2035657/what-is-my-current-desktop-environment
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=652320
    # and http://ubuntuforums.org/showthread.php?t=1139057
    if sys.platform in ["win32", "cygwin"]:
        return "windows"
    elif sys.platform == "darwin":
        return "mac"
    else:  # Most likely either a POSIX system or something not much common
        desktop_session = os.environ.get("DESKTOP_SESSION")
        if desktop_session is not None:  # easier to match if we doesn't have  to deal with caracter cases
            desktop_session = desktop_session.lower()
            if desktop_session in ["gnome", "unity", "cinnamon", "mate", "xfce4", "lxde", "fluxbox",
                                   "blackbox", "openbox", "icewm", "jwm", "afterstep", "trinity", "kde"]:
                return desktop_session
            ## Special cases ##
            # Canonical sets $DESKTOP_SESSION to Lubuntu rather than LXDE if using LXDE.
            # There is no guarantee that they will not do the same with the other desktop environments.
            elif "xfce" in desktop_session or desktop_session.startswith("xubuntu"):
                return "xfce4"
            elif desktop_session.startswith("ubuntu"):
                return "unity"
            elif desktop_session.startswith("lubuntu"):
                return "lxde"
            elif desktop_session.startswith("kubuntu"):
                return "kde"
            elif desktop_session.startswith("razor"):  # e.g. razorkwin
                return "razor-qt"
            elif desktop_session.startswith("wmaker"):  # e.g. wmaker-common
                return "windowmaker"
        if os.environ.get('KDE_FULL_SESSION') == 'true':
            return "kde"
        elif os.environ.get('GNOME_DESKTOP_SESSION_ID'):
            if not "deprecated" in os.environ.get('GNOME_DESKTOP_SESSION_ID'):
                return "gnome2"

    return "unknown"



def supported_de(desktop_session):
    if 'mate' == desktop_session:
        return True
    else:
        return False


def get_data(file):
    if os.path.isfile(file):
        with open(file, 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            data = pickle.load(f)
    else:
        data = {
            'source_wallpaper': '', #the full path to the original, non edited wallpaper
            'modified_wallpaper': '' # the new wallpaper with the quote
        }
    return data

def save_data(data, file):
    with open(file, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def choose_quote(quotes):
    return random.choice(quotes)

def split_quote(quote):

    if SOURCE_INDICATOR in quote:
        quote, by = quote.split(SOURCE_INDICATOR)
    else:
        by = 'Anonymous'

    by = SOURCE_INDICATOR+by

    quote = quote.split()

    words_per_line = 3 if len(quote) < 15 else 5

    quote_parts = [' '.join(quote[i:i+words_per_line]) for i in range(0, len(quote), words_per_line)]
    quote_parts.append(by)

    return '\n'.join(quote_parts)


def get_system_wallpaper():
    args = ["gsettings", "get", "org.mate.background", "picture-filename"]
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0][1:-2].strip().decode("utf-8")

def set_background_image(wallpaper):
    args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % wallpaper]
    subprocess.Popen(args, stdout=subprocess.PIPE)

def get_path(system_wallpaper):
    return '/'.join(system_wallpaper.split('/')[0:-1])

def get_file(system_wallpaper):
    return system_wallpaper.split('/')[-1]



def overlay_quote_on_image(quote, image_file, font):
    #Read image
    image = Image.open(image_file)

    width, height = image.size

    quote_lines = split_quote(quote)

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font,60)

    draw.multiline_text((width/5, height/5), quote_lines, (255,255,255),font=font)

    ImageDraw.Draw(image)

    return image


if __name__ == '__main__':
    # gsettings get org.gnome.sh.background picture-uri
    # gsettings get org.mate.background picture-filename

    desktop_session = get_desktop_environment()

    if (not supported_de(desktop_session)):
        print('Unsupported system.')
        exit(0)

    if not os.path.isfile(QUOTES_FILE):
        print('Quotes file missing')
        exit(0)

    quote = choose_quote(load_quotes_from_file(QUOTES_FILE))

    system_wallpaper = get_system_wallpaper()

    wallpaper_path = get_path(system_wallpaper)
    wallpaper_file = get_file(system_wallpaper)

    data = get_data(PICKLE_FILE)

    if data['modified_wallpaper'] != system_wallpaper:
        data['modified_wallpaper'] = os.path.join(wallpaper_path, str(random.random())[2:10] + wallpaper_file)
        data['source_wallpaper'] = system_wallpaper


    image = overlay_quote_on_image(quote, data['source_wallpaper'], FONT)

    #image.show()

    image.save(data['modified_wallpaper'])

    set_background_image(data['modified_wallpaper'])

    save_data(data, PICKLE_FILE)



