from flask import Flask, request, redirect, make_response, jsonify
from model.matlista import basicusermanager
from public.view import get_html
import json
config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)

d       = backend.getOrders('marcus.brulls@gmail.com')
