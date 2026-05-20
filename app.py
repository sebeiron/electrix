import json # ----
import os
from datetime	import datetime, timedelta
from flask 		import Flask, url_for, render_template, send_from_directory
from workers	import fetchData, processData, fetchData_sample

app = Flask(__name__)

url	= 'https://eonepapirun.azurewebsites.net/api/getSpotPrices?priceArea=SE4&date='


@app.route('/favicon.ico')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/deprecated')
def index_deprecated():
	links = ''
	for item in os.listdir():
		name = item.lower()
		if name.endswith('.py'):
			links += f'<p><a href="{name[:-3]}" title="">{name[:-3]}</a></p>\n'
	return render_template('basic.flsk.html', title=f"{__name__} Root", h1='Pages lists', body=links)


@app.route('/')
def index():
	links = ''
	for rule in app.url_map.iter_rules():
		try:
			if "GET" in rule.methods:
				url = url_for(rule.endpoint, **(rule.defaults or {}))
				links += f'<p><a href="{url}" title="">{rule.endpoint}</a></p>\n'
		except Exception:
			pass
	return render_template('basic.flsk.html', title=f"{__name__} Root", body=f'<h1>Pages lists\n</h1>{links}')


@app.route('/data')
def data():
	time	= datetime.now()
	today	= time.strftime('%Y-%m-%d')
	tomorrow= (time + timedelta(days=1)).strftime('%Y-%m-%d')
	data	= {
		f"{today}"	 : processData(fetchData(url, today)),
		f"{tomorrow}": processData(fetchData(url, tomorrow))
	}
	return render_template('data.flsk.html', title='Electrix', h1=f'Data fetch from {today} to {tomorrow}', data = json.dumps(data))


@app.route('/data-test')
def data_test():
	data1 = fetchData_sample(1)
	data2 = fetchData_sample(2)
	data  = {
		f"{data1['date']}": processData(data1['records']),
		f"{data2['date']}": processData(data2['records'])
	}
	return render_template('data.flsk.html', title='Electrix', h1=f'Data fetch from {data1['date']} to {data2['date']}', data = json.dumps(data))


@app.route('/electrix')
def electrix():
	time	= datetime.now()
	today	= time.strftime('%Y-%m-%d')
	tomorrow= (time + timedelta(days=1)).strftime('%Y-%m-%d')
	data	= {
		f"{today}"	 : processData(fetchData(url, today)),
		f"{tomorrow}": processData(fetchData(url, tomorrow))
	}
	return render_template('electrix.flsk.html', data = json.dumps(data))

# ════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
	app.run(host='localhost', port=8080, debug=True)
