
# uwl: micro web library for python

### quickstart:

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

