#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2020 Herbert Caller,  hacagusae.appspot.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

# standard library
import sys
import os
import glob
# local library
import inkex
from inkex.command import inkscape
# third party
try:
    from PIL import Image
except:
    inkex.errormsg('This extension requires Pillow. Please install the latest version from https://pillow.readthedocs.io/en/stable/.')
    sys.exit()

inkex.localization.localize()

DPI_SIZES={
  "MDPI":48,
  "HDPI":72,
  "XHDPI":96,
  "XXHDPI":144,
  "XXXHDPI":192
}
DPI_FOLDERS={
  "MDPI":"mipmap-mdpi",
  "HDPI":"mipmap-hdpi",
  "XHDPI":"mipmap-xhdpi",
  "XXHDPI":"mipmap-xxhdpi",
  "XXXHDPI":"mipmap-xxxhdpi"
}


class AndroidIconExport(inkex.EffectExtension):

    MDPI="MDPI"
    HDPI="HDPI"
    XHDPI="XHDPI"
    XXHDPI="XXHDPI"
    XXXHDPI="XXXHDPI"

    def __init__(self):
        inkex.Effect.__init__(self)
        self.visibleLayers = True
        self.DIRNAME = self.getUserDirectory()
        #self.arg_parser.add_argument("--directory", action="store", dest="directory",default=self.DIRNAME)

    def findCurrentWorkingDirectory(self):
        home = self.getUserDirectory()
        #inkex.utils.debug(home)
        DOCNAME = self.document.getroot().xpath('@sodipodi:docname', namespaces=inkex.NSS)
        #inkex.utils.debug(DOCNAME)
        files = list(filter(os.path.isfile, glob.glob(home + './**/%s' % DOCNAME[0], recursive=True)))
        #inkex.utils.debug(files)
        if files:
            files.sort(key=lambda x: os.path.getmtime(x))
            head, tail = os.path.split(files[-1])
            self.DIRNAME = head

    def getUserDirectory(self):
        if sys.platform.startswith('win'):
            return os.environ['USERPROFILE']
        else:
            return os.environ['HOME']

    def createDirectory(self,DPI_FOLDER):
        dirname = os.path.join(self.DIRNAME, DPI_FOLDER)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

    def generateIconWithDPI(self,DPI_CODE):
        filepath = os.path.join(self.DIRNAME, "temp", 'ic_launcher.png')
        tempImage = Image.open(filepath)
        self.createDirectory(DPI_FOLDERS[DPI_CODE])
        newImage = tempImage.resize((DPI_SIZES[DPI_CODE],DPI_SIZES[DPI_CODE]), Image.ANTIALIAS)
        filepath = os.path.join(self.DIRNAME, DPI_FOLDERS[DPI_CODE],'ic_launcher.png')
        newImage.save(filepath)

    def exportImageToPNG(self,iconID):
        if not os.path.exists(os.path.join(self.DIRNAME, "temp")):
            os.mkdir(os.path.join(self.DIRNAME, "temp"))
        filepath = os.path.join(self.DIRNAME, "temp", 'ic_launcher.png')
        inkscape(self.options.input_file, export_id=iconID, export_filename=filepath)         

    def getCurrentIcon(self):
        group = self.svg.selected
        #inkex.utils.debug(group)
        return group.popitem(last=False)[0]

    def effect(self):
        self.findCurrentWorkingDirectory()
        inkex.utils.debug("Find id of selected group...")
        iconID = self.getCurrentIcon()
        inkex.utils.debug("Export icon in PNG format and save in temp folder...")
        self.exportImageToPNG(iconID)
        inkex.utils.debug("Create mdpi icon...")
        self.generateIconWithDPI(self.MDPI)
        inkex.utils.debug("Create hdpi icon...")
        self.generateIconWithDPI(self.HDPI)
        inkex.utils.debug("Create xhdpi icon...")
        self.generateIconWithDPI(self.XHDPI)
        inkex.utils.debug("Create xxhdpi icon...")
        self.generateIconWithDPI(self.XXHDPI)
        inkex.utils.debug("Create xxxhdpi icon...")
        self.generateIconWithDPI(self.XXXHDPI)

if __name__ == '__main__':
    AndroidIconExport().run()