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

shortcodes_wetrepublic = ["rLGaeZAaSw","5Xt5FzgaSf","BTCiG2uDeEu","o-KZFmAac8","BUxP3jdDH_n","yIWkpygaej","XFlGZOgaUm","obib-ZgaRZ","J-sa0ygafI","xFTJWVAabM","1TqZKWAaZm","BT__7gCjBK6","BTMf604DUiK","rhn3iqgaZ2","Bfd9ITIjI87","4SSXoJAaUN","sF8I1JAaSW","zLSXOOAaWT","noRjbUgaTd","544F38gaa5","z-YNjcgafv","BD_uMZaAaXX","BEY_YzEgaQh","PBWtcPgaVx","5MRLA-AafG","BGKgB5JAad1","rp4kErAaQ0","Y3W5UPAaeb","BRBoQ-9DMlD","BO2g6ybhAHQ","qIE4D-gae_","3411lFgad9","p2HGnlAabF","kvABh1AaVO","mY0drtAaVo","tbBO7dgaVe","BgUPuWQje91","BXa4Cdqj_X6","sYdx2_Aabh","BLG8frlBuIK","pepZ7AAaev","bmjejYgaf4","2rAZG-AaSK","6IUmZoAad-","BHpgbBrBNwM","md4MMUAaQO","BhE1OMwDCls","4nHlh8AaYi","snunvrgafd","eibVLbgabk","BF6yrh3Aae5","b99U0OgaeT","zirrg0gabM","zvciDFgacK",]
shortcodes_cavesduroyST = ["BJWF1VdBXX3","Bcp5Y72HSQj","BUNVxV-Bd_U","BIdbFeaBdFh","BZwKaNoHCsm","BQBU_M4Bcfe","BRytg9ZBR2K",]
shortcodes_grandBoston = ["Bhr5O7yhbdm","BhehngpBmbn","BbVFoNxlYly","BiFJFKYhVuY","BiXJ8VFBeOc",]
shortcodes_grandSF = ["BikoaIGglxx","BhSLe7qB9Ai","87DwyEmbc5","BFs8p3MGbXO","BiibmbABbp0","Bh7IE-3B7U5",]
shortcodes_oxfordsc_sd = ["BdA3F8rDXdt","BVF2g-Rgjy8",]
shortcodes_prysmCH = ["Bd7CTC0l2ny","BNfxypiD2R8","BdW8Fg7F3Az","Bfy7NTYFlAf","BbWIn9Jlw2X","BhNYtRHFFqb","BhMpnCcF5De","BRgbureldgc","BineYyeltLU","BgZGnGZHSYj","BWGxGOhle_u","BWgJKvjFi4P",]
shortcodes_rudas = ["BInNBO9gU8i","BGU6yTendHQ","BHNSO5CAbfS","BG1XmCcndNs","BElq0D_ndMh","BDESSv3ndKF","BFojCZiHdFu","BFt8Bv5HdJU","Bdm-yeph7pX","BE3P4LrndE4","BGgS7l8HdHz","Bdm-dHoBJzC","BDcyuvMHdFC",]
shortcodes_templeSF = ["BNC74RCjHGi","35CYp3K0EX","BN-554TDM8c","BhYAgvOH6gn","BYexm-mnXZy","Bd500chni1d","BBjNHzfK0Ie","BVqfKX5F9Ci","BGQeK71q0JV","9mMxNeK0LD","BE1dkAvK0G4","BW3J7psFkcN","BErPsTeK0Cw","BDedCmyq0NM","BJv-MyaAyQo","_YG3X3q0OE","vy4uPDK0Me","7v8p_7K0Io","BFPRq_8K0Do","yxs1gSK0HX","BHiMkWrAWId","BWBsAnxlpaG","BGaq-Bcq0K4","-uNGcbq0Kn","BgoryOSnpdx","BcQHTVLHwSZ","BTvCAMRjM_v","0wGeItq0A7","BXGuc4zFWU-","BH032izAWEf","BFkmay1K0Ge","BeUBnd8HFkv","BC61DFiK0BR","_DG0_Bq0Cn",]

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
		while success is None and tries < 1000:
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