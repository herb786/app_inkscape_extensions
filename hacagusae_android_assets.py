#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2020 Herbert Caller, kaioa.com

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
  "MDPI":0.25,
  "HDPI":0.375,
  "XHDPI":0.5,
  "XXHDPI":0.75,
  "XXXHDPI":1
}
DPI_FOLDERS={
  "MDPI":"drawable-mdpi",
  "HDPI":"drawable-hdpi",
  "XHDPI":"drawable-xhdpi",
  "XXHDPI":"drawable-xxhdpi",
  "XXXHDPI":"drawable-xxxhdpi"
}


class AndroidAssetExport(inkex.EffectExtension):

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
        self.DIRNAME = self.getUserDirectory()
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

    def generateImageWithDPI(self,PNG_SRC,DPI_CODE):
        filepath = os.path.join(self.DIRNAME, "temp", PNG_SRC)
        tempImage = Image.open(filepath)
        self.createDirectory(DPI_FOLDERS[DPI_CODE])
        w, h = tempImage.size
        newHeight = int(DPI_SIZES[DPI_CODE]*h)
        newWidth = int(DPI_SIZES[DPI_CODE]*w)
        newImage = tempImage.resize((newWidth,newHeight), Image.ANTIALIAS)
        filepath = os.path.join(self.DIRNAME, DPI_FOLDERS[DPI_CODE],PNG_SRC)
        newImage.save(filepath)

    def exportImageToPNG(self,assetID,assetLABEL):
        filename = assetLABEL + ".png"
        svg_file = self.options.input_file
        #DOCNAME = self.document.getroot().xpath('@sodipodi:docname', namespaces=inkex.NSS)
        #svg_file = os.path.join(self.DIRNAME, DOCNAME[0])
        if not os.path.exists(os.path.join(self.DIRNAME, "temp")):
            os.mkdir(os.path.join(self.DIRNAME, "temp"))
        filepath = os.path.join(self.DIRNAME, "temp", filename)
        inkscape(self.options.input_file, export_id=assetID, export_filename=filepath)

    def generateBaselinePNG(self,ASSETS):
        for asset in ASSETS:
            self.exportImageToPNG(asset["assetID"],asset["assetLABEL"])

    def generateAssetsWithDPI(self,ASSETS,DPI_CODE):
        for asset in ASSETS:
            filename = asset["assetLABEL"] + ".png"
            self.generateImageWithDPI(filename,DPI_CODE)

    def getAssetsByLayer(self,LAYER):
        assets=[]
        for child in LAYER:
            assetId=child.attrib.get('id')
            if assetId:
                assetLabel=child.attrib.get('{http://www.inkscape.org/namespaces/inkscape}label')
                if assetLabel:
                    assets.append({"assetID":assetId,"assetLABEL":assetLabel})
        return assets

    def getAssetCollection(self,LAYERS):
        assets=[]
        for layer in LAYERS:
            children = list(layer)
            assetGroup = self.getAssetsByLayer(children)
            assets=assets + assetGroup
        return assets

    def getLayers(self):
        path = '//svg:g[@inkscape:groupmode="layer"]'
        layers = self.document.xpath(path,namespaces=inkex.NSS)
        return layers

    def effect(self):
        self.findCurrentWorkingDirectory()
        layers = self.getLayers()
        assets = self.getAssetCollection(layers)
        self.generateBaselinePNG(assets)
        self.generateAssetsWithDPI(assets,self.MDPI)
        self.generateAssetsWithDPI(assets,self.HDPI)
        self.generateAssetsWithDPI(assets,self.XHDPI)
        self.generateAssetsWithDPI(assets,self.XXHDPI)
        self.generateAssetsWithDPI(assets,self.XXXHDPI)

if __name__ == '__main__':
    AndroidAssetExport().run()