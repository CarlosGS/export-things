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
import urllib
import time
import sys

thingID = sys.argv[1]

thingReadmeHeader = "**Please note: This page was [automatically generated](https://github.com/carlosgs/export-things) and may have been updated since then. Make sure to check for the current license and authorship.**  \n"

downloadFiles = True # If set to false, will link to original files instead of downloading them
redownloadExistingFiles = False # This saves time when re-running the script in long lists (but be careful, it only checks if file already exists -not that it is good-)

url = "https://www.thingiverse.com"

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
	try:
	    r = requests.get(page, allow_redirects=redir)
	except:
	    time.sleep(10)
	    return httpGet(page, filename, redir)
	if r.status_code != 200:
		print(r.status_code)
		return -1
	if not filename:
		# Remove all non ascii characters
		text = (c for c in r.content if 0 < ord(c) < 127) # changed from r.text to r.content
		text = ''.join(text)
		return text.encode('ascii', 'ignore')
	else:
		with open(filename, 'wb') as fd:
			for chunk in r.iter_content(512):
				fd.write(chunk)
			fd.close()
		return r.history

# Helper function to remove all html tags and format to a BeautifulSoup object
# This is a patch, since the getText function gives problems with non-ascii characters
def myGetText(BScontent):
	try:
		text = str(BScontent.getText(separator=u' ')) # Won't work with non-ascii characters
	except:
		text = re.sub('<[^<]+?>', '', str(BScontent)) # If there are non-ascii characters, we strip tags manually with a regular expression
	return text.strip() # Remove leading and trailing spaces


print("\nProcessing thing: " + thingID)
print("Loading thing data")

res = httpGet(url + "/thing:" + thingID, redir=False) # Load the page of the thing
if res == -1:
	print("Error while downloading " + thingID + " : " + title)
	exit()
res_xml = BeautifulSoup(res, convertEntities=BeautifulSoup.HTML_ENTITIES)


try:
	header_data = res_xml.findAll("div", { "class":"thing-header-data" })[0]
	title = str(header_data.h1.text.encode('utf-8', 'ignore'))
except:
	title = str(res_xml.findAll("title")[0].text.encode('utf-8', 'ignore'))

title = re.sub("\[[^\]]*\]","", title) # Optional: Remove text within brackets from the title
title = title.strip()

folder = "-".join(re.findall("[a-zA-Z0-9]+", title)) # Create a clean title for our folder
print(folder)

makeDirs(folder) # Create the required directories
makeDirs(folder + "/img")


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
	license = myGetText(license[0]) # Get the license
else:
	license = "CC-BY-SA (default, check actual license)"



tags = res_xml.findAll("div", { "class":"thing-info-content thing-detail-tags-container" })
if tags:
	tags = myGetText(tags[0]) # Get the tags
else:
	tags = "None"
if len(tags) < 2: tags = "None"



header = res_xml.findAll("div", { "class":"thing-header-data" })
if header:
	header = myGetText(header[0]) # Get the header (title + date published)
else:
	header = "None"
if len(header) < 2: header = "None"


files = {}
for file in res_xml.findAll("div", { "class":"thing-file" }): # Parse the files and download them
	fileUrl = url + str(file.a["href"])
	fileName = str(file.a["data-file-name"])
	filePath = folder + "/" + fileName
	if downloadFiles:
		print("Downloading file ( " + fileName + " )")
		httpGet(fileUrl, filePath)
	else:
		print("Skipping download for file: " + fileName + " ( " + fileUrl + " )")

	filePreviewUrl = str(file.img["src"])
	filePreviewPath = filePreviewUrl.split('/')[-1]
	filePreview = folder + "/img/" + filePreviewPath
	print("-> Downloading preview image ( " + filePreviewPath + " )")
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
	print("Downloading image ( " + imgName + " )")
	httpGet(imgUrl, imgFile)
	images.append(imgName)


# Write in the page for the thing
with open(folder + "/README.md", 'w') as fd: # Generate the README file for the thing
	fd.write(title)
	fd.write("\n===============\n")
	fd.write(thingReadmeHeader + "\n")
	fd.write(header)
	if len(images) > 0:
		fd.write('\n\n![Image](img/' + urllib.quote(images[0]) + ')\n\n')
	fd.write("Description\n--------\n")
	fd.write(description)
	fd.write("\n\nInstructions\n--------\n")
	fd.write(instructions)

	fd.write("\n\nFiles\n--------\n")
	for path in files.keys():
		file = files[path]
		fileurl = file["url"]
		if downloadFiles:
			fileurl = file["name"]
		fd.write('[![Image](img/' + urllib.quote(file["preview"]) + ')](' + file["name"] + ')\n')
		fd.write(' [ ' + file["name"] + '](' + fileurl + ')  \n\n')

	if len(images) > 1:
		fd.write("\n\nPictures\n--------\n")
		for image in images[1:]:
			fd.write('![Image](img/' + urllib.quote(image) + ')\n')

	fd.write("\n\nTags\n--------\n")
	fd.write(tags + "  \n\n")

	fd.write("  \n\nLicense\n--------\n")
	fd.write(license + "  \n\n")

print("\n\nIt's done!! Keep knowledge free!! Au revoir Thingiverse!!\n")

