#!/usr/bin/env python
# coding: UTF-8

'''
Install or remove MHSM from your system.
'''

import os
import os.path
import shutil
import optparse

# PATHS
EXEC_PATH = "/usr/bin"
PIX_PATH = "/usr/share/pixmaps"
DESK_PATH = "/usr/share/applications"
PATH = "/usr/share/mhsm"

# FILENAMES
EXEC = "mhsm"
NO_INSTALL = ("INSTALL", "mhsm", "setup.py", "MHSM.desktop", "TODO")
GUI_PIXMAPS_PATH = "gui/pixmaps"
PIXMAP = "monitor_mhsm.svg"
DESK = "MHSM.desktop"

def main():
    # Parse the arguments
    parser = optparse.OptionParser()
    parser.add_option("--install", action="store_true", dest="install", default="True", help="Install MHSM on your system")
    parser.add_option("--remove", action="store_false", dest="install", help="Remove MSHM from your system")
    options, arg = parser.parse_args()

    # Check if user is root
    if os.getuid():
        print "\nERROR: You must be root!\n"
        return 1

    # Install MHSM
    # Creates the necesary dirs if don't exist and
    # copy all necesary content on them
    if options.install:
        print "Starting installation..."
        if not os.path.lexists(PATH):
            print "  * Creating folders..."
            os.mkdir(PATH, 0755)
        try:
            print "  * Copying files..."
            print "    * Copying %s to %s" % (EXEC, EXEC_PATH)
            shutil.copy(EXEC, EXEC_PATH)
            os.chmod(os.path.join(EXEC_PATH, EXEC), 0755)
            print "    * Copying %s to %s" % (os.path.join(GUI_PIXMAPS_PATH, PIXMAP), PIX_PATH)
            shutil.copy(os.path.join(GUI_PIXMAPS_PATH, PIXMAP), PIX_PATH)
            os.chmod(os.path.join(PIX_PATH, PIXMAP), 0644)
            print "    * Copying %s to %s" % (DESK, DESK_PATH)
            shutil.copy(DESK, DESK_PATH)
            os.chmod(os.path.join(DESK_PATH, DESK), 0644)

            for arch in os.listdir("."):
                if not os.path.isdir(arch):
                    if arch not in NO_INSTALL:
                        print "    * Copying %s to %s" % (arch, PATH)
                        shutil.copy(arch, PATH)
                        os.chmod(os.path.join(PATH,arch), 0755)
                else:
                    print "    * Copying content of %s to %s" % (arch, os.path.join(PATH,arch))
                    shutil.copytree(arch, os.path.join(PATH,arch))
                    os.chmod(os.path.join(PATH,arch), 0755)
        except IOError, e:
            print "Error during installation.\n  %s\n" % (e[1:])
        else:
            print "\nSuccess!!\nYou can now execute %s on a terminal or go to Applications > System Tools > Thread Monitor MHSM on your Gnome menu." % EXEC
    # Remove MHSM
    else:
        print "\nUninstalling MHSM..."
        try:
            if os.path.lexists(PATH):
                print "  * Removing directory %s..." % PATH
                shutil.rmtree(PATH)
            print "  * Removing %s..." % os.path.join(EXEC_PATH, EXEC)
            os.remove(os.path.join(EXEC_PATH, EXEC))
            print "  * Removing %s..." % os.path.join(PIX_PATH, PIXMAP)
            os.remove(os.path.join(PIX_PATH, PIXMAP))
            print "  * Removing %s..." % os.path.join(DESK_PATH, DESK)
            os.remove(os.path.join(DESK_PATH, DESK))
        except OSError, e:
            print "Error during uninstallation.\n  %s" % (e[1:])
        else:
            print "\nUninstall finished!!\n"


if __name__=="__main__":
    main()
