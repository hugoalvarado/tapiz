import os
import sys
import random
import subprocess
import pickle

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


FONT = '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
PICKLE_FILE = 'data.pickle'
QUOTES_FILE = 'quotes.txt'
SOURCE_INDICATOR = '~'


if os.path.isfile(QUOTES_FILE):
    with open(QUOTES_FILE, 'r') as f:
        quotes = f.readlines()
else:
    print('Quotes file missing')
    exit(0)



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


font = ImageFont.truetype(FONT,60)



if os.path.isfile(PICKLE_FILE):
    with open('data.pickle', 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        data = pickle.load(f)
else:
    data = {
        'source_wallpaper': '', #the full path to the original, non edited wallpaper
        'modified_wallpaper': '' # the new wallpaper with the quote
    }






#gsettings get org.gnome.sh.background picture-uri
#gsettings get org.mate.background picture-filename

desktop_session = get_desktop_environment()

if 'mate' == desktop_session:
    args = ["gsettings", "get", "org.mate.background", "picture-filename"]
    system_wallpaper = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0][1:-2].strip().decode("utf-8")
    wallpaper_path = '/'.join(system_wallpaper.split('/')[0:-1])
    wallpaper_file = system_wallpaper.split('/')[-1]
else:
    print('Unsupported system.')
    exit(1)




if data['modified_wallpaper'] != system_wallpaper:
    data['modified_wallpaper'] = os.path.join(wallpaper_path,str(random.random())[2:10] + wallpaper_file)
    data['source_wallpaper'] = system_wallpaper





#Read image
image = Image.open(data['source_wallpaper']) #Image.open(os.path.join( IMAGE_PATH, IMAGE ))
width, height = image.size


quote = random.choice(quotes)

if SOURCE_INDICATOR in quote:
    quote, by = quote.split(SOURCE_INDICATOR)
else:
    by = 'Anonymous'

by = SOURCE_INDICATOR+by

quote = quote.split()

words_per_line = 3 if len(quote) < 15 else 5

quote_parts = [' '.join(quote[i:i+words_per_line]) for i in range(0, len(quote), words_per_line)]
quote_parts.append(by)

quote_lines = '\n'.join(quote_parts)

draw = ImageDraw.Draw(image)

draw.multiline_text((width/5, height/5), quote_lines, (255,255,255),font=font)

draw = ImageDraw.Draw(image)

image.show()

image.save(data['modified_wallpaper'])

args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % data['modified_wallpaper']]
subprocess.Popen(args, stdout=subprocess.PIPE)


with open(PICKLE_FILE, 'wb') as f:
    # Pickle the 'data' dictionary using the highest protocol available.
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)




if __name__ == '__main__':
    pass