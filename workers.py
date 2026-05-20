import json
import os
import urllib.error
import urllib.request
from typing import List, Optional


# ─────────────────────────────────────────── constants ────────────────────────────────────────────

SLOTS_PER_DAY = 96  # 24 hours x 4 quarter-hours

# Ordered list of all 15-minute time strings for one day
FULL_TIMES: List[str] = [ f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45) ]


# ═══════════════════════════════════════════ FUNCTIONS ════════════════════════════════════════════

"""
Fetches and returns the data for a given date (yyyy-mm-dd) using the e.on API.
Data format:
[
	{ "dateTime": "2026-04-04T00:00:00.000+02:00", "value": "58.73", "definitive": true },
	...
]
"""
def fetchData(url:str, date:str) -> dict:
	try:
		print()
		request = urllib.request.Request(url+date)
		request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36')
		with urllib.request.urlopen(request, timeout=30) as response:
			if response.status == 200:
				content = response.read().decode('utf-8')
				return	json.loads(content)
			else:
				print(f"[HTTP {response.status}]")
	except urllib.error.HTTPError as e:	print(f"[HTTP Error {e.code}] {e.reason}")
	except urllib.error.URLError  as e:	print(f"[URL Error] {e.reason}")
	except Exception			  as e:	print(f"[Error] {str(e)}")
	return {}


"""
 Returns sample data for testing. The format is the same as for fetchData

"""
def	fetchData_sample(sampleNumber:int) -> dict:
	base_dir= os.path.dirname(os.path.abspath(__file__))
	dates = ['2026-04-03', '2026-04-04']
	date  = dates[sampleNumber-1]
	input_path  = os.path.join(base_dir, f"{date}.json")
	with open(input_path, "r", encoding="utf-8") as fh:
		records = json.load(fh)
	return {'date': date, 'records': records}


"""
Reads prices.json (array of objects with dateTime, value, definitive),
fills all 96 fifteen-minute slots of the day ordered by time and using:
  - linear interpolation across contiguous inner gaps
  - flat extrapolation for leading / trailing gaps
Rounds prices to at most 2 decimals.
Output format:
{
	"prices": [ 12.34, 15.32, ... ],	# exactly 96 items
	"added":  [ 8, 9, 16, ... ]			# indexes of extrapolated slots
}
"""
def processData(records:List[dict]) -> List[dict]:

	#──────────────────────────────────────────────────────────
	def to_float(val) -> Optional[float]:
		try:
			return float(val)
		except (TypeError, ValueError):
			return None
	#──────────────────────────────────────────────────────────

	"""
	Return None immediately on empty records
	"""
	if not records:
		return None

	"""
	----- PARSE INPUT -----
	Build an ordered list of 96 Optional[float] slots from the raw records.
	Slots with no matching record remain None.
	"""
	time_index = {t: i for i, t in enumerate(FULL_TIMES)}
	slots = [None] * SLOTS_PER_DAY

	for rec in records:
		time = rec.get('dateTime') or rec.get('datetime') or ''
		if not time:
			continue
		hm = time[11:16]
		if hm is None or hm not in time_index:
			continue
		price = to_float(rec.get('value'))
		if price is None:
			continue
		slots[time_index[hm]] = price

	"""
	----- INTERPOLATE -----
	Fill None prices:
	  - linear interpolation between two known neighbors (inner gaps)
	  - flat extrapolation from the nearest known value (leading / trailing gaps)
	Returns a plain list of float (length == SLOTS_PER_DAY).
	"""
	filled = [None] * SLOTS_PER_DAY

	known = [i for i, v in enumerate(slots) if v is not None]
	if not known:
		return filled

	# Copy known values
	for i in known:
		filled[i] = float(slots[i])   # type: ignore[arg-type]

	# Flat extrapolation – leading and trailing gaps
	for i in range(0, known[0]):
		filled[i] = filled[known[0]]
	for i in range(known[-1] + 1, SLOTS_PER_DAY):
		filled[i] = filled[known[-1]]

	# Linear interpolation – inner gaps
	for a, b in zip(known, known[1:]):
		gap = b - a
		if gap <= 1:
			continue
		v_a, v_b = filled[a], filled[b]
		for k in range(1, gap):
			filled[a + k] = v_a + (v_b - v_a) * k / gap

	"""
	Round prices and collect the indexes of added/extrapolated slots.
	"""
	result = []
	for i, t in enumerate(FULL_TIMES):
		price = round(filled[i], 2)
		added = slots[i] is None
		result.append({"time": t, "price": price, "added": added})
	return result

# ════════════════════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
	# print(fetchData_sample(1))
	# print(fetchData_sample(2))
	# data = fetchData('https://eonepapirun.azurewebsites.net/api/getSpotPrices?priceArea=SE4&date=', '2026-04-29')
	# print(data)
	# print(processData(data))
	pass


