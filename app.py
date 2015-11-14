"""
Insomnist: Share your Insomnia, on the web.

Check out a demo right here: https://insomnist.herokuapp.com
"""
from datetime import datetime
from html import escape as x
from json import dumps, loads
from os import getenv
from redis import Redis
from string import Template
from urllib.parse import parse_qs, unquote_plus
from uuid import uuid4

# Define a very simple framework
# Decorator that splits between two request handlers by HTTP method
split_get_post = lambda get, post: lambda request: (
    post(request) if request['method'] == 'POST' else get(request))

# Build a request dictionary from the wsgi environment
request = lambda env: {
    'method': env['REQUEST_METHOD'],
    'path': env['PATH_INFO'],
    'data': parse_qs(env['wsgi.input'].read().decode()),
    'query': unquote_plus(env['QUERY_STRING'])}

# Define basic response headers
header = lambda *opts: [('Content-type', 'text/html')] + list(opts)
ok_header = '200', header()
redirect_header = '301', header(('Location', '/'))

# Define routes and routing helpers
routes = {}
routes_add = lambda path, controller: routes.__setitem__(path, controller)
route_request = lambda request: routes[request['path']](request)

# Helps creating template contexts
context = lambda request, **kw: dict(list(request.items()) + list(kw.items()))

# The WSGI compatible application object
app = lambda env, start_response: (start_response(
    # Redirect the client browser on POST requests
    *(redirect_header if env['REQUEST_METHOD'] == 'POST' else ok_header)
) and [route_request(request(env)).encode()])

# DB access via Redis
db = Redis.from_url(getenv('REDIS_URL', 'redis://localhost:6379/'))

# This concludes our framework, which is just a collection of helper utilities.

# Next are the views and controllers for our application.

# Styles and templates
style = """body{width:600px;margin:100px auto;font-family:sans-serif;}
input{width:100%;}
.messages>.datetime{font-size:12px;color:grey;text-align:right;}
"""
base = Template(
    "<html><head><meta charset='utf-8'><style>{}</style></head><body>"
    "$content</body></html>".format(style))

# The index view
index_v = lambda context: base.safe_substitute(content="""
<header><h1>Insomnist?</h1></header>
<section><form action='/' method='POST'>
<input name='message' placeholder='Your Message'><br>
<input type='submit' value='Submit'></form></section>
<section class='messages'><h2>Messages</h2>{messages}</section>""".format(
    messages="<hr>".join([
        "<p>{msg[content]}</p><p class='datetime'>{msg[datetime]}<p>".
        format(msg=msg) for msg in context.get('messages', ())])))

# Models for app
post = lambda content: {'datetime': str(datetime.now()), 'content': content}
post_store = lambda post: db.hset(
    'posts', str(uuid4()), dumps(post))
post_all = lambda: sorted(
    [loads(d.decode()) for d in db.hgetall('posts').values()],
    key=lambda entry: entry['datetime'], reverse=True)

# Controllers for app
index = lambda request: index_v(context(request, messages=post_all()))
add_post = lambda request: request['data'].get('message') and post_store(post(
    x(request['data']['message'][0]))) and ''

# Handle GET and POST for /
routes_add('/', split_get_post(index, add_post))
