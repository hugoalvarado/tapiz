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
    """
    
    :param file: 
    :return: 
    """
    with open(file, 'r') as f:
        quotes = f.readlines()

    return quotes


def get_desktop_environment():
    """
    
    :return: 
    """
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
            # Special cases
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
    """
    
    :param desktop_session: 
    :return: 
    """
    if 'mate' == desktop_session:
        return True
    else:
        return False


def get_data(file):
    """
    
    :param file: 
    :return: 
    """
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
    """
    
    :param data: 
    :param file: 
    :return: 
    """
    with open(file, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

def choose_quote(quotes):
    """
    
    :param quotes: 
    :return: 
    """
    return random.choice(quotes)

def split_quote(quote):
    """
    
    :param quote: 
    :return: 
    """

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
    """
    
    :return: 
    """
    args = ["gsettings", "get", "org.mate.background", "picture-filename"]
    return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0][1:-2].strip().decode("utf-8")

def set_background_image(wallpaper):
    """
    
    :param wallpaper: 
    :return: 
    """
    args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % wallpaper]
    subprocess.Popen(args, stdout=subprocess.PIPE)

def set_wallpaper(self, file_loc, first_run):
    """
    
    :param self: 
    :param file_loc: 
    :param first_run: 
    :return: 
    """
    # Note: There are two common Linux desktop environments where
    # I have not been able to set the desktop background from
    # command line: KDE, Enlightenment
    desktop_env = self.get_desktop_environment()
    try:
        if desktop_env in ["gnome", "unity", "cinnamon"]:
            uri = "'file://%s'" % file_loc
            try:
                SCHEMA = "org.gnome.desktop.background"
                KEY = "picture-uri"
                gsettings = Gio.Settings.new(SCHEMA)
                gsettings.set_string(KEY, uri)
            except:
                args = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", uri]
                subprocess.Popen(args)
        elif desktop_env == "mate":
            try:  # MATE >= 1.6
                # info from http://wiki.mate-desktop.org/docs:gsettings
                args = ["gsettings", "set", "org.mate.background", "picture-filename", "'%s'" % file_loc]
                subprocess.Popen(args)
            except:  # MATE < 1.6
                # From https://bugs.launchpad.net/variety/+bug/1033918
                args = ["mateconftool-2", "-t", "string", "--set", "/desktop/mate/background/picture_filename",
                        '"%s"' % file_loc]
                subprocess.Popen(args)
        elif desktop_env == "gnome2":  # Not tested
            # From https://bugs.launchpad.net/variety/+bug/1033918
            args = ["gconftool-2", "-t", "string", "--set", "/desktop/gnome/background/picture_filename",
                    '"%s"' % file_loc]
            subprocess.Popen(args)
        ## KDE4 is difficult
        ## see http://blog.zx2c4.com/699 for a solution that might work
        elif desktop_env in ["kde3", "trinity"]:
            # From http://ubuntuforums.org/archive/index.php/t-803417.html
            args = 'dcop kdesktop KBackgroundIface setWallpaper 0 "%s" 6' % file_loc
            subprocess.Popen(args, shell=True)
        elif desktop_env == "xfce4":
            # From http://www.commandlinefu.com/commands/view/2055/change-wallpaper-for-xfce4-4.6.0
            if first_run:
                args0 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-path", "-s",
                         file_loc]
                args1 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-style",
                         "-s", "3"]
                args2 = ["xfconf-query", "-c", "xfce4-desktop", "-p", "/backdrop/screen0/monitor0/image-show", "-s",
                         "true"]
                subprocess.Popen(args0)
                subprocess.Popen(args1)
                subprocess.Popen(args2)
            args = ["xfdesktop", "--reload"]
            subprocess.Popen(args)
        elif desktop_env in ["fluxbox", "jwm", "openbox", "afterstep"]:
            # http://fluxbox-wiki.org/index.php/Howto_set_the_background
            # used fbsetbg on jwm too since I am too lazy to edit the XML configuration
            # now where fbsetbg does the job excellent anyway.
            # and I have not figured out how else it can be set on Openbox and AfterSTep
            # but fbsetbg works excellent here too.
            try:
                args = ["fbsetbg", file_loc]
                subprocess.Popen(args)
            except:
                sys.stderr.write("ERROR: Failed to set wallpaper with fbsetbg!\n")
                sys.stderr.write("Please make sre that You have fbsetbg installed.\n")
        elif desktop_env == "icewm":
            # command found at http://urukrama.wordpress.com/2007/12/05/desktop-backgrounds-in-window-managers/
            args = ["icewmbg", file_loc]
            subprocess.Popen(args)
        elif desktop_env == "blackbox":
            # command found at http://blackboxwm.sourceforge.net/BlackboxDocumentation/BlackboxBackground
            args = ["bsetbg", "-full", file_loc]
            subprocess.Popen(args)
        elif desktop_env == "lxde":
            args = "pcmanfm --set-wallpaper %s --wallpaper-mode=scaled" % file_loc
            subprocess.Popen(args, shell=True)
        elif desktop_env == "windowmaker":
            # From http://www.commandlinefu.com/commands/view/3857/set-wallpaper-on-windowmaker-in-one-line
            args = "wmsetbg -s -u %s" % file_loc
            subprocess.Popen(args, shell=True)
        ## NOT TESTED BELOW - don't want to mess things up ##
        # elif desktop_env=="enlightenment": # I have not been able to make it work on e17. On e16 it would have been something in this direction
        #    args = "enlightenment_remote -desktop-bg-add 0 0 0 0 %s" % file_loc
        #    subprocess.Popen(args,shell=True)
        # elif desktop_env=="windows": #Not tested since I do not run this on Windows
        #    #From http://stackoverflow.com/questions/1977694/change-desktop-background
        #    import ctypes
        #    SPI_SETDESKWALLPAPER = 20
        #    ctypes.windll.user32.SystemParametersInfoA(SPI_SETDESKWALLPAPER, 0, file_loc , 0)
        # elif desktop_env=="mac": #Not tested since I do not have a mac
        #    #From http://stackoverflow.com/questions/431205/how-can-i-programatically-change-the-background-in-mac-os-x
        #    try:
        #        from appscript import app, mactypes
        #        app('Finder').desktop_picture.set(mactypes.File(file_loc))
        #    except ImportError:
        #        #import subprocess
        #        SCRIPT = """/usr/bin/osascript<<END
        #        tell application "Finder" to
        #        set desktop picture to POSIX file "%s"
        #        end tell
        #        END"""
        #        subprocess.Popen(SCRIPT%file_loc, shell=True)
        else:
            if first_run:  # don't spam the user with the same message over and over again
                sys.stderr.write("Warning: Failed to set wallpaper. Your desktop environment is not supported.")
                sys.stderr.write("You can try manually to set Your wallpaper to %s" % file_loc)
            return False
        return True
    except:
        sys.stderr.write("ERROR: Failed to set wallpaper. There might be a bug.\n")
        return False



def get_home_dir(self):
    """
    
    :param self: 
    :return: 
    """
    if sys.platform == "cygwin":
        home_dir = os.getenv('HOME')
    else:
        home_dir = os.getenv('USERPROFILE') or os.getenv('HOME')
    if home_dir is not None:
        return os.path.normpath(home_dir)
    else:
        raise KeyError("Neither USERPROFILE or HOME environment variables set.")

def get_path(system_wallpaper):
    """
    
    :param system_wallpaper: 
    :return: 
    """
    return '/'.join(system_wallpaper.split('/')[0:-1])

def get_file(system_wallpaper):
    """
    
    :param system_wallpaper: 
    :return: 
    """
    return system_wallpaper.split('/')[-1]



def overlay_quote_on_image(quote, image_file, font):
    """Read the image
    
    :param quote: 
    :param image_file: 
    :param font: 
    :return: 
    """
    image = Image.open(image_file)

    width, height = image.size

    quote_lines = split_quote(quote)

    draw = ImageDraw.Draw(image)

    font = ImageFont.truetype(font, 60)

    draw.multiline_text((width/5, height/5), quote_lines, (255, 255, 255), font=font)

    ImageDraw.Draw(image)

    return image


if __name__ == '__main__':
    # gsettings get org.gnome.sh.background picture-uri
    # gsettings get org.mate.background picture-filename

    desktop_session = get_desktop_environment()

    if not supported_de(desktop_session):
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

    # image.show()

    image.save(data['modified_wallpaper'])

    set_background_image(data['modified_wallpaper'])

    save_data(data, PICKLE_FILE)



