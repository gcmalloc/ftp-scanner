== Description ==
A simple ftp scanner with a webinterface written in jQuery. Written for and mainly at The rmll2012.

== Use ==
Launch the daemon :
    
Then launch the server, using gunicorn or the apache WSGI.

== database component ==
You can also have a look at the example.json in the root directory.

ip:{string (v4,v6}
host:{string}
status:{UP, DOWN}
check_last:{epoch, UTC}
up_number:{unsi int}
down_number:{}
ping
