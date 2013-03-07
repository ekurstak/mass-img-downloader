import urllib, urllib2, sys, os, time
from bs4 import BeautifulSoup, SoupStrainer

class MassDownloader:

	img_list = []
	link_history = []
	# words that filter the image urls
	# (if a word in this array is found in an image url, it wont be downloaded)
	excludes = ['thumbs', 'thumb']


	def __init__(self, base_url, limit):
		if 'https' in base_url:
			self.proto = 'https://'
			self.base = base_url[8:]
		else:
			self.proto = 'http://'
			self.base = base_url[7:]
		self.limit = limit
		self.startTime = time.time()

	def printStats(self):
		print """ # of images downloaded: """, len(self.img_list)
		print """ # of pages visited:     """, len(self.link_history)
		print """ Total time elapsed:     """, (time.time() - self.startTime)

	def validateURL(self, url):
		if self.proto not in url:
			if self.base not in url:
				print "1"
				if url[0] == '/':
					url = self.proto + self.base + url
				else:
					url = self.proto + self.base + '/' + url
			else:
				url = self.proto + url
		return url

	def downloadImg(self, url ):
		parts = url.split('/')
		imgName = parts[-1]
		website = parts[2]
		path = os.path.join(website , imgName)
		if not os.path.exists(website):
			os.makedirs(website)
		urllib.urlretrieve(url, path)
		print 'Downloaded: ', imgName

	def downloadAll(self):
		for image in self.img_list:
			self.downloadImg(image)

	def crawl(self, url, depth):
		if ( (depth == 0) or (len(self.img_list) >= int(self.limit)) ):
			return 0
		if url in self.link_history:
			pass
		else:
			self.link_history.append(url)
			print """ Read:  """, url
			# Download page contents and beautify it

			page_data = urllib2.urlopen(url)
			soup = BeautifulSoup(page_data.read(), 'lxml')

			# Grab all image data and download images

			images = soup.findAll('img')
			for i in images:
				imgLink = self.validateURL(i['src'])
				if any(word in imgLink for word in self.excludes):
					pass
				else:
					if imgLink not in self.img_list:
						self.img_list.append(imgLink)
						print len(self.img_list), '/', self.limit
					else:
						pass
					#self.downloadImg(imgLink)

			# Get all link data and build links for the next pages

			links = soup.findAll('a')
			for link in links:
				if self.base not in link['href']:
					pass
				else:
					plink = self.validateURL(link['href'])
					if plink not in self.link_history:
						self.crawl(plink, depth-1)
					else:
						pass



mid = MassDownloader(sys.argv[1], sys.argv[2])
mid.crawl(sys.argv[1], -1)
mid.downloadAll()
mid.printStats()