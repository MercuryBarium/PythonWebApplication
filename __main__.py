from model.routing import posters

backend = posters()


backend.run(debug=True, host='0.0.0.0', port=8089)