import math
DPSStats = {}

def moving_average(data, window_size):
	num_elements = len(data)
	ma = []
	for n in range(num_elements):
		min_tick = max(n - window_size, 0)
		max_tick = min(n + window_size, num_elements - 1)
		sub_data = data[min_tick:max_tick + 1]
		ma.append(sum(sub_data) / len(sub_data))

	return ma

def calculate_dps_stats(fight_json):

	fight_ticks = len(fight_json['players'][0]["damage1S"][0])
	duration = round(fight_json['durationMS']/1000)

	damagePS = {}
	for index, target in enumerate(fight_json['targets']):
		if 'enemyPlayer' in target and target['enemyPlayer'] == True:
			for player in fight_json['players']:
				player_prof_name  = "{{"+player['profession']+"}} "+player['name']		
				if player_prof_name  not in damagePS:
					damagePS[player_prof_name ] = [0] * fight_ticks

				damage_on_target = player["targetDamage1S"][index][0]
				for i in range(fight_ticks):
					damagePS[player_prof_name ][i] += damage_on_target[i]

	squad_damage_per_tick = []
	for fight_tick in range(fight_ticks - 1):
		squad_damage_on_tick = 0
		for player in fight_json['players']:
			player_prof_name = "{{"+player['profession']+"}} "+player['name']
			player_damage = damagePS[player_prof_name]
			squad_damage_on_tick += player_damage[fight_tick + 1] - player_damage[fight_tick]
		squad_damage_per_tick.append(squad_damage_on_tick)

	squad_damage_total = sum(squad_damage_per_tick)
	squad_damage_per_tick_ma = calculate_moving_average(squad_damage_per_tick, 1)
	squad_damage_ma_total = sum(squad_damage_per_tick_ma)

	CHUNK_DAMAGE_SECONDS = 21
	Ch5CaDamage1S = {}

	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		combat_time = round(sum_breakpoints(get_combat_time_breakpoints(player)) / 1000)
		if player_prof_name not in DPSStats:
			DPSStats[player_prof_name] = {
				"account": player["account"],
				"name": player["name"],
				"profession": player["profession"],
				"duration": 0,
				"combatTime": 0,
				"coordinationDamage": 0,
				"chunkDamage": [0] * CHUNK_DAMAGE_SECONDS,
				"chunkDamageTotal": [0] * CHUNK_DAMAGE_SECONDS,
				"carrionDamage": 0,
				"carrionDamageTotal": 0,
				"damageTotal": 0,
				"squadDamageTotal": 0,
				"burstDamage": [0] * CHUNK_DAMAGE_SECONDS,
				"ch5CaBurstDamage": [0] * CHUNK_DAMAGE_SECONDS,
				"downs": 0,
				"kills": 0,
			}
			
			
		Ch5CaDamage1S[player_prof_name] = [0] * fight_ticks
			
		player_damage = damagePS[player_prof_name]
		
		DPSStats[player_prof_name]["duration"] += duration
		DPSStats[player_prof_name]["combatTime"] += combat_time
		DPSStats[player_prof_name]["Damage_Total"] += player_damage[fight_ticks - 1]
		DPSStats[player_prof_name]["Squad_Damage_Total"] += squad_damage_total

		for statsTarget in player["statsTargets"]:
			DPSStats[player_prof_name]["Downs"] += statsTarget[0]['downed']
			DPSStats[player_prof_name]["Kills"] += statsTarget[0]['killed']

		# Coordination_Damage: Damage weighted by coordination with squad
		player_damage_per_tick = [player_damage[0]]
		for fight_tick in range(fight_ticks - 1):
			player_damage_per_tick.append(player_damage[fight_tick + 1] - player_damage[fight_tick])

		player_damage_ma = calculate_moving_average(player_damage_per_tick, 1)

		for fight_tick in range(fight_ticks - 1):
			player_damage_on_tick = player_damage_ma[fight_tick]
			if player_damage_on_tick == 0:
				continue

			squad_damage_on_tick = squad_damage_per_tick_ma[fight_tick]
			if squad_damage_on_tick == 0:
				continue

			squad_damage_percent = squad_damage_on_tick / squad_damage_ma_total

			DPSStats[player_prof_name]["Coordination_Damage"] += player_damage_on_tick * squad_damage_percent * duration

	# Chunk damage: Damage done within X seconds of target down
	for index, target in enumerate(fight_json['targets']):
		if 'enemyPlayer' in target and target['enemyPlayer'] == True and 'combatReplayData' in target and len(target['combatReplayData']['down']):
			for chunk_damage_seconds in range(1, CHUNK_DAMAGE_SECONDS):
				targetDowns = dict(target['combatReplayData']['down'])
				for targetDownsIndex, (downKey, downValue) in enumerate(targetDowns.items()):
					downIndex = math.ceil(downKey / 1000)
					startIndex = max(0, math.ceil(downKey / 1000) - chunk_damage_seconds)
					if targetDownsIndex > 0:
						lastDownKey, lastDownValue = list(targetDowns.items())[targetDownsIndex - 1]
						lastDownIndex = math.ceil(lastDownKey / 1000)
						if lastDownIndex == downIndex:
							# Probably an ele in mist form
							continue
						startIndex = max(startIndex, lastDownIndex)

					squad_damage_on_target = 0
					for player in fight_json['players']:
						player_prof_name = "{{"+player['profession']+"}} "+player['name']	
						damage_on_target = player["targetDamage1S"][index][0]
						player_damage = damage_on_target[downIndex] - damage_on_target[startIndex]

						DPSStats[player_prof_name]["Chunk_Damage"][chunk_damage_seconds] += player_damage
						squad_damage_on_target += player_damage

						if chunk_damage_seconds == 5:
							for i in range(startIndex, downIndex):
								Ch5CaDamage1S[player_prof_name][i] += damage_on_target[i + 1] - damage_on_target[i]

					for player in fight_json['players']:
						player_prof_name = "{{"+player['profession']+"}} "+player['name']

						DPSStats[player_prof_name]["Chunk_Damage_Total"][chunk_damage_seconds] += squad_damage_on_target

	# Carrion damage: damage to downs that die 
	for index, target in enumerate(fight_json['targets']):
		if 'enemyPlayer' in target and target['enemyPlayer'] == True and 'combatReplayData' in target and len(target['combatReplayData']['dead']):
			targetDeaths = dict(target['combatReplayData']['dead'])
			targetDowns = dict(target['combatReplayData']['down'])
			for deathKey, deathValue in targetDeaths.items():
				for downKey, downValue in targetDowns.items():
					if deathKey == downValue:
						dmgEnd = math.ceil(deathKey / 1000)
						dmgStart = math.ceil(downKey / 1000)

						total_carrion_damage = 0
						for player in fight_json['players']:
							player_prof_name = "{{"+player['profession']+"}} "+player['name']
							damage_on_target = player["targetDamage1S"][index][0]
							carrion_damage = damage_on_target[dmgEnd] - damage_on_target[dmgStart]

							DPSStats[player_prof_name]["Carrion_Damage"] += carrion_damage
							total_carrion_damage += carrion_damage

							for i in range(dmgStart, dmgEnd):
								Ch5CaDamage1S[player_prof_name][i] += damage_on_target[i + 1] - damage_on_target[i]

						for player in fight_json['players']:
							player_prof_name = "{{"+player['profession']+"}} "+player['name']
							DPSStats[player_prof_name]["Carrion_Damage_Total"] += total_carrion_damage

	# Burst damage: max damage done in n seconds
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		player_damage = damagePS[player_prof_name]
		for i in range(1, CHUNK_DAMAGE_SECONDS):
			for fight_tick in range(i, fight_ticks):
				dmg = player_damage[fight_tick] - player_damage[fight_tick - i]
				DPSStats[player_prof_name]["Burst_Damage"][i] = max(dmg, DPSStats[player_prof_name]["Burst_Damage"][i])

	# Ch5Ca Burst damage: max damage done in n seconds
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		player_damage_ps = Ch5CaDamage1S[player_prof_name]
		player_damage = [0] * len(player_damage_ps)
		player_damage[0] = player_damage_ps[0]
		for i in range(1, len(player_damage)):
			player_damage[i] = player_damage[i - 1] + player_damage_ps[i]
		for i in range(1, CHUNK_DAMAGE_SECONDS):
			for fight_tick in range(i, fight_ticks):
				dmg = player_damage[fight_tick] - player_damage[fight_tick - i]
				DPSStats[player_prof_name]["Ch5Ca_Burst_Damage"][i] = max(dmg, DPSStats[player_prof_name]["Ch5Ca_Burst_Damage"][i])
	
					 
