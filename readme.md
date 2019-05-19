
# uwl: micro web library for python

### quickstart:

- clone repo to your project
- copy `uwsgi.ini` file from the repo
- create python file for your webapp. eg: `mywebapp.py`
- use import in your application: `from uwl import route, wsgi`.
- change lines in `uwsgi.ini` to your desired values:
  eg: `module = mywebapp:wsgi.app` and of course where your app resides, change `chdir` to it.
- put ini file to where uwsgi expects or directly run it with uwsgi.
- if you dont have nginx config yet, use example in `nginx.conf`
- goto `localhost` in your browser

there is example working version in container `pvtmert/uwl`
you also can use `docker build -t uwl . && docker run --rm -itp 80:80 uwl`

### caveats:

- `route.py` is not well written, just adds stuff to internal routing table (ordered-dict)
- somehow your scripts needs to be parsed, function names actually does not matter and you can use them over-and-over again.
- i tried to be as much as flexible
- some return values and handling needs to be fixed. proper errors etc.

### example:

project; `/home/mert/projects/myapp`:
- `main.py`:
  ```
  from uwl import wsgi, route

  @route.set(None, r"^/$")
  def main(env, match, *args, **kwargs):
      return (200, {}, "hello, use /test.txt for example")

  @route.set(None, r"^/(.+)$")
  def static(env, match, *args, **kwargs):
      try:
          with open("static/" + match.group()[0]) as file:
              return (200, {}, file.read())
      except Exception as exc:
          return (200, {}, "Error: {}".format(exc))
  ```

- `uwl/`: this library cloned here
- `static/`: static files, i created `test.txt` with content `hello` here.

uwsgi config; `/etc/uwsgi/apps-enabled/myapp.ini`: comment out py-autoreload in production!
```
[uwsgi]

module = main:wsgi.app
chdir = /home/mert/projects/myapp
processes = 4
master = true
vacuum = true

py-autoreload = 2
```

nginx config; `/etc/nginx/sites-enabled/myapp.conf`:
```
server {
	listen 80 default_server;
	location / {
		include uwsgi_params;
		uwsgi_pass unix:/run/uwsgi/app/myapp/socket;
	}
}
```
