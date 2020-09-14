from model.routing import posters
app = posters()
app.run('0.0.0.0', port=8089, debug=True)
