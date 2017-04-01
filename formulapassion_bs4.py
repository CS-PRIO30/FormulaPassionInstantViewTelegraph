# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen #http://stackoverflow.com/questions/2792650/python3-error-import-error-no-module-name-urllib2#2792652
import feedparser
from telegraphapi import Telegraph
from telegraphapi.exceptions import InvalidHTML
import telegram
import schedule
import time
from colorama import Fore, Back, Style

allUrl = []

telegraph = Telegraph()
telegraph.createAccount("PythonTelegraphAPI")
TOKEN_TELEGRAM = '342889196:AAEvqWUngHIBjtmKG-gcLjso4_BvzHZgq_8' #Fpivbot
MY_CHAT_ID_TELEGRAM = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)

def populateAllUrl():
	f = open("log.txt","r")
	rows = f.read().split("\n")
	f.close()
	for row in rows:
		allUrl.append( row )
		'''
	for i in range(len(rows)):
		print i,rows[i]'''

def printWarning(string):
	pass
	#print(Back.YELLOW + Fore.BLUE + string + Style.RESET_ALL)

def sendTelegraph( articleImage, articleTitle, articleDescription, articleUrl,articleContent ):
	global MY_CHAT_ID_TELEGRAM
	articleImage = articleImage
	articleTitle = articleTitle.replace("| FormulaPassion.it","")
	articleDescription = articleDescription
	articleUrlmod = articleUrl.split("/")[-2]
	articleContent = articleContent.replace("\n\n","\n")
	articleContent = articleContent.replace("\n\n\n","\n")
	IMAGEHTML = "<a href=\"" + articleImage + "\"><img src=\"" + articleImage + "\"></img></a>"

	LINK = "<a href=\"" + articleUrl + "\">LINK</a>\n"
	html_content = IMAGEHTML + "<b>" + articleTitle + "</b>\n" + "  " + LINK + articleContent.replace("<strong>","<b>").replace("</strong>","</b>")
	html_content = html_content.replace("<p>","").replace("</p>","")
	#print html_content
	try:
		page = telegraph.createPage( articleTitle, html_content= html_content, author_name="f126ck" )
		url2send = 'http://telegra.ph/' + page['path']		
		bot.sendMessage(parse_mode = "Html", text = "<b>" + articleTitle.replace("| FormulaPassion.it","") + "</b>" + "\n" + url2send ,chat_id=MY_CHAT_ID_TELEGRAM)
	except InvalidHTML:
		bot.sendMessage(disable_web_page_preview = True, parse_mode = "Html", text = "<b>Si è verificato un errore nell'elaborare la seguente pagina:</b>\n" + articleUrl ,chat_id=MY_CHAT_ID_TELEGRAM)
		#printWarning("[!]" + articleUrl )

def checkFeed():
	global allUrl
	entries = feedparser.parse('http://formulapassion.it/feed/').entries
	for i in reversed(range(len(entries))):
		url = entries[ i ].link
		if url not in allUrl:
			html = urlopen( url ).read()
			bsObj = BeautifulSoup( html, "html.parser" )
			articleImage = bsObj.findAll("meta",{"property":"og:image"})[0].attrs["content"]
			articleTitle = bsObj.findAll("meta",{"property":"og:title"})[0].attrs["content"]#.decode('utf-8')
			articleDescription = bsObj.findAll("meta",{"property":"og:description"})[0].attrs["content"]
			articleUrl = bsObj.findAll("meta",{"property":"og:url"})[0].attrs["content"]
			#print articleUrl
			articleContent = bsObj.findAll("div",{"class":"entry-content"})[0]
			[section.extract() for section in articleContent.findAll('section')]
			[div.extract() for div in articleContent.findAll('div')]
			[span.extract() for span in articleContent.findAll('span')]
			[script.extract() for script in articleContent.findAll('script')]
			[noscript.extract() for noscript in articleContent.findAll('noscript')]
			[iframe.extract() for iframe in articleContent.findAll('iframe')]
			[blockquote.extract() for blockquote in articleContent.findAll('blockquote')]
			articleContent = str(articleContent)[27:-6]
			sendTelegraph( articleImage, articleTitle, articleDescription, articleUrl, articleContent )
			allUrl.append( url )
			f = open("log.txt","a")
			f.write(articleUrl + "\n")
			f.close()
	
def main():
	#print "starting app"
	populateAllUrl()
	schedule.every(5).minutes.do( checkFeed )
	while True:
		schedule.run_pending()
		#print "sleeping.."
		time.sleep(60)

main()
