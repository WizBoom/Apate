#!/bin/bash
gunicorn -t 300 -b 127.0.0.1:3000 auth:FlaskApplication
