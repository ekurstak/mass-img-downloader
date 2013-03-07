import urllib, urllib2, sys, os, time, threading
from collections import deque
from bs4 import BeautifulSoup, SoupStrainer

class DownloadThread(threading.Thread):
	def __init__(self, urls):
		threading.Thread.__init__(self)
		self.base = base
		self.urls = urls
		self.count = 0

	def run(self):
		for link in self.urls:
			parts = link.split('/')
			imgName = parts[-1]
			website = parts[2]

			if (imgName == ''):
				pass
			else:
				path = os.path. join(website , imgName)
				if not os.path.exists(website):
					os.makedirs(website)
				try:
					urllib.urlretrieve(link, path)
					print 'Downloaded: ',  imgName
					self.count += 1
				except:
					pass


class MID:
	img_list = []
	current_links = deque()
	seen_links = []
	download_count = 0
	excludes = ['thumbs', 'thumb', 'video']
	includes = ['img', 'image']

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
		print """"""
		print """++++++++++++++++++++++++++++++++++++++"""
		print """ Downloading finished! """
		print """ # of images downloaded: """, self.download_count
		print """ # of pages visited:     """, len(self.seen_links)
		print """ Total time elapsed:     """, (time.time() - self.startTime)
		print """++++++++++++++++++++++++++++++++++++++"""
		print """"""

	def validateURL(self, url):
		if self.proto not in url:
			if self.base not in url:
				if url[0] == '/':
					url = self.proto + self.base + url
				else:
					url = self.proto + self.base + '/' + url
			else:
				url = self.proto + url
		return url

	def allLegal(self, str):
		illegalcharset = '!@$^*()[]\'\"<>'
		if any(c in str for c in illegalcharset):
			return False
		else:
			return True


	def downloadAll(self):
		print """"""
		print """++++++++++++++++++++++++++++++++++++++"""
		print """ Starting downloads now... Sit Tight. """
		print """ # of images to download: """, len(self.img_list)
		print """++++++++++++++++++++++++++++++++++++++"""
		print """"""
		# I chose to use 2 threads. Could be better, but worked for me.
		imgs_one = self.img_list[:len(self.img_list)/2]
		imgs_two = self.img_list[len(self.img_list)/2:]
		dt1 = DownloadThread(imgs_one)
		dt2 = DownloadThread(imgs_two)
		dt1.start()
		dt2.start()
		dt1.join()
		dt2.join()
		self.download_count = dt1.count + dt2.count

	def crawl(self, url):
		self.current_links.append(url)

		print """"""
		print """++++++++++++++++++++++++++++++++++++++"""
		print """ Starting to crawl website... """
		print """ Base URL: """, url
		print """++++++++++++++++++++++++++++++++++++++"""
		print """"""

		while self.current_links:

			# Get current working url and check if it hasnt already been seen

			curl = self.current_links.popleft()

			if curl in self.seen_links:
				print """ Already seen....  """, curl
				pass
			else:
				# Download and parse webpage
				print """ Reading: """, curl
				try:
					page_data = urllib2.urlopen(curl)
					soup = BeautifulSoup(page_data.read(), 'lxml')
				except:
					page_data = "<html></html>"
					soup = BeautifulSoup(page_data, 'lxml')
					pass

				# Get all link data and build links for the next pages

				links = soup.findAll('a')
				for link in links:
					if ( (self.base not in link['href']) and (link['href'][0] != '/') ):
						pass
					else:
						plink = self.validateURL(link['href'])
						if ( (plink in self.seen_links) or (plink in self.current_links) ):
							pass
						else:
							self.current_links.append(plink)

				# Get all image links and add to storage

				images = soup.findAll('img')
				for i in images:
					if (len(self.img_list) >= int(self.limit)):
						self.current_links.clear()
						pass
					imgLink = self.validateURL(i['src'])
					if any(word in imgLink for word in self.excludes):
						pass
					else:
						if ( (imgLink not in self.img_list) and ('http' in imgLink[:4]) and (self.base in imgLink) and (self.allLegal(imgLink)) ):
							self.img_list.append(imgLink)
						else:
							pass

				self.seen_links.append(curl)



mid = MID(sys.argv[1], sys.argv[2])
mid.crawl(sys.argv[1])
mid.downloadAll()
mid.printStats()