import datetime
import logging
import os
import webapp2
import cgi

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

###############################################################################
# We'll just use this convenience function to retrieve and render a template.
def render_template(handler, templatename, templatevalues={}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)


###############################################################################
# We'll use this convenience function to retrieve the current user's email.
def get_user_email():
  result = None
  user = users.get_current_user()
  if user:
    result = user.email()
    return result

###############################################################################
class MainPageHandler(webapp2.RequestHandler):
  def get(self):
    user_email = get_user_email()
    if user_email:
      tasks = get_tasks()
      page_params = {
        'tasks': tasks,
        'user_email': user_email
        # 'login_url': users.create_login_url(),
        # 'logout_url': users.create_logout_url('/')
      }
      render_template(self, 'index1.html', page_params)
    else:
       page_params = {
       'login_url': users.create_login_url('/')
       }
       render_template(self, 'login.html', page_params)


class PostPageHandler(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'post_page.html', {})


class PostTaskHandler(webapp2.RequestHandler):
  def post(self):
    task = Task_Model()
    task.title = cgi.escape(self.request.get('title'))
    task.author = "null"
    task.content = cgi.escape(self.request.get('desc'))
    task.category = cgi.escape(self.request.get('category'))
    task._put()
    self.redirect('/')
    # self.response.write(cgi.escape(self.request.get('desc')))
    # self.response.write('</pre></body></html>')

###############################################################################
class TaskDetailHandler(webapp2.RequestHandler):
  def get(self):
    id = self.request.get('id')
    task = get_task(id)
 #   email = get_user_email()
    if task:
      task.comments = task.get_comments()
      task.comment_count = len(task.comments)
      task.count = task.count_votes()
      page_params = {
      # 'user_email': email,
      # 'login_url': users.create_login_url(),
      # 'logout_url': users.create_logout_url('/'),
      'task': task
      }
      render_template(self, 'task_detail.html', page_params)
    else:
      self.redirect('/')

###############################################################################
# models
class Task_Model(ndb.Model):
  title = ndb.StringProperty()
  content = ndb.StringProperty()
  author = ndb.StringProperty()
  category = ndb.StringProperty()
  time_created = ndb.DateTimeProperty(auto_now_add=True)


###############################################################################
# static methods
def get_tasks():
  result = list()
  q = Task_Model.query()
  q = q.order(-Task_Model.time_created)
  for task in q.fetch(100):
    result.append(task)
    return result

###############################################################################
def get_task(task_id):
  return ndb.Key(urlsafe=task_id).get()

mappings = [
  ('/', MainPageHandler),
  ('/post_task', PostTaskHandler),
  # ('/upload', UploadPageHandler),
  # ('/upload_complete', FileUploadHandler),
  # ('/dumb', DumbHandler),
  # ('/notdumb', NotDumbHandler),
  ('/task', TaskDetailHandler),
  ('/post', PostPageHandler)
]

app = webapp2.WSGIApplication(mappings, debug=True)