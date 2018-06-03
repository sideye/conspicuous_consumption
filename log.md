5/28

Overall, I came in expecting quick success in scraping instagram for all sorts of data, but I soon realized that this was much harder than I had imagined. I estimate I put in about 8-10 hours looking into this, and I have to say that the results are not as successful as I would have liked. 

Anyways, here are some of my notes. I can compile this into a google doc or note something for easier collaboration and documentation if you'd like.

I mainly focused on getting post shortcodes this week:
- Instagram official API: didn't work. I think Facebook requires users of its graph API to be developers with apps and privacy policies. 
- This Instagram scraper (https://github.com/rarcega/instagram-scraper) using python: this app seems very promising. I found success with this for the first couple tries, but it stopped working on my end soon after so that I could not implement modifications. The app also has a lot of features including scraping for comments/likes/hashtags. I think we can modify the code pretty easily (from looking at app.py, follow and trace the scrape method) to scrape shortcodes.
- This website (http://www.picluck.net/) that displays all of instagram's content but removes autoscrolling. This seems pretty promising for scraping likes/comments/users etc. However, I have not been able to recover shortcodes of any post from this website, which makes it a little challenging to use. Perhaps there exists a smart work around/clever hack?
- This app (https://www.4kdownload.com/products/product-stogram) that acts as a desktop app and apparently downloads the photos. Could you possibly look into this? Currently I am behind the great firewall and the app does not work with my VPN, so I have not been able to try this out. 
- This Jupyter notebook (https://github.com/pwikstrom/build-a-bot/blob/master/instagrab.ipynb) that utilizes selenium webdriver. This took me 2-3 hours to set up the environment and fix all errors to get it to work on my end. Annoyingly, nothing was successfully scraped and there was no error to trace and fix. I suspect it has something to do with the possibly now outdated load more codes, but I'm not quite sure. 
- A possible PHP solution (https://gist.github.com/cosmocatalano/4544576). I took a quick look into this and it never halted on my end. I have no experience with PHP at this moment, but I could look into this.


6/6
Completed:
- Added some more data collection to current code (scraper_winputs.py): you can refer to the data_test.csv file within the outputs folder of the repo, which scraped 1 particular post with 13 comments (this one: https://www.instagram.com/p/BhJRE1PhUdf/). 
	- Factored code to scrape comments using a new function “single_post_comments”. Features collected for each comment are comment id, comment username, comment time, and comment text. Each post can be grouped by post_id to see a more coarse value of each post. 
	- Factored code to scrape post caption, with column name “CAPTION”. If no caption exists, “N/A” is outputted for that entry. 
Issues:
- I have currently scraped the tags of each post and stored them in a list. However, I’m not quite sure how to display them in the current table format.


