export_things.py
=============

Script that simplifies exporting all your stuff out of Thingiverse  
It creates a Git-compatible directory with a list and folders. Each folder contains all the files, images and description for each design.  
Free your things! Au revoir Thingiverse!  

Example of the result: <https://github.com/carlosgs/carlosgs-designs>  


Disclaimer
--------
Not associated with Thingiverse, use at your own risk  

Instructions
--------
* _Optional:_ Create an empty Git repository, clone the repo locally
* Download [the python script](export_things.py) as raw into the created empty directory
* Edit lines 17-19 for user, authorName, and authorDescription
* Install PIP (sudo apt-get install python-pip)
* Install requests (sudo pip install requests)
* Install beautifulsoup (sudo pip install beautifulsoup) not BeautifulSoup4
* Run the script from the same directory (python export_things.py)
* _Optional:_ Commit and push the changes into your Git repository

Credit
--------
* Thanks to everyone who is re-sharing the script
* Thanks to **Derrick Oswald** for writing installation instructions

Author: Carlos Garcia Saura (carlosgs)
--------
<http://carlosgs.es/>  

License
--------
Creative Commons - Attribution - Share Alike license.  


