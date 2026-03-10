#!/bin/sh
uvicorn main:app --host 0.0.0.0 --port 50081 &
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
