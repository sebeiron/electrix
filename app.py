import json # ----
import os
from datetime	import datetime, timedelta
from flask 		import Flask, render_template, send_from_directory
from workers	import fetchData, processData

app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
	time	= datetime.now()
	today	= time.strftime('%Y-%m-%d')
	tomorrow= (time + timedelta(days=1)).strftime('%Y-%m-%d')
	data	= {
		f"{today}"	 : processData(fetchData(today)),
		f"{tomorrow}": processData(fetchData(tomorrow))
	}
	return render_template('electrix.flsk.html', data = json.dumps(data))


@app.route('/data')
def data():
	time	= datetime.now()
	today	= time.strftime('%Y-%m-%d')
	tomorrow= (time + timedelta(days=1)).strftime('%Y-%m-%d')
	data	= {
		f"{today}"	 : processData(fetchData(today)),
		f"{tomorrow}": processData(fetchData(tomorrow))
	}
	return render_template('data.flsk.html', title='Electrix', h1=f'Data fetch from {today} to {tomorrow}', data = json.dumps(data))

@app.route('/health')
def health_check():
	return '{"message":"OK"}'

# ════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)
