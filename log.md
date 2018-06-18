# Progress Log
## 5/28

Overall, I came in expecting quick success in scraping instagram for all sorts of data, but I soon realized that this was much harder than I had imagined. I estimate I put in about 8-10 hours looking into this, and I have to say that the results are not as successful as I would have liked. 

I mainly focused on getting post shortcodes this week:
- Instagram official API: didn't work. I think Facebook requires users of its graph API to be developers with apps and privacy policies. 
- This Instagram scraper (https://github.com/rarcega/instagram-scraper) using python: this app seems very promising. I found success with this for the first couple tries, but it stopped working on my end soon after so that I could not implement modifications. The app also has a lot of features including scraping for comments/likes/hashtags. I think we can modify the code pretty easily (from looking at app.py, follow and trace the scrape method) to scrape shortcodes.
- This website (http://www.picluck.net/) that displays all of instagram's content but removes autoscrolling. This seems pretty promising for scraping likes/comments/users etc. However, I have not been able to recover shortcodes of any post from this website, which makes it a little challenging to use. Perhaps there exists a smart work around/clever hack?
- This app (https://www.4kdownload.com/products/product-stogram) that acts as a desktop app and apparently downloads the photos. Could you possibly look into this? Currently I am behind the great firewall and the app does not work with my VPN, so I have not been able to try this out. 
- This Jupyter notebook (https://github.com/pwikstrom/build-a-bot/blob/master/instagrab.ipynb) that utilizes selenium webdriver. This took me 2-3 hours to set up the environment and fix all errors to get it to work on my end. Annoyingly, nothing was successfully scraped and there was no error to trace and fix. I suspect it has something to do with the possibly now outdated load more codes, but I'm not quite sure. 
- A possible PHP solution (https://gist.github.com/cosmocatalano/4544576). I took a quick look into this and it never halted on my end. I have no experience with PHP at this moment, but I could look into this.


## 6/10

Overall, I've modified the code to scrape comments. I think the URL extension trick scrapes in exactly the first 40 comments.

Completed:
- Added some more data collection to current code (scraper_winputs.py): you can refer to the data_test.csv file within the outputs folder of the repo, which scraped 1 particular post with 13 comments (this one: https://www.instagram.com/p/BhJRE1PhUdf/). 
	- Factored code to scrape comments using a new function “single_post_comments”. Features collected for each comment are comment id, comment username, comment time, and comment text. Each post can be grouped by post_id to see a more coarse value of each post. 
	- Factored code to scrape post caption, with column name “CAPTION”. If no caption exists, “N/A” is outputted for that entry. 
	- Implemented regex to scrape hashtags and mentions (tagged users) from post caption and comments. However, I am not sure how to implement this into the table (see issues below), so it is currently commented out and not in practice.
- Updated cavesduroyST's given shortcodes using the new script to include the above added columns/features. 

Issues resolved/need to be resolved:
- Since the output file is in CSV format, the output breaks (does not adhere to desired table format) if either the caption or comment includes a comma or new line (\n). Currently, I have been changing them to spaces to avoid this; tell me if you want to change it to something else. 
- I have currently scraped the tags and mentions of each post and comment, storing both in lists. However, I’m not quite sure how to display them in the current table format.
- Due to the nature of the table, if a post has no comments, currently it is not outputted at all. I've currently dealt with this by adding a "has comments?" column with true/false values to not discount posts without comments. If a post has no comments, then its 4 comment columns are marked as "N/A"
- The like preview (edge_media_preview_like) allows us to scrape the first(?) 10 users who liked the post. I can implement this if you want, although it may not be a representative or accurate sample. 
- Some of the posts have a JSON decoding error: not sure why this is happening. Does not appear to be a bug in the scraper. Will look into later.


Next steps
- Look into JSON decoding error.
- I think I should be able to download the pictures using this script, if you'd like.
- Resolve how to store mentions and tags in comments and captions.
- Determine how to scrape likes.


## 6/17

Completed:
- Modified table schema into 2 tables as discussed, 1 table purely for posts and another for comments. Both tables can be joined on shortcodes. 
- Changed: if a post had no caption, the data entry for the caption column is now empty (a NaN) instead of "N/A"
- Added features to scrape tags (proceeding a #) and mentions (proceeding a @) for both comments and posts, so these features exist in both the post and comments tables. Each hashtag or username is separated by a space. 
- Wrote some simple automation to scrape all clubs in one run. Ran the implementation and wrote the results from scraping all given shortcodes from all clubs in the outputs directory. 
	- Estimated scraping speed: ~80 posts per minute. 
- Added and try-except block to handle errors gracefully. This avoids the JSON decoding error from last week. Often, these posts are posts that were deleted on instagram. All erroring posts' shortcodes and error types (e.g. JSON decoding erorr) are stored and saved into an errors.csv file, which is in the outputs directory, with all other output files.
- Added a column to scrape the first 10 likes, which is all that is displayed in the JSON file. These results were scraped into the outputs2 directory. (However the error file in that directory is not correct as I had to restart the code halfway, so refer to all errors from the outputs directory).

Issues resolved/need to be resolved:
- Some of the video view counts are incorrect with 0 views. This is an error on instagram's part as the source JSON is simply wrong (indicates 0 views) and hence we cannot do much about it. This is something to be aware of when doing data analysis. 

Next steps
- Look into solutions that allow us to scrape more likes
- Look into Microsoft face APIs to perhaps to gender + face prediction based on instagram profile photos


## 6/24

Completed
- Added Microsoft Face API functionality to identify gender and age of user based on profile picture. Ran this on all users who were the first 10 to like a post, for all posts by clubs Rudas and Oxford. Created a separate file called data_CLUB_likes.csv to store the info of each user who liked a post, which can be found in directory outputs3. 
	- Estimaed scraping speed: 17 seconds per 10 posts, or ~35 posts per minute.
	- Conducted some human validation to see accuracy of the face API. See the Face_API_Correctness.md file for details. 
- Added club information for shortcodes that encountered an error. The new errors.csv in each output directory now has 3 columns: shortcode, club, and error type.
	- All errors are of the same type: JSON decoding error. This is generally due to deleted instagram posts, causing the JSON file to be not found.

Next steps
- Logging for errors?
- 
