from flask import Flask,render_template, request

app = Flask(__name__)


@app.route('/healthcheck')
def healthcheck():
    print('')
    return "Alive", 200

@app.route('/init')
def initialize():
    print('Initializing...')
    return render_template('index.html')

@app.route('/form')
def test_form():
    return render_template('test-form.html')

@app.route('/form', methods=['POST'])
def test_form_post():
    text = request.form['text']
    processed_text = text.upper()
    msg = "{}".format(processed_text)
    return msg


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000, threaded=True)