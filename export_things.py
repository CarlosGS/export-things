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


# EDIT THIS!
user = "carlosgs" # User from Thingiverse (as in the profile URL)
authorName = "Carlos Garcia Saura (carlosgs)" # Any string is OK
authorDescription = "<http://carlosgs.es/>"

readmeHeader = "**Please note: This list of things was [automatically generated](https://github.com/carlosgs/export-things). Make sure to check the individual licenses and authorships.**  \n"

thingReadmeHeader = "**Please note: This thing is part of a list that was [automatically generated](https://github.com/carlosgs/export-things) and may have been updated since then. Make sure to check for the current license and authorship.**  \n"

listPageTitle = "Things designed by " + authorName
#listPageTitle = "Things liked by " + authorName

urlPathToDownload = "/designs/page:" # "/likes/page:" # Set to the url you want to download from (either your posted designs or your liked designs)

authorMark = True # If set true, will write your author name and description at the bottom of all pages

downloadFiles = True # If set to false, will link to original files instead of downloading them
redownloadExistingFiles = False # This saves time when re-running the script in long lists (but be careful, it only checks if file already exists -not that it is good-)

redownloadExistingThings = True # If set False, it won't re-download anything fron things that already have a folder (be careful, it ONLY checks if the THING FOLDER already exists -not that it is good-). Useful to save time when resuming long lists

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
	r = requests.get(page, allow_redirects=redir)
	if r.status_code != 200:
		print(r.status_code)
		return -1
	if not filename:
		# Remove all non ascii characters
		text = (c for c in r.text if 0 < ord(c) < 127)
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

thingList = {}

print("Username: " + user)

with open("README.md", 'w') as fdr: # Generate the global README file with the list of the things
	fdr.write(listPageTitle)
	fdr.write("\n===============\n\n")
	
	fdr.write(readmeHeader)
	
	thingCount = 0
	pgNum = 1
	while 1: # Iterate over all the pages of things
		print("\nPage number: " + str(pgNum))
#		if pgNum < 17:
#			pgNum += 1
#			continue
		res = httpGet(url + "/" + user + urlPathToDownload + str(pgNum), redir=False)#, filename="test" + str(pgNum) + ".html")
		if res == -1: break
		res_xml = BeautifulSoup(res, convertEntities=BeautifulSoup.HTML_ENTITIES)
		things = res_xml.findAll("div", { "class":"thing thing-interaction-parent" })
		for thing in things: # Iterate over each thing
			#title = str(thing["title"])
			title = str(thing.findAll("span", { "class":"thing-name" })[0].text.encode('utf-8', 'ignore'))
			title = re.sub("\[[^\]]*\]","", title) # Optional: Remove text within brackets from the title
			title = title.strip()
			id = str(thing["data-thing-id"]) # Get title and id of the current thing
			
			print("\nProcessing thing: " + id + " : " + title)
#			if id != "59196": continue
			
			folder = "-".join(re.findall("[a-zA-Z0-9]+", title)) # Create a clean title for our folder
			print(folder)
			previewImgUrl = str(thing.findAll("img", { "class":"thing-img" })[0]["src"]) # Get the link for the preview image
			previewImgName = previewImgUrl.split('/')[-1]
			previewImgFile = folder + "/img/" + previewImgName
			
			if redownloadExistingThings or not os.path.exists(folder):
				makeDirs(folder) # Create the required directories
				makeDirs(folder + "/img")
			
				print("Downloading preview image ( " + previewImgName + " )")
				httpGet(previewImgUrl, previewImgFile) # Download the preview image
			
				print("Loading thing data")
			
				res = httpGet(url + "/thing:" + id, redir=False) # Load the page of the thing
				if res == -1:
					print("Error while downloading " + id + " : " + title)
					exit()
				res_xml = BeautifulSoup(res, convertEntities=BeautifulSoup.HTML_ENTITIES)
			
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
					if authorMark:
						fd.write("\n\nBy: " + authorName + "\n--------\n")
						fd.write(authorDescription)
					fd.close()
			
			
			thingList[title] = {}
			thingList[title]["title"] = title
			thingList[title]["folder"] = folder
			thingList[title]["img"] = urllib.quote(previewImgFile)
			#thingList[title]["description"] = description
			
			thingCount += 1
			
			thing = thingList[title]
			# Add to the global thing list
			fdr.write(str(thingCount) + '. [' + thing["title"] + '](' + thing["folder"] + '/)\n')
			fdr.write("--------\n")
			fdr.write('[![Image](' + thing["img"] + ')](' + thing["folder"] + '/)  \n\n')
			fdr.flush()
			
			#if thingCount > 2: break
		#if thingCount > 2: break
		pgNum += 1
	
	fdr.write("  \n\nLicense\n--------\n")
#	fdr.write("CC-BY-SA (unless other specified)\n\n")
	fdr.write("Please check the individual pages for each design\n\n")
	if authorMark:
		fdr.write("\n\nBy: " + authorName + "\n--------\n")
		fdr.write(authorDescription)
	fdr.close()

print("\n\nIt's done!! Keep knowledge free!! Au revoir Thingiverse!!\n")

