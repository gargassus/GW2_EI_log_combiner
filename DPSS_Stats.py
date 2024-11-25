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


def calculate_dps_stats(fight_json, fight, players_running_healing_addon, config, combat_time, fight_time):

	fight_ticks = len(fight_json['players'][0]["damage1S"][0])

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

	skip_fight = {}
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']

		if player['notInSquad']:
			skip_fight[player_prof_name] = True
			continue

		if 'dead' in player['combatReplayData'] and len(player['combatReplayData']['dead']) > 0 and (combat_time / fight_time) < 0.4:
			skip_fight[player_prof_name] = True
		else:
			skip_fight[player_prof_name] = False

	squad_damage_per_tick = []
	for fight_tick in range(fight_ticks - 1):
		squad_damage_on_tick = 0
		for player in fight_json['players']:
			player_prof_name = "{{"+player['profession']+"}} "+player['name']
			if skip_fight[player_prof_name]:
				continue
	
			player_damage = damagePS[player_prof_name]
			squad_damage_on_tick += player_damage[fight_tick + 1] - player_damage[fight_tick]
		squad_damage_per_tick.append(squad_damage_on_tick)

	squad_damage_total = sum(squad_damage_per_tick)
	squad_damage_per_tick_ma = moving_average(squad_damage_per_tick, 1)
	squad_damage_ma_total = sum(squad_damage_per_tick_ma)

	CHUNK_DAMAGE_SECONDS = 21
	Ch5CaDamage1S = {}
	UsedOffensiveSiege = {}

	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		if skip_fight[player_prof_name]:
			continue

		DPSStats_prof_name = player_prof_name + " " + player_role	
		if DPSStats_prof_name not in DPSStats:
			DPSStats[DPSStats_prof_name] = {
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
		UsedOffensiveSiege[player_prof_name] = False
			
		player_damage = damagePS[player_prof_name]
		
		DPSStats[DPSStats_prof_name]["duration"] += fight_time
		DPSStats[DPSStats_prof_name]["combatTime"] += combat_time
		DPSStats[DPSStats_prof_name]["Damage_Total"] += player_damage[fight_ticks - 1]
		DPSStats[DPSStats_prof_name]["Squad_Damage_Total"] += squad_damage_total

		for statsTarget in player["statsTargets"]:
			DPSStats[DPSStats_prof_name]["Downs"] += statsTarget[0]['downed']
			DPSStats[DPSStats_prof_name]["Kills"] += statsTarget[0]['killed']

		for damage_dist in player['totalDamageDist'][0]:
			if damage_dist['id'] in siege_skill_ids:
				UsedOffensiveSiege[player_prof_name] = True

		if "minions" in player:	
			for minion in player["minions"]:
				for minion_damage_dist in minion["totalDamageDist"][0]:
					if minion_damage_dist['id'] in siege_skill_ids:
						UsedOffensiveSiege[player_prof_name] = True

		# Coordination_Damage: Damage weighted by coordination with squad
		player_damage_per_tick = [player_damage[0]]
		for fight_tick in range(fight_ticks - 1):
			player_damage_per_tick.append(player_damage[fight_tick + 1] - player_damage[fight_tick])

		player_damage_ma = moving_average(player_damage_per_tick, 1)

		for fight_tick in range(fight_ticks - 1):
			player_damage_on_tick = player_damage_ma[fight_tick]
			if player_damage_on_tick == 0:
				continue

			squad_damage_on_tick = squad_damage_per_tick_ma[fight_tick]
			if squad_damage_on_tick == 0:
				continue

			squad_damage_percent = squad_damage_on_tick / squad_damage_ma_total

			DPSStats[DPSStats_prof_name]["Coordination_Damage"] += player_damage_on_tick * squad_damage_percent * fight.duration

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
						if skip_fight[player_prof_name]:
							continue
						
						DPSStats_prof_name = player_prof_name

						damage_on_target = player["targetDamage1S"][index][0]
						player_damage = damage_on_target[downIndex] - damage_on_target[startIndex]

						DPSStats[DPSStats_prof_name]["Chunk_Damage"][chunk_damage_seconds] += player_damage
						squad_damage_on_target += player_damage

						if chunk_damage_seconds == 5:
							for i in range(startIndex, downIndex):
								Ch5CaDamage1S[player_prof_name][i] += damage_on_target[i + 1] - damage_on_target[i]

					for player in fight_json['players']:
						player_prof_name = "{{"+player['profession']+"}} "+player['name']

						DPSStats_prof_name = player_prof_name

						DPSStats[DPSStats_prof_name]["Chunk_Damage_Total"][chunk_damage_seconds] += squad_damage_on_target

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
							if skip_fight[player_prof_name]:
								continue
							
							DPSStats_prof_name = player_prof_name
							damage_on_target = player["targetDamage1S"][index][0]
							carrion_damage = damage_on_target[dmgEnd] - damage_on_target[dmgStart]

							DPSStats[DPSStats_prof_name]["Carrion_Damage"] += carrion_damage
							total_carrion_damage += carrion_damage

							for i in range(dmgStart, dmgEnd):
								Ch5CaDamage1S[player_prof_name][i] += damage_on_target[i + 1] - damage_on_target[i]

						for player in fight_json['players']:
							player_prof_name = "{{"+player['profession']+"}} "+player['name']
							if skip_fight[player_prof_name]:
								continue
							
							player_role = player_roles[player_prof_name]
							DPSStats_prof_name = player_prof_name + " " + player_role
							DPSStats[DPSStats_prof_name]["Carrion_Damage_Total"] += total_carrion_damage

	# Burst damage: max damage done in n seconds
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		if skip_fight[player_prof_name] or UsedOffensiveSiege[player_prof_name]:
			# Exclude Dragon Banner from Burst stats
			continue

		DPSStats_prof_name = player_prof_name
		player_damage = damagePS[player_prof_name]
		for i in range(1, CHUNK_DAMAGE_SECONDS):
			for fight_tick in range(i, fight_ticks):
				dmg = player_damage[fight_tick] - player_damage[fight_tick - i]
				DPSStats[DPSStats_prof_name]["Burst_Damage"][i] = max(dmg, DPSStats[DPSStats_prof_name]["Burst_Damage"][i])

	# Ch5Ca Burst damage: max damage done in n seconds
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		if skip_fight[player_prof_name] or UsedOffensiveSiege[player_prof_name]:
			# Exclude Dragon Banner from Burst stats
			continue

		DPSStats_prof_name = player_prof_name
		player_damage_ps = Ch5CaDamage1S[player_prof_name]
		player_damage = [0] * len(player_damage_ps)
		player_damage[0] = player_damage_ps[0]
		for i in range(1, len(player_damage)):
			player_damage[i] = player_damage[i - 1] + player_damage_ps[i]
		for i in range(1, CHUNK_DAMAGE_SECONDS):
			for fight_tick in range(i, fight_ticks):
				dmg = player_damage[fight_tick] - player_damage[fight_tick - i]
				DPSStats[DPSStats_prof_name]["Ch5Ca_Burst_Damage"][i] = max(dmg, DPSStats[DPSStats_prof_name]["Ch5Ca_Burst_Damage"][i])
	
	# Track Stacking Buff Uptimes
	damage_with_buff_buffs = ['stability', 'protection', 'aegis', 'might', 'fury', 'resistance', 'resolution', 'quickness', 'swiftness', 'alacrity', 'vigor', 'regeneration']
	for player in fight_json['players']:
		player_prof_name = "{{"+player['profession']+"}} "+player['name']
		if skip_fight[player_prof_name]:
			continue

		player_role = player_roles[player_prof_name]
		DPSStats_prof_name = player_prof_name + " " + player_role
		if DPSStats_prof_name not in stacking_uptime_Table:
			stacking_uptime_Table[DPSStats_prof_name] = {}
			stacking_uptime_Table[DPSStats_prof_name]["account"] = player['account']
			stacking_uptime_Table[DPSStats_prof_name]["name"] = player['name']
			stacking_uptime_Table[DPSStats_prof_name]["profession"] = player['profession']
			stacking_uptime_Table[DPSStats_prof_name]["role"] = player_role
			stacking_uptime_Table[DPSStats_prof_name]["duration_might"] = 0
			stacking_uptime_Table[DPSStats_prof_name]["duration_stability"] = 0
			stacking_uptime_Table[DPSStats_prof_name]["might"] = [0] * 26
			stacking_uptime_Table[DPSStats_prof_name]["stability"] = [0] * 26
			stacking_uptime_Table[DPSStats_prof_name]["firebrand_pages"] = {}
			for buff_name in damage_with_buff_buffs:
				stacking_uptime_Table[DPSStats_prof_name]["damage_with_"+buff_name] = [0] * 26 if buff_name == 'might' else [0] * 2
		  
		player_damage = damagePS[player_prof_name]
		player_damage_per_tick = [player_damage[0]]
		for fight_tick in range(fight_ticks - 1):
			player_damage_per_tick.append(player_damage[fight_tick + 1] - player_damage[fight_tick])

		player_combat_breakpoints = get_combat_time_breakpoints(player)

		for item in player['buffUptimesActive']:
			buffId = int(item['id'])	
			if buffId not in uptime_Buff_Ids:
				continue

			buff_name = uptime_Buff_Ids[buffId]
			if buff_name in damage_with_buff_buffs:
				states = split_boon_states_by_combat_breakpoints(item['states'], player_combat_breakpoints, fight.duration*1000)

				total_time = 0
				for idx, [state_start, state_end, stacks] in enumerate(states):
					if buff_name in ['stability', 'might']:
						uptime = state_end - state_start
						total_time += uptime
						stacking_uptime_Table[DPSStats_prof_name][buff_name][min(stacks, 25)] += uptime

					if buff_name in damage_with_buff_buffs:
						start_sec = state_start / 1000
						end_sec = state_end / 1000

						start_sec_int = int(start_sec)
						start_sec_rem = start_sec - start_sec_int

						end_sec_int = int(end_sec)
						end_sec_rem = end_sec - end_sec_int

						damage_with_stacks = 0
						if start_sec_int == end_sec_int:
							damage_with_stacks = player_damage_per_tick[start_sec_int] * (end_sec - start_sec)
						else:
							damage_with_stacks = player_damage_per_tick[start_sec_int] * (1.0 - start_sec_rem)
							damage_with_stacks += sum(player_damage_per_tick[start_sec_int + s] for s in range(1, end_sec_int - start_sec_int))
							damage_with_stacks += player_damage_per_tick[end_sec_int] * end_sec_rem

						if idx == 0:
							# Get any damage before we have boon states
							damage_with_stacks += player_damage_per_tick[start_sec_int] * (start_sec_rem)
							damage_with_stacks += sum(player_damage_per_tick[s] for s in range(0, start_sec_int))
						if idx == len(states) - 1:
							# leave this as if, not elif, since we can have 1 state which is both the first and last
							# Get any damage after we have boon states
							damage_with_stacks += player_damage_per_tick[end_sec_int] * (1.0 - end_sec_rem)
							damage_with_stacks += sum(player_damage_per_tick[s] for s in range(end_sec_int + 1, len(player_damage_per_tick)))
						elif len(states) > 1 and state_end != states[idx + 1][0]:
							# Get any damage between deaths, this is usually a small amount of condis that are still ticking after death
							next_state_start = states[idx + 1][0]
							next_state_sec = next_state_start / 1000
							next_start_sec_int = int(next_state_sec)
							next_start_sec_rem = next_state_sec - next_start_sec_int

							damage_with_stacks += player_damage_per_tick[end_sec_int] * (1.0 - end_sec_rem)
							damage_with_stacks += sum(player_damage_per_tick[s] for s in range(end_sec_int + 1, next_start_sec_int))
							damage_with_stacks += player_damage_per_tick[next_start_sec_int] * (next_start_sec_rem)

						if buff_name == 'might':
							stacking_uptime_Table[DPSStats_prof_name]["damage_with_"+buff_name][min(stacks, 25)] += damage_with_stacks
						else:
							stacking_uptime_Table[DPSStats_prof_name]["damage_with_"+buff_name][min(stacks, 1)] += damage_with_stacks

				if buff_name in ['stability', 'might']:
					stacking_uptime_Table[DPSStats_prof_name]["duration_"+buff_name] += total_time
					
		if player_prof_name not in FB_Pages:
			FB_Pages[player_prof_name] = {}
			FB_Pages[player_prof_name]["account"] = player['account']
			FB_Pages[player_prof_name]["name"] = player['name']
			FB_Pages[player_prof_name]["fightTime"] = 0
			FB_Pages[player_prof_name]["firebrand_pages"] = {}
					
		# Track Firebrand Buffs
		tome1_skill_ids = ["41258", "40635", "42449", "40015", "42898"]
		tome2_skill_ids = ["45022", "40679", "45128", "42008", "42925"]
		tome3_skill_ids = ["42986", "41968", "41836", "40988", "44455"]
		tome_skill_ids = [
			*tome1_skill_ids,
			*tome2_skill_ids,
			*tome3_skill_ids,
		]

		if player['profession'] == "Firebrand" and "rotation" in player:
			FB_Pages[player_prof_name]["fightTime"] += player['activeTimes'][0]/1000
			for rotation_skill in player['rotation']:
				skill_id = str(rotation_skill['id'])
				if skill_id in tome_skill_ids:
					pages_data = FB_Pages[player_prof_name]["firebrand_pages"]
					pages_data[skill_id] = pages_data.get(skill_id, 0) + len(rotation_skill['skills'])
 
	return DPSStats