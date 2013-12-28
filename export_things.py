#!/usr/bin/python

# Thingiverse* exporter
# by Carlos Garcia Saura (http://carlosgs.es)
# CC-BY-SA license (http://creativecommons.org/licenses/by-sa/3.0/)
# https://github.com/carlosgs/export-things
# *Unofficial program, not associated with Thingiverse
# Use at your own risk!

# Modules
import requests
from BeautifulSoup import BeautifulSoup
import os
import re


# EDIT THIS!
user = "carlosgs" # User from Thingiverse (as in the profile URL)
authorName = "Carlos Garcia Saura (carlosgs)" # Any string is OK
authorDescription = "<http://carlosgs.es/>"
readmeHeader = "**Please note: This list has been automatically generated. Some of the designs have been updated since then, and already have their own GitHub page.**  \n"



redownloadExistingFiles = False # This saves time when re-running the script

url = "https://www.thingiverse.com/"

# Helper function to create directories
def makeDirs(path):
    try:
        os.makedirs(path)
    except:
        return -1
    return 0

# Helper function to perform the required HTTP requests
def httpGet(page, filename=False, redir=True):
    if filename and not redownloadExistingFiles and os.path.exists(filename):
        return [] # Simulate download OK for existing file
    r = requests.get(page, allow_redirects=redir)
    if r.status_code != 200:
        print(r.status_code)
        return -1
    if not filename:
        return r.text
    else:
        with open(filename, 'wb') as fd:
            for chunk in r.iter_content(512):
                fd.write(chunk)
            fd.close()
        return r.history



thingList = {}

print("Usuario: " + user)

thingCount = 0
pgNum = 1
while 1: # Iterate over all the pages of things
    print("\nPagina: " + str(pgNum))
    res = httpGet(url + user + "/designs/page:" + str(pgNum), redir=False)#, filename="test" + str(pgNum) + ".html")
    if res == -1: break
    res_xml = BeautifulSoup(res)
    things = res_xml.findAll("div", { "class":"thing thing-interaction-parent" })
    for thing in things: # Iterate over each thing
        title = str(thing["title"])
        title = re.sub("\[[^\]]*\]","", title) # Optional: Remove text within brackets from the title
        title = title.strip()
        id = str(thing["data-thing-id"]) # Get title and id of the current thing
        
        print("\nProcesando " + id + " : " + title)
        
        #folder = title.replace(' ', '-').replace('(', '').replace(')', '').replace('*', '')
        folder = "-".join(re.findall("[a-zA-Z0-9]+", title)) # Create a clean title for our folder
        previewImgUrl = str(thing.findAll("img", { "class":"thing-img" })[0]["src"]) # Get the link for the preview image
        previewImgName = previewImgUrl.split('/')[-1]
        previewImgFile = folder + "/img/" + previewImgName
        
        makeDirs(folder) # Create the required directories
        makeDirs(folder + "/img")
        
        print("Descargando imagen de vista previa ( " + previewImgName + " )")
        httpGet(previewImgUrl, previewImgFile) # Download the preview image
        
        print("Cargando datos")
        
        res = httpGet(url + "/thing:" + id, redir=False) # Load the page of the thing
        if res == -1:
            print("Error al descargar " + id + " : " + title)
            exit()
        res_xml = BeautifulSoup(res)
        
        description = res_xml.findAll("div", { "id":"description" })
        if description:
            description = "".join(str(item) for item in description[0].contents) # Get the description
            description = description.strip()
        else:
            description = "None"
        
        instructions = res_xml.findAll("div", { "id":"instructions" })
        if instructions:
            instructions = "".join(str(item) for item in instructions[0].contents) # Get the instructions
            instructions = instructions.strip()
        else:
            instructions = "None"
        
        
        license = res_xml.findAll("div", { "class":"license-text" })
        if license:
            license = str(license[0].getText(separator=u' ')) # Get the license
            license = license.strip()
        else:
            license = "CC-BY-SA (default, check actual license)"
        
        
        
        tags = res_xml.findAll("div", { "class":"thing-info-content thing-detail-tags-container" })
        if tags:
            tags = str(tags[0].getText(separator=u' ')) # Get the tags
            tags = tags.strip()
        else:
            tags = "None"
        if len(tags) < 2: tags = "None"
        
        
        
        header = res_xml.findAll("div", { "class":"thing-header-data" })
        if header:
            header = str(header[0].getText(separator=u' ')) # Get the header (title + date published)
            header = header.strip()
        else:
            header = "None"
        if len(header) < 2: header = "None"
        
        
        
        files = {}
        for file in res_xml.findAll("div", { "class":"thing-file" }): # Parse the files and download them
            fileUrl = url + str(file.a["href"])
            fileName = str(file.a["title"])
            filePath = folder + "/" + fileName
            print("Descargando archivo ( " + fileName + " )")
            httpGet(fileUrl, filePath)
            
            filePreviewUrl = str(file.img["src"])
            filePreviewPath = filePreviewUrl.split('/')[-1]
            filePreview = folder + "/img/" + filePreviewPath
            print("Descargando preview ( " + filePreviewPath + " )")
            httpGet(filePreviewUrl, filePreview)
            
            files[filePath] = {}
            files[filePath]["url"] = fileUrl
            files[filePath]["name"] = fileName
            files[filePath]["preview"] = filePreviewPath
        
        gallery = res_xml.findAll("div", { "class":"thing-page-slider main-slider" })[0]
        images = []
        for image in gallery.findAll("div", { "class":"thing-page-image featured" }): # Parse the images and download them
            imgUrl = str(image["data-large-url"])
            imgName = imgUrl.split('/')[-1]
            imgFile = folder + "/img/" + imgName
            print("Descargando imagen ( " + imgName + " )")
            httpGet(imgUrl, imgFile)
            images.append(imgName)
        
        
        
        with open(folder + "/README.md", 'w') as fd: # Generate the README file for the thing
            fd.write(title)
            fd.write("\n===============\n")
            fd.write(readmeHeader + "\n")
            fd.write(header)
            fd.write('\n\n![Image](img/' + images[0] + ' "Title")\n\n')
            fd.write("Description\n--------\n")
            fd.write(description)
            fd.write("\n\nInstructions\n--------\n")
            fd.write(instructions)
            
            fd.write("\n\nFiles\n--------\n")
            for path in files.keys():
                file = files[path]
                fd.write('[![Image](img/' + file["preview"] + ')](' + file["name"] + ')\n')
                fd.write(' [ ' + file["name"] + '](' + file["name"] + ')  \n\n')
            
            fd.write("\n\nPictures\n--------\n")
            for image in images[1:]:
                fd.write('![Image](img/' + image + ' "Title")\n')
            
            fd.write("\n\nTags\n--------\n")
            fd.write(tags + "  \n\n")
            
            fd.write("\n\nAuthor: " + authorName + "\n--------\n")
            fd.write(authorDescription)
            fd.write("  \n\nLicense\n--------\n")
            fd.write(license + "  \n\n")
            fd.close()
        
        
        
        thingList[title] = {}
        thingList[title]["title"] = title
        thingList[title]["folder"] = folder
        thingList[title]["img"] = previewImgFile
        thingList[title]["description"] = description
        thingCount += 1
        #if thingCount > 2: break
    #if thingCount > 2: break
    pgNum += 1


with open("README.md", 'w') as fd: # Generate the global README file with the list of the things
    fd.write("Things from " + authorName)
    fd.write("\n===============\n\n")
    
    fd.write(readmeHeader)
    
    for title in thingList.keys():
        thing = thingList[title]
        
        fd.write('[' + thing["title"] + '](' + thing["folder"] + '/)\n')
        fd.write("--------\n")
        fd.write('[![Image](' + thing["img"] + ')](' + thing["folder"] + '/)  \n\n')
    
    fd.write("\nAuthor: " + authorName + "\n--------\n")
    fd.write(authorDescription)
    fd.write("  \n\nLicense\n--------\n")
    fd.write("CC-BY-SA (unless other specified)\n\n")
    fd.close()
    fd.close()


