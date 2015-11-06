#!/usr/bin/env python

import webapp2
import urllib
import json
import urllib2
import logging

from google.appengine.api import urlfetch
from google.appengine.api import taskqueue
from google.appengine.api import mail

import app_config

def exists(name,create_folder=False):
    try:
        url = "https://api.dropboxapi.com/1/metadata/auto/%s" % urllib.pathname2url(name)
    
        result = urlfetch.fetch(url=url,
            headers={'Authorization': 'Bearer %s' % app_config.token})

        if result.status_code == 404:
            if create_folder:
                url = "https://api.dropboxapi.com/1/fileops/create_folder"        
                form_data = urllib.urlencode({"root" : "auto", "path" : name})
                result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST,
                    headers={'Authorization': 'Bearer %s' % app_config.token})
        
                if result.status_code == 200:
                    return True
                else:
                    return False
            else:
                return False
        return True
    except Exception as e:
        logging.exception('Unexpected checking exists %s' % name)
        return False

def move(src_path,dest_path):
    try:
        url = "https://api.dropboxapi.com/1/fileops/move"
        form_data = urllib.urlencode({"root" : "auto", "from_path" : src_path, "to_path" : dest_path})
        result = urlfetch.fetch(url=url, payload=form_data, method=urlfetch.POST,
            headers={'Authorization': 'Bearer %s' % app_config.token})
        if result.status_code == 200:
            return True
        else:
            logging.error('Unable to move %s to %s - status code: %d' % (src_path, dest_path, result.status_code))
            logging.error(result.content)
            return False
    except Exception as e:
        logging.exception('Unexpected error moving %s to %s' % (src_path,dest_path))
        return False
        
def download(path):
    url = "https://content.dropboxapi.com/1/files/auto/%s" % urllib.pathname2url(path)

    try:
      req = urllib2.Request(url)
      req.add_header('Authorization','Bearer %s' % app_config.token)
      resp = urllib2.urlopen(req)
      return resp
    except urllib2.URLError, e:
        logging.exception('Error downloading %s' % path)
        return None
        
def send_mail(name,data):
    try:
        mail.send_mail(sender=app_config.sender_email,
                       to= app_config.destination_email,
                       subject=name,
                       body="Receipt Attached",
                       attachments=[(name, data.read())])
        return True
    except Exception as e:
        logging.exception('Unexpected error in sending mail')
        return False
      
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.status = 204

class ScanHandler(webapp2.RequestHandler):
    def get(self):
        resp_json = {'files' : [], 'status' : 'success'}
        try:
            url = "https://api.dropboxapi.com/1/metadata/auto/?list=true"
            result = urlfetch.fetch(url=url,
                headers={'Authorization': 'Bearer %s' % app_config.token})
            if result.status_code == 200:
              metadata = json.loads(result.content)
              if metadata['contents']:
                  for content in metadata['contents']:
                      if content:
                          if not content['is_dir']:
                              resp_json['files'].append(content['path'])
                              # Add the task to the default queue.
                              taskqueue.add(url='/worker', params={'path': content['path'][1:]})
            self.response.status = 200
        except Exception as e:
            logging.error('Error while scanning for new files')
            self.response.status = 500
            resp_json['status'] = 'failure'
        
        self.response.write(json.dumps(resp_json))

class JobHandler(webapp2.RequestHandler):
    def post(self):
        try:
            path = self.request.get('path')
            if exists(app_config.sent_folder,True):
                if exists(path):
                    ba = download(path)
                    if ba:
                        if send_mail(path, ba):
                            move(path,"%s/%s" % (app_config.sent_folder, path))
                        else:
                            self.response.status = 500
                            return
                    else:
                        self.response.status = 500
                        return
                else:
                    logging.error('Path %s not found - unable to continue' % path)
            else:
                logging.error('Sent folder %s does not exist and unable to create it' % app_config.sent_folder)
            
            self.response.status = 204
        except Exception as e:
            logging.exception('Unexpected error in worker type: %s' % type(e))

            self.response.status = 500

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/scan', ScanHandler),
    ('/worker', JobHandler)
], debug=True)
