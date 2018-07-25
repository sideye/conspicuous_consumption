import requests
from bs4 import BeautifulSoup as soup
import json
import datetime
import re
import sys
import gender_guesser.detector as gender
import traceback
import os

def get_datetime(time_code):

	print(
	    datetime.datetime.fromtimestamp(
	        int(time_code)
	    ).strftime('%Y-%m-%d %H:%M:%S')
	)

def single_post(shortcode, file):
	url = 'https://instagram.com/p/' + shortcode + '/?__a=1'
	r = requests.get(url)

	b_soup = soup(r.text, 'html.parser')
	new_dict = json.loads(str(b_soup))
	new_dict = new_dict['graphql']
	node = new_dict['shortcode_media']
	file.write(node['id'] + ',' + node['shortcode'] + ',' + str(node['edge_media_preview_like']['count']) + ',' + str(node['edge_media_to_comment']['count']) 
		+ ',' + datetime.datetime.fromtimestamp(int(node['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S') + ',' + str(node['is_video']) + ',')
	
	if node['is_video']:
		file.write(str(node['video_view_count']))
	else:
		file.write('N/A')
	file.write('\n')


def single_post_comments(shortcode, file_posts, file_comments, file_likes):
	url = 'https://instagram.com/p/' + shortcode + '/?__a=1'
	r = requests.get(url)

	b_soup = soup(r.text, 'html.parser')
	new_dict = json.loads(str(b_soup))
	new_dict = new_dict['graphql']
	node = new_dict['shortcode_media']


	#I. Write Post
	#Basic details: ID, shortcode, like count, comment count
	post_details = node['id'] + ',' + node['shortcode'] + ',' + str(node['edge_media_preview_like']['count']) + ',' + str(node['edge_media_to_comment']['count']) + ',' 
	
	# Datetime and weekday
	post_details += datetime.datetime.fromtimestamp(int(node['taken_at_timestamp'])).strftime('%Y-%m-%d %H:%M:%S') + ','
	weekdays = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
	post_details += weekdays[datetime.datetime.fromtimestamp(int(node['taken_at_timestamp'])).weekday()] + ','

	#Caption
	try :
		caption = str(node['edge_media_to_caption']['edges'][0]['node']['text'])
	except:
		caption = ''
	#replaces commas with spaces
	caption = re.sub(r'[,\n]', ' ', caption)
	post_details += caption + ','

	post_details += str(node['is_video']) + ','
	if node['is_video']:
		post_details += str(node['video_view_count']) + ','
	else:
		post_details += 'N/A' + ','

	#Scrapes likes. Currently instagram only shows the first 10 users.
	likes_string = ""
	for like in node['edge_media_preview_like']['edges']:
		likes_string += like['node']['username'] + " "
		gender = detect_name(like['node']['username'])
		if gender == 'male' or gender == 'female' or gender == "mostly_male" or gender == "mostly_female":
			if gender == "mostly_male":
				gender = "male"
			elif gender == "mostly_female":
				gender = "female"
			file_likes.write(node['shortcode'] + ',' + like['node']['username'] + ',' + gender + ',' + like['node']['profile_pic_url'])
			file_likes.write("\n")
		# Deprecated: calls Microsoft Face API to analyze gender. 
		# else:
		# 	age, gender = detect_face(like['node']['profile_pic_url'])
		# 	if gender == None: #No face in picture
		# 		file_likes.write(node['shortcode'] + ',' + like['node']['username'] + ',,' + like['node']['profile_pic_url'])
		# 	else:
		# 		file_likes.write(node['shortcode'] + ',' + like['node']['username'] + ',' + str(gender) + ',' + like['node']['profile_pic_url'])
		# 	file_likes.write("\n")
		else:
			file_likes.write(node['shortcode'] + ',' + like['node']['username'] + ',' + ',' + like['node']['profile_pic_url'])
			file_likes.write("\n")
	post_details += likes_string + ','

	#Scrapes caption for hashtags and mentions
	#Credit: https://gist.github.com/mahmoud/237eb20108b5805aed5f
	tags = re.findall("(?:^|\s)[＃#]{1}(\w+)", caption)
	mentions = re.findall("(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)", caption)
	tag_string = ""
	for tag in tags:
		tag_string += tag + " "
	mention_string = ""
	for mention in mentions:
		mention_string += mention + " "
	post_details += tag_string + ',' + mention_string + ','

	#Has comments
	num_comments = int(node['edge_media_to_comment']['count'])
	if num_comments == 0:
		post_details += "false"
		
	else:
		post_details += "true"
	file_posts.write(post_details)
	file_posts.write('\n')


	#II. Write Comments
	for comment in node['edge_media_to_comment']['edges']: 
		comment_details = shortcode + ','
		node = comment['node']
		#replaces commas with spaces
		comment_text = re.sub(r'[,\n]', ' ', str(node['text']))

		comment_details += str(node['id']) + ',' + str(node['owner']['username']) + ',' + datetime.datetime.fromtimestamp(int(node['created_at'])).strftime('%Y-%m-%d %H:%M:%S') + ',' + comment_text + ','

		#finds tags and mentions
		tags = re.findall("(?:^|\s)[＃#]{1}(\w+)", comment_text)
		mentions = re.findall("(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)", comment_text)
		tag_string = ""
		for tag in tags:
			tag_string += tag + " "
		mention_string = ""
		for mention in mentions:
			mention_string += mention + " "
		comment_details += tag_string + ',' + mention_string

		file_comments.write(comment_details)
		file_comments.write('\n')


def detect_face(url):
	"""
	Returns age and gender of the first face in URL as a tuple. If no face exists, returns (None, None)
	Uses Microsoft Cognitive Services' face API. 
	Get started guide: https://docs.microsoft.com/en-us/azure/cognitive-services/face/quickstarts/python
	Documentation: https://westus.dev.cognitive.microsoft.com/docs/services/563879b61984550e40cbbe8d/operations/563879b61984550f30395236
	Demo video: https://www.youtube.com/watch?v=WysMruemktY&t=1126s
	"""
	params = {
		'returnFaceId': 'true',
		'returnFaceLandmarks': 'false',
		'returnFaceAttributes': 'age,gender',
	}
	headers = {
		'Content-Type': 'application/json',
		'Ocp-Apim-Subscription-Key': '875ba7bdf8df47da919b047314b97ca9',
	}
	server = 'https://westus.api.cognitive.microsoft.com/face/v1.0/detect'
	image = {'url': url,}
	response = requests.post(server, params = params, headers = headers, json = image)
	response_json = json.loads(response.content.decode('utf-8'))
	try:
		return response_json[0]["faceAttributes"]["age"], response_json[0]["faceAttributes"]["gender"]
	except:
		return None, None

def detect_name(username):
	# https://stackoverflow.com/questions/49788905/what-is-the-new-instagram-json-endpoint
	r = requests.get('https://www.instagram.com/' + username)
	s = soup(r.content)
	scripts = s.find_all('script', type="text/javascript", text=re.compile('window._sharedData'))
	stringified_json = scripts[0].get_text().replace('window._sharedData = ', '')[:-1]
	profile = json.loads(stringified_json)['entry_data']['ProfilePage'][0]
	full_name = profile["graphql"]["user"]["full_name"]
	try:
		first_name = re.compile('\w+').findall(full_name)[0]
	except:
		first_name = ""
	gender = detector.get_gender(first_name)
	return gender


#Put your shortcodes in the next line in the following format shortcodes = ['Bg9WTITBE2N', 'BfnwmP2hY4d', 'BeD0vn7h-7E']
#shortcodes_rudas = ['BhJRE1PhUdf'	,'BfnwmP2hY4d'	,'BeD0vn7h-7E'	,'Bd-xJ_uhkk8'	,'Bd-wzgqhVdS'	,'Bd7qd1SBqrX'	,'Bds8eh4hitz'	,'BdpumcqBRVa'	,'BdnalRXBOc1'	,'Bdm-yeph7pX'	,'Bdm-dHoBJzC'	,'Bdm8LCaBbfB'	,'Bdm8Eu-h82e'	,'BbM87AQBw8d'	,'BbIDA1JBAp7'	,'BbH2F04hZNG'	,'Ba9iUYWhZCP'	,'Ba9fzTUhwz6'	,'BaxkbUGhkr3'	,'BaswsnXhNpa'	,'BaqUJ5QBgcJ'	,'BahAKKFhkTE'	,'Bag2EDjhtWQ'	,'BZsn7dnBbIh'	,'BZWuXHYjbWv'	,'BZO2jEEBWuX'	,'BZJ4m-yhBIt'	,'BZGwksQh7ZB'	,'BY7-WI4j99t'	,'BYRXCs0hxQn'	,'BU35WRhDLn9'	,'BUldRqajPs4'	,'BUjkOjsjfj2'	,'BUcItrrhS4I'	,'BTi2tgohBZK'	,'BTSR96MhzeP'	,'BTSADitBiBe'	,'BTRUHr5hoKY'	,'BTGKNwehELB'	,'BSmRRJvhOC2'	,'BR-j8XDBsdH'	,'BR1E0TAhYVI'	,'BQ_G1hDBnw-'	,'BQvn8DoBSAK'	,'BQbBl8RgF6P'	,'BP5oir7A-YM'	,'BP5ocbKARN-'	,'BP5obMWApwQ'	,'BPqMTNBgSKt'	,'BPqMRs5g40x'	,'BPqMQQvgEJw'	,'BPXzK8wAKRz'	,'BPXzIJQg8_g'	,'BPVOK-JAFuZ'	,'BPVOJiLgzQt'	,'BPGE1qagwZG'	,'BPGEvmQgi0y'	,'BPGEuQkgVLY'	,'BOniGSbAEsj'	,'BOniEMxg3Kc'	,'BOfMx_2Ak2B'	,'BOfMwvGAUul'	,'BOfMutEANga'	,'BOfMtd_Ae0A'	,'BOVUG3ig066'	,'BOVUFZ1AxbV'	,'BN4pyqWgLlR'	,'BNuXPR3AD9L'	,'BNuXNn_A4Dv'	,'BNfCyWWgBzu'	,'BNfCv_NgF0l'	,'BNcgnHugtQF'	,'BNcgjk2Aicp'	,'BNZyLzzge-1'	,'BNZyGTWAA1y'	,'BNKXZi_g9-O'	,'BNKXX_TAnU4'	,'BNIHCwbgqS1'	,'BNIHBuog0bs'	,'BNCmXWSgg_i'	,'BM4cuHOgX71'	,'BM4csjrgcjE'	,'BM4crxSAyjo'	,'BMzXvNQAoLm'	,'BMzXsZ0g8FQ'	,'BMrfrQnA72W'	,'BMrfqMqAiNS'	,'BMmU0xeA_U4'	,'BMmUy99Ak-2'	,'BMmUxc0gVWH'	,'BMeIYdOAFvG'	,'BMeIWc2gQnD'	,'BMeITOCgUIp'	,'BMeIQ-0A101'	,'BMUbYV9Au2s'	,'BMUbWShArG3'	,'BMRhEuXgkox'	,'BMRgrf0AY4k'	,'BMRglcoAvOV'	,'BMRgbdyAgN5'	,'BMRgNaNAD8G'	,'BMRgEcXgP6n'	,'BMRf7cdABfe'	,'BMRfzfcAI42'	,'BMRfwDlABGA'	,'BL_22b9AkTq'	,'BL_21XcgeN3'	,'BL_2zuMAH2K'	,'BL_2xwfAKBO'	,'BL_2vZJgS2p'	,'BL1WimYAt-y'	,'BLwNX00A3ek'	,'BLwNG7-gO80'	,'BLtzttRgyf0'	,'BLs8KIzASZe'	,'BLs7rdqAmhx'	,'BLs7i0eA34U'	,'BLs7XjqAp9m'	,'BLoelTygRJm'	,'BLZBi3-AoEs'	,'BLO7a-hg-9R'	,'BLJrGaag9Gh'	,'BLJqp3LAwtw'	,'BLJqSQagCPo'	,'BLEQcGHAfKm'	,'BLEP22TgA3M'	,'BLEPjDYgWth'	,'BK8xcSqgbQV'	,'BK8xPTogDyB'	,'BKyUNSjgOF3'	,'BKyT_o7gmTu'	,'BKyTg5QgrXL'	,'BKyTIw8Az1x'	,'BKyTBoxApEa'	,'BKyS4KigAtW'	,'BKySu5WgJIo'	,'BKySic4AHrf'	,'BKq40Lfgvo7'	,'BKq4p0_A2Re'	,'BKq4YWiAIy4'	,'BKq4O4DA1jF'	,'BKl4OioAmfE'	,'BKkL4evgmDi'	,'BKjEUHPgoTI'	,'BKgg5zTA5uC'	,'BKYzZsWAYLV'	,'BKVlOGBg9-f'	,'BKVkDq2gDST'	,'BKVj2hNAdn_'	,'BKVjRRogyiT'	,'BKVjIhfgKgX'	,'BKVi_xfgXhp'	,'BKVi2i3gfnJ'	,'BKVitx5gSjS'	,'BKRALb5gV2S'	,'BKQu-ijAroW'	,'BKQuXJ4AKPX'	,'BKQuMU6gEUc'	,'BKOV2TLAqQg'	,'BKGx9XlgCNi'	,'BKGxx7HgXZb'	,'BKD-_wPAkCB'	,'BKD-00zA9P1'	,'BKD-tEngE5l'	,'BKA9mNDj26d'	,'BKA9SvAgwWZ'	,'BKA9IVsAhX9'	,'BKA86JVgSrT'	,'BJ7pW2pA62h'	,'BJ7ov52g_xJ'	,'BJ7nZX4ANGR'	,'BJ7nNviAIzU'	,'BJ7nIX8AByl'	,'BJ7nAa-AsaM'	,'BJz34S5A5SM'	,'BJzxLOYAIW_'	,'BJzxKgMglTy'	,'BJzxCUdASiC'	,'BJzwx3lgjRW'	,'BJue8OnAZHG'	,'BJuex8hg4Zb'	,'BJuebLwg-y4'	,'BJueNwLAPLd'	,'BJud2McAZFN'	,'BJs86dlgN3a'	,'BJs8t5rg1tm'	,'BJs8jvBgV1l'	,'BJs8YNIAvh8'	,'BJqL8usAmI2'	,'BJqLvBkgIxR'	,'BJqLRjoAhQb'	,'BJoH5S5AgYT'	,'BJm6QodgzEq'	,'BJm5qcZAMS4'	,'BJm5VYqgqwA'	,'BJmys7cABch'	,'BJlEHOVAqgk'	,'BJlDz1FAZpL'	,'BJfYjGoAcaU'	,'BJfYB2fA38B'	,'BJfXZOggyKa'	,'BJVBQhGgKi0'	,'BJLxDO-ANWF'	,'BJLwvVWAvxT'	,'BJLwafOAD7v'	,'BJLeehHApTB'	,'BJLecrPg-FZ'	,'BJLeFuggbwv'	,'BJLeAahAIs5'	,'BJLd2VvAaqO'	,'BJLdq9FgnNo'	,'BJI1udMgykb'	,'BJGVdDiA04o'	,'BJDnmAdgRXe'	,'BJDniBQgOi7'	,'BJDne_rg2ny'	,'BJDnNR0A69M'	,'BJDmnsdgcSa'	,'BJDmZLYA0zX'	,'BJDmMvlALRl'	,'BJDlzWwg03C'	,'BI8RzXUgOjv'	,'BI8RclPAo2E'	,'BI8Q_cFgW-G'	,'BI8QjnXAwKu'	,'BI5e4Q2gERT'	,'BI5esbxg1Iq'	,'BI5elV2g625'	,'BI5eg8_gNx7'	,'BI5ec8iAQZL'	,'BI0m17SAiZB'	,'BIxMC_7gtLW'	,'BIxL_0UAnmp'	,'BIxL2mtA61f'	,'BIxLn8rAGqn'	,'BIxLiv7g9Gv'	,'BIxLcpYA0Gb'	,'BIxLSiRAyJ8'	,'BIu0Pb2ArjM'	,'BIt9xIrgerW'	,'BIt1E07AeSz'	,'BInrduqAGMy'	,'BInrFbFA6jB'	,'BInrAnJgEot'	,'BInq7yPgBvr'	,'BInq3V_g0ta'	,'BInqs2NA0Kn'	,'BInqk4SAJXJ'	,'BInqcUUgeln'	,'BInqHNFA-3f'	,'BInNBO9gU8i'	,'BIicIIJAa13'	,'BIf3eMYg4jk'	,'BIf3Q82ATB0'	,'BIf3HABgZCc'	,'BIf2qRbgSed'	,'BIf2f99g3m4'	,'BIf19cXgzTe'	,'BIf1q46gjfw'	,'BIf1dw4AWia'	,'BIepMYmAQmD'	,'BIdTSkJg3AB'	,'BIdTPIngDLb'	,'BIdTD6cAONa'	,'BIdS_PsAPEM'	,'BIdSy1dAXv3'	,'BIdSoB9gzPT'	,'BIdShMfAHZ5'	,'BIdSZrngMr-'	,'BIdSNp6g_sV'	,'BIb6Py0Arkv'	,'BIX-eSCA29z'	,'BIX983wgiQG'	,'BIX9KAeg96v'	,'BIVea7rAxVm'	,'BIVeVJ7ghS8'	,'BIVeLZFATt9'	,'BIVeDrigXvQ'	,'BIVd13UgYUs'	,'BIVdxKDAZ4J'	,'BIVdsHhgelw'	,'BIVdl37AERK'	,'BIVdf0MgXzq'	,'BIVdR11giCk'	,'BIVdM4tAs0N'	,'BIVSIQHADMY'	,'BIUd4hvAw7-'	,'BIQVX55A2Vx'	,'BIP0vCzgcTF'	,'BIPFL6fgSh3'	,'BILIlQgAewO'	,'BILIbo9AUiK'	,'BILIYA4APqA'	,'BILH4X8AyXO'	,'BIIVkDxAwV_'	,'BIFEyaWA6VL'	,'BIDTm3eAhbt'	,'BIDTe1YgJp8'	,'BIDTVwpglsr'	,'BIDTSp_AN9L'	,'BIDSnSaAXbu'	,'BIDShz5ABYJ'	,'BIDSaF0AQoS'	,'BIDSU0eAADn'	,'BIDSMh_gOc3'	,'BIDSJo-AJTV'	,'BIC4Po2AZ50'	,'BICTeZvAksC'	,'BICOFPvg0S_'	,'BH9cTkoAyVA'	,'BH7vNKkgHlx'	,'BH6ezEagK7P'	,'BH6eYdrAoA6'	,'BH6eSAdAM9J'	,'BH6ePF8AySh'	,'BH6eImeA91z'	,'BH6eBT6gkRY'	,'BH6dptBAg1R'	,'BH6dkgjgjgZ'	,'BH6ddU0gBy6'	,'BH5n1shgJxU'	,'BH28A-WgfTM'	,'BH27ye3A0qN'	,'BH27mz_AC5e'	,'BH27e4_gC1R'	,'BH27WESg4u4'	,'BH2gG7kgNLd'	,'BH2f6t6AYMW'	,'BH2fwUSAy_P']

shortcodes_cavesduroyST = ["BJBUM46BJnT","BVNW8MzHv9J","BWLfmJ9H1-d","BVvPiAqHogf","BX1HC4Onx8-","BXi_SpynSQs","BAUm0o0BNAF","BIlCQX4hd1-","BK7-qH6BPGN","BfWSflIH6WD","BiKZwKTAE4I","BYjRWDZnQcO","BQ_T5gMBY8U","BQ3be2cBuNv","BWn9PPNH_5K","BTo848JByV8","BRWnlJfBazQ","BMcQG0xB9rl","BcAoOvvHz53","BOYAiisBdc1","BZwKaNoHCsm","BW3GZGwHzf6","BC89x-ZhNLH","Bd-za5AnKee","BJlD5Z_Brr6","BUnVSVUBm7d","BYHPN2qH_tG","Bcp5Y72HSQj","BNppNQ2h3cP","BhcakUtAoh9","BKgbIjjB00g","BJ2v9ZrBzMa","BPnxloghj05","BOprTGbh4cl","BKWkUQtBXKz","Bgb345vg2N4","BJd4zbwhX-9","BRytg9ZBR2K","BimmTFzAKLn","BIdbFeaBdFh","BXbhd6rnQge","BH7uoDgBLov","BIvmTm2BuQn","BJJUht5hRHO","BIGGpfuAtog","BSUCwBEBSZU","BUNVxV-Bd_U","BQbNw2zloQp","BL_rjLuBnoj","BPIwSIyhgkM","BXOihtgnv_C","BF87hrVBNIp","Bg_pfDYnS50","Be1KvhQnxWu","BHaaKCVhrvH","BQBU_M4Bcfe","BUfazk3BbeY","BJWF1VdBXX3","BGzuBS1BNG6","BI3E5FUhKBI",]
shortcodes_grandBoston = ["BiFJFKYhVuY","BhehngpBmbn","Bd0mEsvl_Ls","BfjZNnvFNzJ","Bhr5O7yhbdm","BbVFoNxlYly","BerPsgsl49b","BimycU0hwic","BdbR5aHlR23","Bf1qKLBFF3n","BeOLOf8lw-L","Bb73kRrltQu","BdD-B-tFivj","Bbhe2ODlO6U","Be9Dn6Pl-6F","BcfM1i1lPua","BgHdThtnQ5y","BgWUMZpHonD","BcP6kllFay3","BfTtC8wlU3U","BiXJ8VFBeOc",]
shortcodes_grandSF = ["BbIMpcvBnrq","BSpT_JYg41D","BZhYXoSBTZm","BRysY3Xgu25","BUhmGmPgkKq","9UqEY-GbVr","BW_ca_VAm0P","BhSLe7qB9Ai","BikoaIGglxx","BFmkjw3mbfI","BIs10Pggx8m","Bdyq4TbBrSp","BVYdInCgS_a","BPYT-pIAtx9","kr6eJ8mbRi","BQn9aDsgrvE","BGKwAcTGbTN","BYGvquZAYNO","BBdl4pCGbev","BdBPW6AhSav","BewG7ddB1Fo","BGXk7iaGbZU","BayJEpnBjd5","BVStv0kAVe-","Bh7IE-3B7U5","BI5gyM7gnes","BRqzpd7AGpk","BaNVyN0hLI9","BdTvb6lB_tm","BKq7UbxAb35","BIENOFHgK8R","-7ICPEmbfl","BP-3ONTA3Dn","BH5PSjzgH3F","BCmgffxmbfZ","BiibmbABbp0","BJw7XkZg9G7","BD9FsJ5GbUL","-P6OZlmbcp","BFIx4s7GbSP","BWbCvQ4Aiif","BS7NA2Rgm81","BSjyRFEgKGl","Bg4iGMqhOW5","BGh1vvkGbe7","BV7vgcggSyx","Y3OtNjmbf0","BLKx3JHA8Tk","Bgb9tj6H0K8","BPqXfzvgtZV","BTfU7QPgC-6","BeoDInYBgWj","BAyLr8OGbe5","ueUlhqmbWN","BEjd5wVGbXO","BIYp8PjghvM","BRMLoAyAk82","BFs8p3MGbXO","87DwyEmbc5","BZwM1NVhwkg","BWlWNG9gRJF","BbnD5LOhgYn","8RUy9oGbe5","BTrkxSkgaWe","BG-gjH_mbT7","BEwuXmgGbZ-","BSMQgk5ghyS","VbE6b4mbVr","BUU6GJ5AGiT","a3wTKMmbTd","BMIKI4EgtfS","_p91-0GbV7","BcabnUEBPkf","BaFnJ8-B6N0","BUCtCVBAOj9",]
shortcodes_oxfordsc_sd = ["BdifKAkj1vy","BXGehZrAv2S","BevYsc6DB2q","BWeh-uzAErD","BeGigtCDFlU","BQed8YGB1P6","BZHobhvAIwq","BUGgrDrA7SW","BhADTINh8ul","BTfaMXDAdt9","Bacw2gxArBe","BU98sQcAnNg","BfjlGtnDDkU","BYjvhDNg8lq","BWIXX7Rg-xG","BTHNe1WgxgJ","BYJ0pKLA-q1","BQ06cxBAzHl","BVF2g-Rgjy8","BdA3F8rDXdt","BVYLPm4g2mX","BR40NG4gcUt",]
shortcodes_prysmCH = ["BMNrs2XDyj4","BLrTye9j85P","BYRpc_qFHhS","BVkwEMNlbXi","BRbNTMqlt5Q","BV8EtJwlDVq","BUHpOfElgSL","BVU30dklsTZ","Bi0SFFHHyaL","BJlsDeID5ja","BKbyje5DJB8","BNpiQmKjOHP","BGNHDqdNhFD","BVaAbLyl3ft","BYOqF10FArk","BOQTE6YjfmY","BTfYpTyFbGQ","BTLVJ8_FL1V","BZFO14DlvEF","BOAdWxwDRRQ","BRgbureldgc","BSUbycXlAgI","BUKWO1Vl8iA","BWGxGOhle_u","BVdI__DFm_k","BX3sWLxFJ72","BPzH-rDDbBA","BZWhiL-lWcI","BXf6rueFJTR","BT-Jt6hFigo","BZB6HWQlTr4","BhMpnCcF5De","Bb40qG0FYH1","BV-1nOVlbCV","BMax-kgDPBK","BRWQ8qDFdYb","BUXETohFAOh","BKn-qRADOCy","BNK9pt3jctY","BbfDOSDFcaT","BL4asEpjb3G","BVsDUE-FZWz","BWxqdFjF3Ei","BaUwid2FaV2","BWgJKvjFi4P","BJ88XtYjIsd","BUrruhNFFQg","BRoqcUAlLnT","BgZGnGZHSYj","BSMJSKpFFme","BUfBMCvFyB0","BHaQJmjj32T","BUh5bAJFYTx","BUP2TyEldu_","BSgwr5VFkkI","BapIfi-F_bJ","BTAMZAblDaO","BLXGsuRjBXu","BU2UBhLlJHQ","BWnwr3Llppy","BM-BgA6DYEV","BQq9JYKl9X7","BJBydQJjT6m","BIyaMPuDz9S","BT4RlQ6FfIs","BOaqpEpD8Eo","BQ7SUC1FaRV","BdW8Fg7F3Az","BLHQTQiDjlw","BO2i8JODAz0","Bcg-WJ9lPRi","BN0S_hpDj3z","BW8hJ_JlRkq","BXDkWNnFqtp","BMnOR4LDESv","BNfxypiD2R8","BRMEm2LhdvZ","BJQ6CoBjaDL","BTrnWeWlS1E","BVKj8EwlwNI","BWRvEHulBkI","BXOiP9jFQbJ","BMCgH4sjLBJ","BQlPVc0Dguo","BP-7wWGDeHL","BbWIn9Jlw2X","BUcYKAvlyS9","BYj6V6ClbDE","BNQ8KhLj-to","BYtTr4HFsXQ","BZRV_BoF1aZ","BhNYtRHFFqb","BTHYBCGlOMH","BYEi1H2FJtJ","BX02qt1lsaA","Ba66bL4lQ5o","BeoDliFFzh2","BJ0YNYwDMXD","BTXEwjmlkNg","BVwWL-sFhZH","BZrh36MFCYV","BZ4Xb_sFMMg","BbnIVv_lfpE","BUkcpU0lq8Q","Bfy7NTYFlAf","BWakX7Ql5_b","BSrJLcslJHd","BPfnSnHjEUM","BXrMierlqYc","BIk4yxbDpEP","BRxO6KQlTV_","BTww5CXlX3J","BVC1jW3Fwsf","BHxdBaBjMKF","BTklcuPF8Hr","BPGaoAijM14","BineYyeltLU","BhhsEY8FkbH","BcDk6eMl1Jv","BR8_KX9lvm6","BSl_A-oFme8","Bd7CTC0l2ny","BV2WbZZlA3A","Bea9hNLFwmn","BIavPnoj_xH","BPPCQmgDien","BWOQ60oFhb4","BS3yeb_llab","BW3olYUlulg","BVNkaublMg2","BXJa45NFeUu","BSyp8T6lhht","BIGKw8kDGTx","BK6teNtDR67","BKTQT8qjLOu","BU6I9CeFEQn","BcsSQE9l_YB",]
shortcodes_rudas = ["BFGmDPeHdJ9","BKQuMU6gEUc","BDBJ_XrndI0","BFGmsqTHdLY","BElq0D_ndMh","BFJmac7HdDm","BH6eYdrAoA6","BHfjQa9gJB7","BDAnA20ndLq","BLs7XjqAp9m","BFY9DNvHdAW","BH28A-WgfTM","BIX9KAeg96v","BMRhEuXgkox","BGAD7WgHdNX","BHyqKu-gRQS","Bdm-yeph7pX","BHNS6ryADou","BI0m17SAiZB","BGADlJjHdMS","BHm-cqTgdst","BFBu2IvHdJ4","BUcItrrhS4I","BDSr1QundJQ","BInrduqAGMy","BC_RPr6HdO1","BEiwvmyndG3","BFBtyLHndHV","BPVOJiLgzQt","BJzxKgMglTy","BDgiCDPndKD","BEBHDE4ndDI","BD2klDZndB-","BERSCw7ndNW","BDXpyXJndBB","BHyp5-_A2fh","BETwvT9ndNn","BDkiCqQHdGY","BFojCZiHdFu","BJI1udMgykb","BE-8T-yndME","BDse8wLndHh","BIVdf0MgXzq","BHHxsHJANb1","BOfMtd_Ae0A","BIdTPIngDLb","BFt8Bv5HdJU","BH9cTkoAyVA","BJ7nAa-AsaM","BGY-3fdHdJ0","BGH-IGhHdOh","BHfji7eg6bx","BHAbmgPHdDG","BGMOIm6HdCh","BEI9fsGHdDy","BNZyGTWAA1y","BDcyuvMHdFC","BGgS7l8HdHz","BGm00iandF5","BFYWbyqHdLs","BDfsB_NndDT","BJLwvVWAvxT","BI8RclPAo2E","BKVlOGBg9-f","BEI8gxJndBs","BE3P4LrndE4","BEauSgcHdB1","BKRALb5gV2S","BJDniBQgOi7","BDvAGrnHdLZ","BERSc8EndON","BFcQTdbndKl","BQ_G1hDBnw-","BKA9SvAgwWZ","BD_gokLHdJ0","BDEV8A0ndB-","BHT6YkCgdT9","BDESSv3ndKF","BG64Rw3ndIY","BFBtdhLHdGn","BNcgjk2Aicp","BHNQzjLgdxn","BILIlQgAewO","BElr-9THdAI","BIf3Q82ATB0","BG1XmCcndNs","BJs86dlgN3a","BIDShz5ABYJ","BHHyMqkgnAD","BILH4X8AyXO","BGuTBNHndAq","BDSsBveHdJl","BDbgc54ndA6","BIb6Py0Arkv","BDOeqTPndKM","BGU6yTendHQ","BJm6QodgzEq","BHNSO5CAbfS","BDByiCdndN3","BGR1LyiHdB6","BEsGNz5ndGI","BE3PuKYndEc","BGSpsJ6ndB6","BIxL2mtA61f","BFt7Q31ndGo","BInNBO9gU8i","BKq4p0_A2Re","BFQ-0ObHdMb","BDa3eCyndFg","BD2kD3AHdBY","BGmysVlndPu","BDsfbisndIX","Bdm-dHoBJzC","BF1IxM5ndPJ","BJmys7cABch",]
shortcodes_templeSF = ["BAvrpgOK0P2","-4g8KDq0L5","Bc28GfAHSub","BGQeK71q0JV","BfBw7kZHc2O","42dEYJK0HT","Bb8STbHHpS1","BUIzT5TgIb6","3AeaTBq0Bi","BhPi6xJn0U6","BY1N_SmHZ80","BJGhfVUAUcE","BVNNWRnAXTf","BVqfKX5F9Ci","BBq8xkgK0F2","BHX0wSaAtpb","BQ8hWnRDg-i","_IWZQcq0BQ","-FRW1VK0Gv","BI5uHggAJ3V","BSxMpk7gGb5","BHtMuvVgXH_","_DG0_Bq0Cn","0wGeItq0A7","BfTzc_jHzV_","BWOnGcslVAT","BP8Gh0nD9Fy","BOyQpNxjxxq","9epQHjq0GE","BWawITAl2DD","Bc-nI-pnyP9","5nQBS5q0Kc","58Rsw4q0D6","BDmEuzCq0I0","BY-ASzknIG9","BCcBNAvq0Eo","8wYQcUq0N6","BTPLGdvgQcW","BSmMQvnAOKE","BWx70tUlacU","BBS-LURq0Hz","BEEwp9CK0E5","BeUBnd8HFkv","BfKOZlZHWEn","5YJ2-3q0Bx","BRluLKQDtHX","6LYkMcK0Gf","BcsiE1anVKi","BOIcgmAjpQg","BRcOOqmjxHc","BEMSnUvK0Hf","BH032izAWEf","0YqeKDK0FX","-e3xDhq0Ax","BIion3KgbJs","17qNmLq0Nt","xvSQcYq0LD","_f0DLrq0Mi","BPQ3yDhjA6H","BWjHVLwl2A4","BeMjDKIH-LH","BDedCmyq0NM","xAohsEK0BF","BX1EZ2TFt0S","BSRl4deAX2f","BT13lzpDOqE","BfruazCHR5J","BafYtwCHTzh","Bdx-eK_HAZQ","BgZXo4vh1iU","BauJe4_HXfs","BNC74RCjHGi","BCTVhgYK0Aw","BcjJ87fHoHM","3zwKYZK0I1","9uQ4KFK0Ah","Bbu2-DzHVFc","6F71qkq0Nx","BJ80Y3gAZa_","BDEKSj1q0Jc","BPt8J7eDonW","BTvCAMRjM_v","BU-peShACM0","BK4rjCKDG1c","BYMEnTPHP_R","BanJeChn8rj","BAnIWj7K0C_","BcalBNznwVw","BYq_iXxH4Uq","BeuRV_nHSmT","BYexm-mnXZy","BJeCTbSgwI3","BAQGvecq0H9","Bg-IJCXHWoY","BZIFvDInGpK","BPbilJXDSHZ","BGxJcPBK0Py","BZ9IeSKn3Yk","BJv-MyaAyQo","yxs1gSK0HX","BUSVsZWg8IN","BCCAGZ-q0DV","BS9GU_2AYZc","BUcYaczAejd","BAaaaCOq0Oa","BJTcXqRAENK","BYWVk79nLII","BX6rp5rlm4G","BXGuc4zFWU-","Bf95v5Snvr8","Ba-kU8HHaev","BhfwbpNnsqw","BKHxfcOA9hb","BIVW_m6AaRX","0MvG8cK0Nm","BGGFUJAq0J-","BGaq-Bcq0K4","9mMxNeK0LD","BbQBGJwl9kQ","BbGGrAmnv6a","BdTy28mHrUs","BUAEWQaAasg","9HCftnq0Nh","Ba2liZBHwFi","7Yqfgxq0CW","8hR3-5q0At","BFkmay1K0Ge","Bdoab7tH9iI","BgHY5BuBWfN","BQedeHvDQNu","BMFdm80D-ZF","BeEKfdpnVYl","BRE8YykjkJJ","BOpzVygjvaO","BhYAgvOH6gn","BN-554TDM8c","vLTBVlK0Eh","BKR4hQ0AJSQ","BMnLyK8DN8U","BUh505JAWCZ","BFxe8kFK0Ig","BTFsSI3ANsK","BcGTVhvHGRf","BIBJ-CxAo26","_YG3X3q0OE","BFDVQNMq0Nt","BbgF-5Cn2NT","BTfk_CUDOv9","4bJGZsq0PY","BZrQtwgHFvW","Bgh4OWUhuX0","BhFPLIjntYm","BHiMkWrAWId","7v8p_7K0Io","8Og3KTq0FQ","wnZC4NK0A3","99qHO0K0Ak","vg6Dkbq0OL","4pX2tOK0No","BMQP1rjjGmr","BNnAc5cDzjR","BOVIuwnDn_r","8T3o21K0D9","BW3J7psFkcN","BCwADDUq0Mh","BQGVCTLDmbS","BG7U3uiq0Bu","BNaCt_CDFm0","BJn4H0tgAt-","BU2Wy23gMxz","6ijimOq0H5","BErPsTeK0Cw","BgoryOSnpdx","BL2dFwvDU6t","BIKxyk5A2wf","BQydsSpj4fp","BXrRzTUlVb-","BVc4AS3l8hF","Bg1sBc2Hq8w","BebbxO5nDIa","BfbsyWxnGHP","BMx0H70DnE4","BE1dkAvK0G4","BGk4arwq0FL","BRPdP6PDZhO","5Nd61Hq0IH","Be4mNQDHVIo","BBVi_-3q0Cd","BEXVWo4q0BB","-Sl3iUK0Il","BcQHTVLHwSZ","-uNGcbq0Kn","wZqpIcK0B4","BB5mLQEq0G6","BD1zMQlK0M7","65lWQzK0Hu","BaX6LP7H6Nf","BKuJ8fAjbiX","BKghszMA9mI","BXYqSK2Aqwr","BXivBmIFvMD","BC61DFiK0BR","6xsLvPq0Im","BDuI7buq0Jg","BSZZiWjgCkL","v_8bypq0Mt","BSEtSKsgLnb","BADcubqq0Ny","BdeJP6-HCnx","BBjNHzfK0Ie","vy4uPDK0Me","2eU1fwK0K1","8_Sr3nq0G5","BHLo3cRAtnt","BFccs5Rq0HG","BCmQcUDK0OY","1U_6oMq0DO","BdMXux4nzVs","BZcmikvn9E4","35CYp3K0EX","BaRvx49H4Ay","BQRv7T0D10y","BPDsuvZjNLs","BItuwE-AEZT","BN2j7Jtj0LR","BDRWy6Lq0EL","Belj0PEHbMw","BFPRq_8K0Do","BWBsAnxlpaG","BEhnbUOK0Be","BV0IB9dFcmQ","BMaegesjuWw","BLcTQijDhx8","BRyn8T_A5si","7JT7qIK0Ae","BfjK3QbnqVY","BF6vXQKq0C0","BQo2Abng9QF","Bd500chni1d","BbXxNV3ntC5","9WpmsoK0Eb","BR7HBJVADYI",]
shortcodes_wetrepublic = ["BVcsg2vDigm","qF_FzjgaWC","sTPMTOgaUl","lLLWDYgacu","qSOr6GAaR1","BgUPuWQje91","XFlGZOgaUm","8y5tTTAaeP","Bdk8cxZjqG7","kvABh1AaVO","BQOYiJyhqZj","BYtWSuHDB4h","BKi5vP-BAUf","2W0zfAgaWz","TgypVNgaRi","BftxQewjJ2a","uYthBkgaWT","dfroMJgaQQ","QFxqTVgaT9","BYGscB8DOe2","lfcdocgaSv","njPrSQAaUw","quH-uZgaV2","BFwigY3Aac4","cIGYyzAaf8","2gy17fgaXx","Bhjv7btD3Gu","BelUNsAndqc","a1xwAWAaTZ","BXOTuwLjt57","n1ZiwbgaVW","BTCiG2uDeEu","BHPvzMtBQYJ","8tIgFbAaa5","raOF9uAaSr","rnCmL0gafF","3Nq_PWgaWq","BF6yrh3Aae5","pRb59FAadF","6N1qjpgaRz","1JC843gaZO","LHy5R0AaZp","xkus4tAad4","BVS0wQRjDHZ","rGE4F9AaWf","bcNaaJAaeW","nYemUCgaRS","z0s_ZMgab9","bw9ArRAaSf","4KJpn7gadH","BAfEO0fgaWp","BHpgbBrBNwM","BKv06DFBOkA","sNt_TCAabT","BIvClGchakB","KiO3oYgaeY","pNIrTrgaQB","yIWkpygaej","vEpSgpAaVS","q-JzGegadH","Yn-J2vgaUe","BZEc_apDXMb","BPsqXrlh_-5","BE9UQu4Aaa4","1jb8SFAaQR","m1LVdlAac2","d7gPvYAaZo","13Y4-dAaZ0","qIE4D-gae_","kA63XFAaWE","BKOLzTzhDzT","PBWtcPgaVx","ntWNokAaeY","BIc65TzhgC8","BJbBblMB3MZ","OfasDJAabs","BCQkXA2AaXa","obib-ZgaRZ","OE7YnPAabJ","aReiOdAaXY","2kAOB4gaeW","XU-9EGAaTx","BE4WrHkgaca","BRYvvu8DHQE","0LUpJPAaaK","fNr4v4gaes","BTrc1f5Dx0J","s_EhZmAaSA","dp3qq8Aadd","5dTeEbgaU_","W5YKsDAaaT","BCgBxxxAac7","md4MMUAaQO","BTzIt0oDnzE","BCMCAwnAaWs","BHZ_ibohR7u","BamSqvUDnP4","Bfd9ITIjI87","2RSdb1gaZ9","nOq_flgaYo","Bf6SEiuDe38","BFmPIqlAaZK","4Gz2JlAaZ1","pbuibggafW","Z1X45bgaep","0_YjnBAaSf","_nYBs1gaUg","BGKgB5JAad1","4ALqPfgaVu","BQirlfxFPMM","o-KZFmAac8","BI75mhZh1a0","5x50qEAaXW","nEj3CwgabG","aUONUeAaWm","BEY_YzEgaQh","rQvALCAaVN","BLY-L4QhVLk","0giPmsgaZt","1n8Ji1AaQp","BRtkyaSjNdc","21MYnrgabD","syOQ6AAaXt","BAuqT6IAaVu","BJf9sMDhF0I","zvciDFgacK","qhW8iwgaTv","6_Jk-sAaZF","9KGAgVAab2","mY0drtAaVo","BDlwoVMAaW4","n_J0kFgabw","sk8ilAAaZ_","6VaxuHAacU","pEhwWZgafr","BUxP3jdDH_n","8Lwt9AgaTX","BGUnYWIgaV2","BXBcuRegFOj","BTfLOV6jB-8","1bRU75gaac","a_brJ6gaYh","BgHfc3LDt1-","oqwsNgAadf","BR_Q5JgjteZ","BXa4Cdqj_X6","p-DyDMgaa6","p7GXtWgaV_","4nHlh8AaYi","rc0lFeAaTr","mqUTi_AaSv","BDOf80ngaW1","sLFuatgaTq","eibVLbgabk","mT2Wgegaf7","BG2jhzHAafV","e3NV00gaYm","ZMC4BQAacC","BgoitCQjjtb","3WqBbSgaU3","awksRegac-","BCs4x91gaW8","BUc29iqD1Zj","sYdx2_Aabh","BZUA9_qjEUQ","2wz_n0gaR6","tInunwgadc","rLGaeZAaSw","l8qju-AaVz","mv-9DdAaWl","2Mf-5MAadT","3t7_51AaTK","IkigRkgaSS","pepZ7AAaev","oCXbPaAaZT","KVjhRKAacc","Y5---fAaX-","Be_B4uWDWeA","2EeTA9AadT","uBzdlEgadW","eQlhWEAadO","BJ5sTFQBvRe","XlCuZCgaTp","BFhYggNAaVY","tvWbtwgaVu","r7zSDXgaeS","BPLHOXvBHEh","BEJzKQYgaUk","J-sa0ygafI","BGaK0Z-gaVW","BVKrarejwwg","nJvGTwgaeN","3IeYSKgadN","nTcTRhgaRn","xFTJWVAabM","rvJsn4AaW8","BUM69dkjldl","s8ZguGgaUh","BSMcsLxDruo","2_gWv8gaYi","73ECHbgad-","eF0CckgaU_","BS35kx-jjfa","WVZE_BAaUS","BT__7gCjBK6","bT-rVCAaSM","pWtACOAaao","BD_uMZaAaXX","m_SfdtAaWA","BJyTGBKhWP-","r2fXYJgac2","zSsL6-gaa5","tVg_jcAaRj","noRjbUgaTd","-j4rDbAaTT","svnxCYgaRV","OKz4KuAabW","BaCp9t6jn0R","qqQxVxgafc","yxN0fOgaVf","BBYBOYcAaf_","BH2YAM4hH_E","5sAKM9AaSq","NmV5FVAaWa","Y3W5UPAaeb","y-J-xZAaaj","omM9KVgaSL","lVPbd4AaYB","rhn3iqgaZ2","0n-k34gaXe","mIqdaDgafS","bHb4ULAaSk","MRA99dgaSU","Xf5nfMgaZS","5Xt5FzgaSf","BUP5fZdjJyE","Jp30J2gaU5","BIlL_70BjZY","ym6og5AaU7","BRi35qyjxQc","BIVRsTahiE1","Bbugtnij5Wa","BVnCPoajdHM","4wx1rHgaTj","2rAZG-AaSK","s3PSDzgaQL","sqamicAaUx","z-YNjcgafv","Bg6ygrxDMjJ","oXJXFPAaf4","6qHw8MAaTJ","q6JCfhgaXO","BD9QD_6gaYv","rp4kErAaQ0","k-ef3hgaXK","pxUYNCgaS6","X0SaoIgacQ","rP3cRKAaR_","mjAHDMgaTE","BJQ0x6PhvZl","4hWHxmgaaA","ZtZHqBAaXW","pJs_g2gaaF","aCEKX2gaaJ","BTMf604DUiK","tCofuXgad6","heFLP0gafm","BO2g6ybhAHQ","6drRTJAaRw","3znsEGAaTT","BLobRMehdoU","dCxjYOgaYI","BhE1OMwDCls","BEeZiLVgaSp","7G-1C7gaWM","qZjTkpAadK","qerMVhgaYD","BSULcQzjzBr","BV-Kw3tjsjM","rVhpv7AaVC","oUNwIDAaYD","BY3k2AiDpwV","ZwH9TOgaX4","BgbphBZjzoS","BSwknh-DMPX","q4lbQaAaZY","BRBoQ-9DMlD","BTU0ISzDfir","NClDRngaRu","qC_GnggabE","BJBC22WBUYH","tOVfuXAaSe","544F38gaa5","3j2VYrgaSA","pkd9bNgae4","5IEvelAaQE","7v9oQ3AaR2","7VlDL_gaUx","BGxFT8AgaV3","BcpubRVDFzh","BDbIPmMAafU","sX_apVgaTb","qm7uigAaWX","qVJV6zAaeX","PVDjW-Aaft","czyiqpgaVW","snunvrgafd","BSjUK0BDyAY","phF2fXgaY5","LMMGYkAaW0","mbQ7chAaXZ","oPNClhAaVs","tbBO7dgaVe","0QYiV6AadM","BDBkTNJAac5","BWOB2KnjJGW","BZrFDvhj0mh","U1xOSWgaS6","X-ObH9gae9","7oBzPrgabW","6yRW9BgaRW","rDC7G3gaSE","ticvLSgaTv","bmjejYgaf4","BIAsFpbh2hI","6A-P_CAabL","7cA0uIgaRm","6IUmZoAad-","BU9zfehj7z5","BFb7YecgaZ_","62xMVygaYc","YGpgvxgaUE","5MRLA-AafG","1RG4z1gaT8","BUryOGqD1Ns","18i8vxgaTA","sAyi1agaZ9","mtQArlgaSF","nypfVdgaQl","lqNAJuAaZk","dNhNMjgacT","BRTmaPrDrLi","JQEuKngaYt","p2HGnlAabF","l0jqBQAaTU","eXwSbYgaZz","zLSXOOAaWT","ne3Jm6gaSW","BRweV2gjzPx","oHJf0kAaVi","tqeANhgaaj","3411lFgad9","Yqotaygac0","YfurZfAacy","3gBLLMgaYd","BGpjnC-gac9","cuRoTKAaXA","BHAxDTSAaf_","ZeKrdbgabY","4Z7OYEgaSL","08eENmAaY8","471dmsAaRU","sF8I1JAaSW","0YVd7pAaQB","8CAe7LgaX_","LtcAUBgaXa","zirrg0gabM","J0BqJ3AaWb","ajI-W2gabv","jH_hGkAac2","eu9GVggaV3","7gA0bpgaeq","1TqZKWAaZm","K21GDbAaRl","o4QiqcAadq","dxL2OygaRG","a4Yvr6AaZw","BhRutsZDZ2I","96fpkTAaWN","BW5aHgKjdgL","Zd9U_cgaU0","mOHokSgadt","1vvk4ZAaYQ","BLG8frlBuIK","tLMdobAaRz","r0OMWPgaW8","0ynbeDgacF","b99U0OgaeT","n54zyxAadp","qNKORtgaQF","ccdLbKgaQH","sfbHIjgaUp","qzRlUWgaSH","4SSXoJAaUN","BJqPhVKh8bI","BNr1kXRBpnJ",]

#All clubs dictionary 
clubs = {"rudas": shortcodes_rudas, "oxfordsc_sd": shortcodes_oxfordsc_sd, "wetrepublic": shortcodes_wetrepublic, "templeSF": shortcodes_templeSF, "grandBoston": shortcodes_grandBoston, "grandSF": shortcodes_grandSF, "prsymCH": shortcodes_prysmCH, "cavesduroyST": shortcodes_cavesduroyST}
#clubs = {"wetrepublic": shortcodes_wetrepublic, "templeSF": shortcodes_templeSF, "grandBoston": shortcodes_grandBoston, "grandSF": shortcodes_grandSF, "prsymCH": shortcodes_prysmCH, "cavesduroyST": shortcodes_cavesduroyST}

# errors = ["Bdm-yeph7pX","Bdm-dHoBJzC","kvABh1AaVO","BiFJFKYhVuY","Bhr5O7yhbdm","BhehngpBmbn","Bh7IE-3B7U5","BiibmbABbp0","BikoaIGglxx","BhNYtRHFFqb","BhMpnCcF5De","BgZGnGZHSYj","Bfy7NTYFlAf"]
# COMPLETE
#file = open("data_rudas.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_rudas:
#	single_post(code, file)
#file.close()

#COMPLETE
#file = open("data_wetrepublic.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_wetrepublic:
#	single_post(code, file)
#file.close()

# COMPLETE
#file = open("data_oxfordsc_sd.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_oxfordsc_sd:
#	single_post(code, file)
#file.close()

#file = open("data_templeSF.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_templeSF:
#	single_post(code, file)
#file.close()

#file = open("data_grandBoston.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_grandBoston:
#	single_post(code, file)
#file.close()

#file = open("data_grandSF.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_grandSF:
#	single_post(code, file)
#file.close()

#file = open("data_prysmCH.csv","w")
#file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
#for code in shortcodes_prysmCH:
#	single_post(code, file)
#file.close()

# file = open("data_cavesduroy.csv","w")
# file.write("ID, SHORTCODE, LIKES, COMMENTS, DATE, IS_VIDEO, VIDEO_VIEW_COUNT\n")
# for code in shortcodes_cavesduroyST:
# 	single_post(code, file)
# file.close()

# file = open("data_rudas.csv","w")
# file.write("ID, SHORTCODE, LIKES, NUM_COMMENTS, DATE, CAPTION, IS_VIDEO, VIDEO_VIEW_COUNT, HAS_COMMENTS, COMMENT_ID, COMMENT_USER, COMMENT_TIME, COMMENT_TEXT\n")
# for code in shortcodes_rudas:
# 	single_post_comments(code, file)
# file.close()

# file = open("outputs/data_cavesduroy.csv","w")
# file.write("ID, SHORTCODE, LIKES, NUM_COMMENTS, DATE, CAPTION, IS_VIDEO, VIDEO_VIEW_COUNT, HAS_COMMENTS, COMMENT_ID, COMMENT_USER, COMMENT_TIME, COMMENT_TEXT\n")
# for code in shortcodes_cavesduroyST:
# 	single_post_comments(code, file)
# file.close()

# file = open("outputs/data_prysmCH.csv","w")
# file.write("ID, SHORTCODE, LIKES, NUM_COMMENTS, DATE, CAPTION, IS_VIDEO, VIDEO_VIEW_COUNT, HAS_COMMENTS, COMMENT_ID, COMMENT_USER, COMMENT_TIME, COMMENT_TEXT\n")
# for code in shortcodes_prysmCH:
# 	single_post_comments(code, file)
# file.close()

# file = open("data_grandSF.csv","w")
# file.write("ID, SHORTCODE, LIKES, NUM_COMMENTS, DATE, CAPTION, IS_VIDEO, VIDEO_VIEW_COUNT, HAS_COMMENTS, COMMENT_ID, COMMENT_USER, COMMENT_TIME, COMMENT_TEXT\n")
# for code in shortcodes_grandSF:
# 	single_post_comments(code, file)
# file.close()

detector = gender.Detector()

errors = {}
output_dir = "ErrorFixes"
if not os.path.isdir(output_dir):
	os.mkdir(output_dir)

for club in clubs:
	print("Working on", club)
	file_posts_path = output_dir + "/data_" + club + "_posts.csv"
	file_posts = open(file_posts_path, "w")
	file_comments_path = output_dir + "/data_" + club + "_comments.csv"
	file_comments = open(file_comments_path, "w")
	file_likes_path = output_dir + "/data_" + club + "_likes.csv"
	file_likes = open(file_likes_path, "w")
	file_posts.write("ID,SHORTCODE,LIKES,NUM_COMMENTS,DATE,WEEKDAY,CAPTION,IS_VIDEO,VIDEO_VIEW_COUNT,USERS_LIKED,TAGS,MENTIONS,HAS_COMMENTS\n")
	file_comments.write("SHORTCODE,COMMENT_ID,COMMENT_USER,COMMENT_TIME,COMMENT_TEXT,COMMENT_TAGS,COMMENT_MENTIONS\n")
	file_likes.write("SHORTCODE,USER_LIKED,GENDER,PROFILE_PIC_URL\n")
	file_posts.close()
	file_comments.close()
	file_likes.close()
	file_posts.close()
	index = 1
	for code in clubs[club]:
		file_posts = open(file_posts_path, "a")
		file_likes = open(file_likes_path, "a")
		file_comments = open(file_comments_path, "a")
		print("Currently working on: ", club, "Code: ", code, index, "out of", len(clubs[club]))
		index += 1
		success = None
		tries = 0
		while success is None and tries < 100:
			try:
				single_post_comments(code, file_posts, file_comments, file_likes)
				success = 1
			except:
				tries += 1
				errors[code] = [club, sys.exc_info()[0]] # Saves both club info and error type as a list
				print("Error on:", code, club)
				traceback.print_exc()
		file_posts.close()
		file_comments.close()
		file_likes.close()
print(errors)
file_errors = open(output_dir + "/errors.csv", "w")
file_errors.write("SHORTCODE,CLUB,ERROR\n")
for key, value in errors.items():
	file_errors.write(key + ',' + str(value[0]) + ',' + str(value[1]))
	file_errors.write("\n")
file_errors.close()