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
- Wrote some simple automation to scrape all clubs in one run. Ran the implementation and wrote the results from scraping all given shortcodes from all clubs in the `outputs` directory. 
	- Estimated scraping speed: ~80 posts per minute. 
- Added and try-except block to handle errors gracefully. This avoids the JSON decoding error from last week. Often, these posts are posts that were deleted on instagram. All erroring posts' shortcodes and error types (e.g. JSON decoding erorr) are stored and saved into an errors.csv file, which is in the `outputs` directory, with all other output files.
- Added a column to scrape the first 10 likes, which is all that is displayed in the JSON file. These results were scraped into the `outputs2` directory. (However the error file in that directory is not correct as I had to restart the code halfway, so refer to all errors from the `outputs` directory).

Issues resolved/need to be resolved:
- Some of the video view counts are incorrect with 0 views. This is an error on instagram's part as the source JSON is simply wrong (indicates 0 views) and hence we cannot do much about it. This is something to be aware of when doing data analysis. 

Next steps
- Look into solutions that allow us to scrape more likes
- Look into Microsoft face APIs to perhaps to gender + face prediction based on instagram profile photos


## 6/24

Completed
- Added Microsoft Face API functionality to identify gender and age of user based on profile picture. Ran this on all users who were the first 10 to like a post, for all posts by clubs Rudas and Oxford. Created a separate file called `data_CLUB_likes.csv` to store the info of each user who liked a post, which can be found in directory `outputs3`. 
	- Estimated scraping speed: 17 seconds per 10 posts, or ~35 posts per minute.
	- Conducted some validation to see accuracy (precision and recall) of the face API. See the Face_API_Correctness.md file for details. 
- Added club information for shortcodes that encountered an error in the script and updated all errors.csv files. The new errors.csv in each output directory now has 3 columns: shortcode, club, and error type.
	- All errors are of the same type: JSON decoding error. This is generally due to deleted instagram posts, causing the JSON file to be not found.
- Conducted datetime analysis on clubs' posts. See the "Datetime EDA" python notebook to see more.
- Added column for weekday. 
- Fixed spacing error that caused all cells/entries to begin with a space. 
- Copied the entire repo to an AWS Lightsail Virtual Machine to scrape continuously without interruption. Rescraped data to fix spacing error and include weekday. (Currently in process)
	- All outputs should be found in the directory `Jun25Outputs`

Next steps
- Test for time zone by commenting on a post
- Look into scraping more likes
- Analyze robustness of face ID in more detail
- Look into analyzing user gender based on full name and check accuracy
	- Synthesize results from face + user full name

## 7/4

Completed
- Updated results from the VM can be found in the `Jun25Outputs` directory. Note that the likes csv files are empty as Microsoft face ID was not used during this scrape.
- Timestamp results: since the datetime is given as a timestamp (i.e. an integer value of the number of seconds since [UNIX Epoch](https://en.wikipedia.org/wiki/Unix_time])), timezone does not matter. Unix Epoch is 00:00:00 1/1/1970 UTC. We simply have to be able to convert the timestamp integer value into the local time and date. 
- Added Gender Analyzer based off first name. 
	- Installed [gender-guessor](https://pypi.org/project/gender-guesser/), a python package that detects first name gender. 
	- Instagram directly forbids GET requests of profiles through `https://www.instagram.com/<username>/?__a=1`, despite our web browsers being able to access it. Instead, I find a quick API [here](https://stackoverflow.com/questions/48709680/is-it-allowed-to-use-this-link-https-www-instagram-com-username-a-1) hosted on heroku that skirts around this: `https://apinsta.herokuapp.com/u/<username>`.
		- **There is an issue with using this API. See below.**
	- Current logic to determine gender: uses gender analyzer based off of first name. If the results are "andy" (androgynous name) or "unknown", calls Microsoft Face API to check for gender. If this still does not yield a result, the gender field is blank.
	- **Approximate accuracy**: off a trial test of 10 posts, out of the 88 likes, 46 of them had their gender identified (52%). I have not been able to determine the accuracy of the results yet, so feel free to do so. You can find the file in `Jul4Outputs/data_rudas_likes.csv`. 
	- **Approximate speed**: 10 posts took about 168 seconds. ~3.5 posts per minute. This looks like it's pretty slow. If we had 8000 posts (which is my guess for the number of posts right now), it'd take more than 38 hours to complete.
- ~~Pushed the gender analyzer back to the VM to let it run. Will analyze my Azure subscription to make sure it doesn't explode in costs. I currently have 200$ of free credit expiring in 12 days, so I plan on using that once our free subscription is exhausted.~~ Currently not in use due to existing issue below. 
	- Our current free plan allows for 30k free calls to face API, of which we've used about 2k so far. 

Issues
- We've maxed out our free requests using this service (I was not aware that there was a limited free amount before maxing it out). There was only 5k total free requests (per IP I think), which was not enough to even scrape Rudas' data. 
	- Found a potential workaround [here](https://stackoverflow.com/questions/49788905/what-is-the-new-instagram-json-endpoint) that does not require the above API. Will look into later. 

Next steps
- Resolve existing issue to get user profile JSONs to determine their full names. 
- Another way to determine gender is to scrape more pictures of a user's profile. Generally, the most pictures a profile posts should be of themselves, so examining more images could be a good way to get more data and hence make a better prediction.
- Look into scraping more likes

## 7/5

Completed
- Fixed issue with getting user profile JSONs by using the above workaround.
- Pushed new script to VM and am now rerunning the script on the VM. Estimated completion: ~1.5 days continuous running. New outputs will be placed in the `Jul5Outputs` folder. 
	- See approximate speed above. 

Next Steps
- Determine accuracy of current gender classifier more confidently. 
- There appears to be some errors with the script that's causing some posts to error. The error traces back to the workaround solution, where a certain key 'ProfilePage' is absent from the JSON. However, the error does not seem reproducible (not sure why this is). Will look into rescraping these when the first round of scraping is done.
- Look into scraping more likes

## 7/6

Completed 
- Scraping complete and the results can be found in `Jul5Outputs`. There were 5153 errors out of the total 7655 shortcodes. All errors are logged in the errors file. 
	- Confirmed that the error does not seem to be reproducible. I can look into this as to why it is; I suspect that the 10 preview likes may change the users each time, or the current workaround is inconsistent.
	- So far we've used about 10.5k of the 30k free calls on Azure, and we used about 7k calls overnight. With 7655-5153=2502 posts complete, 7000 / 2502 x 5153 = 14.5k calls estimated for the remaining 5153 codes, which we should have enough for. 

Next Steps
- Determine accuracy of current gender classifier more confidently by using pandas + Jupyter.
- Use pandas + Jupyter to clean out the error file and then rescrape the error'ed out shortcodes.
- Look into scraping more likes

## 7/8

Completed
- Grouped all errors by club. All error'ed out shortcodes grouped can be found in the `Jul5Outputs/errors` directory. You can find the script that did  this in the file called `Jul5OutputsCleaning.ipynb`.
- Began scraping the 5153 error'ed out shortcodes on Azure and now we only have 3438 errors. Rescraping again; this'll take a few times I imagine. The 5153-3438 newly successful shortcodes can be found in `Jul8Outputs`. 

Next Steps
- Determine accuracy of current gender classifier more confidently by using pandas + Jupyter.
- Look into scraping more likes

## 7/15 & 7/16

Completed
- Revamped code logic to handle errors. New script will now not move on until the parser is able to scrape a full name without error, or until 100 tries have been made. Pushed code to VM to scrape from scratch, and successfully scraped around 6600 shortcodes.
	- Outputs can be found in the `Jul15Outputs` directory.
	- **This makes 7/6 and 7/8's progress obsolete.**
	- Errors are in the `errors.csv` file; there are about 1000 of them.
- My free 200 USD credit 1 month long Azure subscription has expired, just as we finished scraping up this batch. Hence, the 1000 error'd out shortcodes will not be able to go through face analysis.
- Moved all older outputs into the folder `Legacy Outputs`. 

Next Steps
- Determine accuracy of current gender classifier more confidently by using pandas + Jupyter.
- Scrape the 1000 error'd out shortcodes.
- Look into scraping more likes

## 7/24

Completed
- Cleaned errored shortcodes from last scraping and finished rescraping on VM. New script for error scrapings is called `error_scrape.py` and can be found in the `Jul15Outputs` directory. The outputs can also be found there, in a directory called `ErrorFixes`.
- Conducted basic EDA on data. Analyzed recall rate, gender ratio of likes by club, avg number of likes per post by month and by weekday, and number of posts per weekday and month. Report can be found in a PDF called `Precision Recall Analysis`.
	- **When reading data into pandas, there appears to be an encoding error. The fix is by adding the parameter quoting=csv.QUOTE_NONE into the `pd.read_csv` function call.**
	- Some results: 
		- 62% of all profiles had their genders successfully identified. No results on accuracy yet (need to analyze manually).
		- Out of all successfully identified genders for likes, males made up 64%. This may be due to bias from our classifiers; perhaps male names or male profile pictures are more easily to classify?
		- Some clubs had more balanced gender ratios on users who liked a post, while others did not. Notably, prysmCH and grandSF had a 50-50 balance, while wetrepublic had >70% males who liked posts.
		- Somewhat unsurprisingly, posts tend to garner more likes on average in the summer months from June to Sept. There were also more posts during that period.
		- There was also some variance in posts' like numbers between weekday; specifically posts posted on on a GMT monday averaged 486.5 likes, while those posted on a GMT Saturday garnered only 380 likes on average. This was against my initial intuition (as clubs are most busy on the weekends), although it may make sense: instagram posts are often used to hype up events before or after the event.

Next Steps
- Noticed a typo with prysmCH as _prsymCH_. Will fix when all shortcodes are done scraping.
- Look into using selenium to collect more shortcodes?
- Determine accuracy of current gender classifier more confidently by using pandas + Jupyter.

## 7/30

Completed
- Rescraped the error'd out codes (the errors of the original errors) to remove all error short codes once and for all. 

Next Steps
- Clean out all outputs from the 7/15 scraping.


## 8/14

Completed
- Created a successful selenium web scraper to get all shortcodes of a profile. See the `Selenium` folder. 
	-I've scraped shortcodes for CLE Houston, Ohm LA, and Boulevard3 LA at this moment.
- Cleaned up scraped data from 7/15. There were a couple instances where the output went haywire due to different types of quotation marks starting and ending strings, which did not properly close the string and hence affected the shape of the table for the CSV file. Also found considerable duplicate rows between the batches, which have now been removed. 
	- All final outputs can be found in the `final_outputs` directory within `Jul15Outputs`. 
	- Source files from the 3 different batches of output scraping (2nd batch is the errors from the 1st batch, and the 3rd batch is the errors from the 2nd batch) have been moved to their respective directories. 

Next Steps
- Port the selenium code into a standalone `.py` file (instead of through jupyter notebook). Then execute the selenium web scraper on some new clubs. 

## 8/17

Completed
- Modified Selenium script slightly to counteract an annoyance in which Instagram switches around the div containers to mess up the XPath, causing Selenium to fail to find elements by its container location.
	- Completed scraping Temple Denver and Hakkasan LV.
-Began scraping Cle Houston, Ohm LA, and Boulevard3's shortcodes for instagram data on a virtual machine.

Next Steps
- Port the selenium code into a standalone `.py` file (instead of through jupyter notebook). Then execute the selenium web scraper on some new clubs. 