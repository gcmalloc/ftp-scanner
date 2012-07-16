##ftp-scanner
###Description
A ftp scanner with a webinterface written in jQuery. Entirely compatible with python 3000. Written for and mainly at The rmll2012.

##Use

1. Start the mysql server and change the config accordingly.
2. Change the ip range accord to your will.
3. Launch the scanner process :
     `python scanner/scanner.py`

4. Then launch the server, using gunicorn or the apache WSGI. Or just the test server with :
     `python app/app.py`

##Dependencies
* python3.1 or greater
* Bottle
* oursql
* netaddr

#protocol
You can also have a look at the example.json in the root directory.

ip:{string (v4,v6}
host:{string}
status:{UP, DOWN}
check_last:{epoch, UTC}
up_number:{unsi int}
down_number:{}
ping
