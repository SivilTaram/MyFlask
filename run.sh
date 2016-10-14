service nginx stop
pkill gunicorn
gunicorn -w4 -b0.0.0.0:8080 test:app &
service nginx start
