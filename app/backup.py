"""
Use Dropbox to backup the database every six hours, or import to backup a specific file on demand
"""

import os
import posixpath
import time

from dropbox.client import DropboxClient, ErrorResponse
from config import DevelopmentConfig
from app import db

def backup(filename):
	"""
	Backs up a specified file
	"""
	token = DevelopmentConfig.dropbox_app_token
	client = DropboxClient(token)
	f = open(filename, 'rb')
	dropbox_filename = '/' + filename
	response = client.put_file(dropbox_filename, f, overwrite=True)
	return "uploaded:", response
	


if __name__ == '__main__':
	# backup_file = db.database_name
	while True:
		os.system("pg_dump -Ft gage_web > gage_web.tar")
		backup('gage_web.tar')
		time.sleep(21600) # backup every 6 hours