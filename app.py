# app.py

from flask import Flask, render_template, request, json         # import flask
import scrapper_amaz

app = Flask(__name__)             # create an app instance

@app.route("/", methods = ['GET', 'POST'])                   # at the end point /
def index():                      # call method hello
  if request.method == 'POST':
    amazon_url = request.form['url']
    try:
      result = scrapper_amaz.main_scrapper(amazon_url)
      if '_id' in result:
        del result['_id']
    except:
      result = 'None'

    return json.dumps(result)

  if request.method == 'GET':
    return render_template('index.html')         # which returns "hello world"

if __name__ == "__main__":        # on running python app.py
    app.run(debug=True)                     # run the flask app