Repo for conspicuous consumption research with Max Mueller.

# Get Started 
Install all dependencies and required packages by running in your command line (terminal): `pip3 install -r requirements.txt`. If you are on mac or linux, pip and python should be automatically installed. If not, you must first install python3 and pip, Python's package manager.

Get all post shortcodes from an instagram page.
1. This script is on Jupyter Notebook, and requires its installation. You can read more about [installing Jupyter Notebook here](https://jupyter.readthedocs.io/en/latest/install.html).
2. Once Jupyter notebook is installed, activate jupyter notebook environment with the command `jupyter notebook` in your command line (it's also advised to do this within a virutal environment).
3. Open the `Selenium Notebook` file, which can be found in the `Selenium` directory.
4. Replace the URL variable with the desired instagram profile page.
5. From the top, execute each cell in order. A new headless browser should open up and run in the background; ignore it and let the program run. The program will finish executing when you no longer see the hourglass icon in your Jupyter Notebook tab. 
6. Before executing the last cell, change the 2nd line of the last cell to your desired file name. I.e. change the `open("hakkasanLV.txt"` to `open("<YOUR FILE NAME>.txt"`. This will create a file in the `Selenium` folder with your desired file name and a list of all the shortcodes inside, which you can then copy paste into the post scraper.

Scrape posts given shortcode.
1. Open `scraper_winputs.py`: this is the post scraper program.
2. For each club you want to scrape, create a variable that points to a list of shortcode strings you want to scrape (you can just copy paste the output from the shortcode scraper above).
3. Once all your club shortcode lists are defined as variables, define a dictionary with name `clubs`. The dictionary should map a string (of your choosing, this will be what the club's associated output files will begin with) to a list of shortcodes, one key-value pair for each club. It currently looks something like this: `clubs = {"boulevardLA": shortcodes_boulevard, "CleHouston": shortcodes_cle, "OhmLA": shortcodes_ohm}`, where `shortcodes_CLUBNAME` is a list of shortcode strings.
4. Change the output_dir string on line 190 to name the folder for which all results will be outputted to.
5. You can now run the script. Open terminal and navigate to the directory in which the repo is located, and run `python3 scraper_winputs.py`. This process may take a while, depending on the number of shortcodes that are being scraped.

If you have any questions, feel free to email me at alanliang@berkeley.edu.

