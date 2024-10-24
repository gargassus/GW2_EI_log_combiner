#    This file contains the configuration for computing the detailed top stats in arcdps logs as parsed by Elite Insights.
#    Copyright (C) 2024 John Long (Drevarr)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


import config
import gzip
import json

# Top stats dictionary to store combined log data
top_stats = config.top_stats

team_colors = config.team_colors

# Buff and skill data collected from al logs
buff_data = {}
skill_data = {}
damage_mod_data = {}
high_scores = {}
personal_damage_mod_data = {
	"total": [],
}
personal_buff_data = {}

players_running_healing_addon = []

def determine_log_type_and_extract_fight_name(fight_name: str) -> tuple:
	"""
	Determine if the log is a PVE or WVW log and extract the fight name.

	If the log is a WVW log, the fight name is extracted after the " - " delimiter.
	If the log is a PVE log, the original fight name is returned.

	Args:
		fight_name (str): The name of the fight.

	Returns:
		tuple: A tuple containing the log type and the extracted fight name.
	"""
	if "Detailed WvW" in fight_name:
		# WVW log
		log_type = "Detailed WVW"
		fight_name = fight_name.split(" - ")[1]
	elif "World vs World" in fight_name:
		# WVW log
		log_type = "WvW"
		fight_name = fight_name.split(" - ")[1]
	else:
		# PVE log
		log_type = "PVE"
	return log_type, fight_name


def update_high_score(stat: str, key: str, value: float) -> None:

	if stat not in high_scores:
		high_scores[stat] = {}
	if len(high_scores[stat]) < 5:
		high_scores[stat][key] = value
	elif value > min(high_scores[stat].values()):
		lowest_key = min(high_scores[stat], key=high_scores[stat].get)
		del high_scores[stat][lowest_key]
		high_scores[stat][key] = value


def determine_player_role(player: dict) -> str:
	crit_rate = player["statsAll"][0]["criticalRate"]
	total_damage = player["dpsAll"][0]["damage"]
	power_damage = player["dpsAll"][0]["powerDamage"]
	condi_damage = player["dpsAll"][0]["condiDamage"]
	if 'extHealingStats' in player:
		total_healing = player["extHealingStats"]["outgoingHealing"][0]["healing"]
	else:
		total_healing = 0
	if 'extBarrierStats' in player:
		total_barrier = player["extBarrierStats"]["outgoingBarrier"][0]["barrier"]
	else:
		total_barrier = 0

	if total_healing > total_damage:
		return "Support"
	if total_barrier > total_damage:
		return "Support"
	if condi_damage > power_damage:
		return "Condi"
	if crit_rate <= 40:
		return "Support"
	else:
		return "DPS"


#get_max_hits(player['targetDamageDist'], skill_map, name_prof)
def get_max_hits(targetDamageDist: dict, skill_data: dict, buff_map: dict, name: str, profession: str) -> None:
	"""
	Get the maximum damage hit by skill.

	Args:
		fight_data (dict): The fight data.

	"""
	for target in targetDamageDist:
		for skill in target[0]:
			max_hit = skill["max"]
			skill_id = skill["id"]
			if f"s{skill_id}" in skill_data:
				skill_name = skill_data[f"s{skill_id}"]['name']
			elif f"b{skill_id}" in buff_map:
				skill_name = buff_map[f"b{skill_id}"]['name']
			else:
				continue

			update_high_score(
				"max_hits",
				"{{"+profession+"}}"+name+" | "+f"{skill_name}",
				f"{max_hit:,}"
				)


def get_total_shield_damage(fight_data: dict) -> int:
	"""
	Extract the total shield damage from the fight data.

	Args:
		fight_data (dict): The fight data.

	Returns:
		int: The total shield damage.
	"""
	total_shield_damage = 0
	for skill in fight_data["targetDamageDist"]:
		total_shield_damage += skill["shieldDamage"]
	return total_shield_damage


def get_buffs_data(buff_map: dict) -> None:
	"""
	Collect buff data across all fights.

	Args:
		buff_map (dict): The dictionary of buff data.
	"""
	for buff in buff_map:
		buff_id = buff[1:]
		name = buff_map[buff]['name']
		stacking = buff_map[buff]['stacking']
		icon = buff_map[buff]['icon']
		if buff_id not in buff_data:
			buff_data[buff_id] = {
				'name': name,
				'stacking': stacking,
				'icon': icon
			}
		

def get_skills_data(skill_map: dict) -> None:
	"""
	Collect skill data across all fights.

	Args:
		skill_map (dict): The dictionary of skill data.
	"""
	for skill in skill_map:
		skill_id = skill[1:]
		name = skill_map[skill]['name']
		auto_attack = skill_map[skill]['autoAttack']
		icon = skill_map[skill]['icon']
		if skill_id not in skill_data:
			skill_data[skill_id] = {
				'name': name,
				'auto': auto_attack,
				'icon': icon
			}


def get_damage_mods_data(damage_mod_map: dict, personal_damage_mod_data: dict) -> None:
	"""
	Collect damage mod data across all fights.

	Args:
		damage_mod_map (dict): The dictionary of damage mod data.
	"""
	for mod in damage_mod_map:
		name = damage_mod_map[mod]['name']
		icon = damage_mod_map[mod]['icon']
		incoming = damage_mod_map[mod]['incoming']
		shared = False
		if mod in personal_damage_mod_data['total']:
			shared = False

		else:
			shared = True

		if mod not in damage_mod_data:
			damage_mod_data[mod] = {
				'name': name,
				'icon': icon,
				'shared': shared,
				'incoming': incoming
			}


def get_personal_mod_data(personal_damage_mods: dict) -> None:
	for profession, mods in personal_damage_mods.items():
		if profession not in personal_damage_mod_data:
			personal_damage_mod_data[profession] = []
		for mod_id in mods:
			mod_id = "d"+str(mod_id)
			if mod_id not in personal_damage_mod_data[profession]:
				personal_damage_mod_data[profession].append(mod_id)
				personal_damage_mod_data['total'].append(mod_id)


def get_enemies_by_fight(fight_num: int, targets: dict) -> None:
	"""
	Organize targets by enemy for a fight.

	Args:
		fight_num (int): The number of the fight.
		targets (list): The list of targets in the fight.
	"""
	if fight_num not in top_stats["fight"]:
		top_stats["fight"][fight_num] = {}

	for target in targets:
		if target["isFake"]:
			continue

		top_stats["fight"][fight_num]["enemy_count"] += 1

		team = target["teamID"]

		if team in team_colors:
			team = "enemy_" + team_colors[team]
		else:
			team = "enemy_Unk"

		if team not in top_stats["fight"][fight_num]:
			# Create a new team if it doesn't exist
			top_stats["fight"][fight_num][team] = 0

		top_stats["fight"][fight_num][team] += 1


def get_enemy_downed_and_killed_by_fight(fight_num: int, targets: dict, players: dict, log_type: str) -> None:
	"""
	Count enemy downed and killed for a fight.

	Args:
		fight_num (int): The number of the fight.
		targets (list): The list of targets in the fight.
	"""
	enemy_downed = 0
	enemy_killed = 0

	if fight_num not in top_stats["fight"]:
		top_stats["fight"][fight_num] = {}

	if log_type != "WVW":  # WVW doesn't have target[defense] data, must be "Detailed WvW" or "PVE"
		for target in targets:
			if target["isFake"]:
				continue

			if target['defenses'][0]['downCount']:
				enemy_downed += target['defenses'][0]['downCount']
			if target['defenses'][0]['deadCount']:
				enemy_killed += target['defenses'][0]['deadCount']
	else:
			for player in players:
				enemy_downed += sum(enemy[0]['downed'] for enemy in player['statsTargets'])
				enemy_killed += sum(enemy[0]['killed'] for enemy in player['statsTargets'])
	
	top_stats["fight"][fight_num]["enemy_downed"] = enemy_downed
	top_stats["fight"][fight_num]["enemy_killed"] = enemy_killed
	top_stats['overall']['enemy_downed'] = top_stats['overall'].get('enemy_downed', 0) + enemy_downed
	top_stats['overall']['enemy_killed'] = top_stats['overall'].get('enemy_killed', 0) + enemy_killed


def get_parties_by_fight(fight_num: int, players: list) -> None:
	"""
	Organize players by party for a fight.

	Args:
		fight_num (int): The number of the fight.
		players (list): The list of players in the fight.
	"""
	if fight_num not in top_stats["parties_by_fight"]:
		top_stats["parties_by_fight"][fight_num] = {}

	for player in players:
		if player["notInSquad"]:
			# Count players not in a squad
			top_stats["fight"][fight_num]["non_squad_count"] += 1
			continue
		top_stats["fight"][fight_num]["squad_count"] += 1
		group = player["group"]
		name = player["name"]
		if group not in top_stats["parties_by_fight"][fight_num]:
			# Create a new group if it doesn't exist
			top_stats["parties_by_fight"][fight_num][group] = []
		if name not in top_stats["parties_by_fight"][fight_num][group]:
			# Add the player to the group
			top_stats["parties_by_fight"][fight_num][group].append(name)


def get_stat_by_key(fight_num: int, player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Add player stats by key to top_stats dictionary

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	for stat, value in player[stat_category][0].items():
		top_stats['player'][name_prof][stat_category][stat] = top_stats['player'][name_prof][stat_category].get(stat, 0) + value
		top_stats['fight'][fight_num][stat_category][stat] = top_stats['fight'][fight_num][stat_category].get(stat, 0) + value
		top_stats['overall'][stat_category][stat] = top_stats['overall'][stat_category].get(stat, 0) + value


def get_stat_by_target_and_skill(fight_num: int, player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Add player stats by target and skill to top_stats dictionary

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	for target in player[stat_category]:
		if target[0]:
			for skill in target[0]:
				skill_id = skill['id']

				if skill_id not in top_stats['player'][name_prof][stat_category]:
					top_stats['player'][name_prof][stat_category][skill_id] = {}
				if skill_id not in top_stats['fight'][fight_num][stat_category]:
					top_stats['fight'][fight_num][stat_category][skill_id] = {}
				if skill_id not in top_stats['overall'][stat_category]:
					top_stats['overall'][stat_category][skill_id] = {}
					
				for stat, value in skill.items():
					if stat == 'max':
						update_high_score(f"{stat_category}_{stat}", f"{name_prof}|{skill_id}", value)
					if stat != 'id':
						top_stats['player'][name_prof][stat_category][skill_id][stat] = top_stats['player'][name_prof][stat_category][skill_id].get(
							stat, 0) + value
						top_stats['fight'][fight_num][stat_category][skill_id][stat] = top_stats['fight'][fight_num][stat_category][skill_id].get(
							stat, 0) + value
						top_stats['overall'][stat_category][skill_id][stat] = top_stats['overall'][stat_category][skill_id].get(stat, 0) + value


def get_stat_by_target(fight_num: int, player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Add player stats by target to top_stats dictionary

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	if stat_category not in top_stats['player'][name_prof]:
		top_stats['player'][name_prof][stat_category] = {}

	for target in player[stat_category]:
		if target[0]:
			for stat, value in target[0].items():
				top_stats['player'][name_prof][stat_category][stat] = top_stats['player'][name_prof][stat_category].get(stat, 0) + value
				top_stats['fight'][fight_num][stat_category][stat] = top_stats['fight'][fight_num][stat_category].get(stat, 0) + value
				top_stats['overall'][stat_category][stat] = top_stats['overall'][stat_category].get(stat, 0) + value


def get_stat_by_skill(fight_num: int, player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Add player stats by skill to top_stats dictionary

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	for skill in player[stat_category][0]:
		if skill:
			skill_id = skill['id']
			if skill_id not in top_stats['player'][name_prof][stat_category]:
				top_stats['player'][name_prof][stat_category][skill_id] = {}
			if skill_id not in top_stats['fight'][fight_num][stat_category]:
				top_stats['fight'][fight_num][stat_category][skill_id] = {}
			if skill_id not in top_stats['overall'][stat_category]:
				top_stats['overall'][stat_category][skill_id] = {}

			for stat, value in skill.items():
				if stat != 'id':
					top_stats['player'][name_prof][stat_category][skill_id][stat] = top_stats['player'][name_prof][stat_category][skill_id].get(stat, 0) + value
					top_stats['fight'][fight_num][stat_category][skill_id][stat] = top_stats['fight'][fight_num][stat_category][skill_id].get(stat, 0) + value
					top_stats['overall'][stat_category][skill_id][stat] = top_stats['overall'][stat_category][skill_id].get(stat, 0) + value


def get_buff_uptimes(fight_num: int, player: dict, stat_category: str, name_prof: str, fight_duration: int, active_time: int) -> None:
	"""
	Calculate buff uptime stats for a player

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
		fight_duration (int): The duration of the fight in milliseconds.
		active_time (int): The duration of the player's active time in milliseconds.

	Returns:
		None
	"""
	for buff in player[stat_category]:
		buff_id = buff['id']
		buff_uptime_ms = buff['buffData'][0]['uptime'] * fight_duration / 100
		buff_presence = buff['buffData'][0]['presence']

		if buff_id not in top_stats['player'][name_prof][stat_category]:
			top_stats['player'][name_prof][stat_category][buff_id] = {}
		if buff_id not in top_stats['fight'][fight_num][stat_category]:
			top_stats['fight'][fight_num][stat_category][buff_id] = {}
		if buff_id not in top_stats['overall'][stat_category]:
			top_stats['overall'][stat_category][buff_id] = {}

		if stat_category == 'buffUptimes':
			stat_value = buff_presence * fight_duration / 100 if buff_presence else buff_uptime_ms
		elif stat_category == 'buffUptimesActive':
			stat_value = buff_presence * active_time / 100 if buff_presence else buff_uptime_ms

		top_stats['player'][name_prof][stat_category][buff_id]['uptime_ms'] = top_stats['player'][name_prof][stat_category][buff_id].get('uptime_ms', 0) + stat_value
		top_stats['fight'][fight_num][stat_category][buff_id]['uptime_ms'] = top_stats['fight'][fight_num][stat_category][buff_id].get('uptime_ms', 0) + stat_value
		top_stats['overall'][stat_category][buff_id]['uptime_ms'] = top_stats['overall'][stat_category][buff_id].get('uptime_ms', 0) + stat_value


def get_target_buff_data(fight_num: int, player: dict, targets: dict, stat_category: str, name_prof: str) -> None:
	"""
	Calculate buff uptime stats for a target caused by squad player

	Args:
		filename (str): The filename of the fight.
		player (dict): The player dictionary.
		targets (dict): The targets dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
		fight_duration (int): The duration of the fight in milliseconds.

	Returns:
		None
	"""
	for target in targets:
		if 'buffs' in target:
			for buff in target['buffs']:
				buff_id = buff['id']

				if player['name'] in buff['statesPerSource']:
					name = player['name']
					buffTime = 0
					buffOn = 0
					firstTime = 0
					conditionTime = 0
					appliedCounts = 0
					for stateChange in buff['statesPerSource'][name]:
						if stateChange[0] == 0:
							continue
						elif stateChange[1] >=1 and buffOn == 0:
							if stateChange[1] > buffOn:
								appliedCounts += 1
							buffOn = stateChange[1]
							firstTime = stateChange[0]

						elif stateChange[1] == 0 and buffOn:
							buffOn = 0
							secondTime = stateChange[0]
							buffTime = secondTime - firstTime
					conditionTime += buffTime

					#if buff_id not in top_stats['player'][name_prof][stat_category]:
					if buff_id not in top_stats['player'][name_prof][stat_category]:
						top_stats['player'][name_prof][stat_category][buff_id] = {
							'generated': 0,
							'applied_counts': 0,
						}
					if buff_id not in top_stats['fight'][fight_num][stat_category]:
						top_stats['fight'][fight_num][stat_category][buff_id] = {
							'generated': 0,
							'applied_counts': 0,
						}
					if buff_id not in top_stats['overall'][stat_category]:
						top_stats['overall'][stat_category][buff_id] = {
							'generated': 0,
							'applied_counts': 0,
						}

					top_stats['player'][name_prof][stat_category][buff_id]['generated'] += conditionTime
					top_stats['player'][name_prof][stat_category][buff_id]['applied_counts'] += appliedCounts

					top_stats['fight'][fight_num][stat_category][buff_id]['generated'] += conditionTime
					top_stats['fight'][fight_num][stat_category][buff_id]['applied_counts'] += appliedCounts

					top_stats['overall'][stat_category][buff_id]['generated'] += conditionTime
					top_stats['overall'][stat_category][buff_id]['applied_counts'] += appliedCounts


def get_buff_generation(fight_num: int, player: dict, stat_category: str, name_prof: str, duration: int, buff_data: dict, squad_count: int, group_count: int) -> None:
	"""
	Calculate buff generation stats for a player

	Args:
		fight_num (int): The number of the fight.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
		duration (int): The duration of the fight in milliseconds.
		buff_data (dict): A dictionary of buff IDs to their data.
		squad_count (int): The number of players in the squad.
		group_count (int): The number of players in the group.
	"""
	for buff in player.get(stat_category, []):
		buff_id = str(buff['id'])
		buff_stacking = buff_data[buff_id].get('stacking', False)

		if buff_id not in top_stats['player'][name_prof][stat_category]:
			top_stats['player'][name_prof][stat_category][buff_id] = {}
		if buff_id not in top_stats['fight'][fight_num][stat_category]:
			top_stats['fight'][fight_num][stat_category][buff_id] = {}
		if buff_id not in top_stats['overall'][stat_category]:
			top_stats['overall'][stat_category][buff_id] = {}

		buff_generation = buff['buffData'][0].get('generation', 0)
		buff_wasted = buff['buffData'][0].get('wasted', 0)

		if buff_stacking:
			if stat_category == 'squadBuffs':
				buff_generation *= duration * (squad_count - 1)
				buff_wasted *= duration * (squad_count - 1)
			elif stat_category == 'groupBuffs':
				buff_generation *= duration * (group_count - 1)
				buff_wasted *= duration * (group_count - 1)
			elif stat_category == 'selfBuffs':
				buff_generation *= duration
				buff_wasted *= duration

		else:
			if stat_category == 'squadBuffs':
				buff_generation = (buff_generation / 100) * duration * (squad_count-1)
				buff_wasted = (buff_wasted / 100) * duration * (squad_count-1)
			elif stat_category == 'groupBuffs':
				buff_generation = (buff_generation / 100) * duration * (group_count-1)
				buff_wasted = (buff_wasted / 100) * duration * (group_count-1)
			elif stat_category == 'selfBuffs':
				buff_generation = (buff_generation / 100) * duration
				buff_wasted = (buff_wasted / 100) * duration

				
		top_stats['player'][name_prof][stat_category][buff_id]['generation'] = top_stats['player'][name_prof][stat_category][buff_id].get('generation', 0) + buff_generation
		top_stats['player'][name_prof][stat_category][buff_id]['wasted'] = top_stats['player'][name_prof][stat_category][buff_id].get('wasted', 0) + buff_wasted

		top_stats['fight'][fight_num][stat_category][buff_id]['generation'] = top_stats['fight'][fight_num][stat_category][buff_id].get('generation', 0) + buff_generation
		top_stats['fight'][fight_num][stat_category][buff_id]['wasted'] = top_stats['fight'][fight_num][stat_category][buff_id].get('wasted', 0) + buff_wasted

		top_stats['overall'][stat_category][buff_id]['generation'] = top_stats['overall'][stat_category][buff_id].get('generation', 0) + buff_generation
		top_stats['overall'][stat_category][buff_id]['wasted'] = top_stats['overall'][stat_category][buff_id].get('wasted', 0) + buff_wasted


def get_skill_cast_by_prof_role(active_time: int, player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Add player skill casts by profession and role to top_stats dictionary

	Args:
		'active_time' (int): player active time in milliseconds.
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""

	profession = player['profession']
	role = determine_player_role(player)
	prof_role = f"{profession}-{role}"
	active_time /= 1000
	
	if 'skill_casts_by_role' not in top_stats:
		top_stats['skill_casts_by_role'] = {}

	if prof_role not in top_stats['skill_casts_by_role']:
		top_stats['skill_casts_by_role'][prof_role] = {
			'total': {}
		}

	if name_prof not in top_stats['skill_casts_by_role'][prof_role]:
		top_stats['skill_casts_by_role'][prof_role][name_prof] = {
			'ActiveTime': 0,
			'Skills': {}
		}

	top_stats['skill_casts_by_role'][prof_role][name_prof]['ActiveTime'] += active_time

	for skill in player[stat_category]:
		skill_id = skill['id']
		cast_count = len(skill['skills'])

		if skill_id not in top_stats['skill_casts_by_role'][prof_role][name_prof]['Skills']:
			top_stats['skill_casts_by_role'][prof_role][name_prof]['Skills'][skill_id] = 0
		if skill_id not in top_stats['skill_casts_by_role'][prof_role]['total']:
			top_stats['skill_casts_by_role'][prof_role]['total'][skill_id] = 0

		top_stats['skill_casts_by_role'][prof_role]['total'][skill_id] += cast_count
		top_stats['skill_casts_by_role'][prof_role][name_prof]['Skills'][skill_id] = top_stats['skill_casts_by_role'][prof_role][name_prof]['Skills'].get(skill_id, 0) + cast_count


def get_healStats_data(fight_num: int, player: dict, players: dict, stat_category: str, name_prof: str) -> None:
	"""
	Collect data for extHealingStats and extBarrierStats

	Args:
		fight_num (int): The fight number.
		player (dict): The player dictionary.
		players (dict): The players dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	
	if stat_category == 'extHealingStats' and 'extHealingStats' in player:
		for index, heal_target in enumerate(player[stat_category]['outgoingHealingAllies']):
			heal_target_name = players[index]['name']
			outgoing_healing = heal_target[0]['healing'] - heal_target[0]['downedHealing']
			downed_healing = heal_target[0]['downedHealing']

			#print('Healing', heal_target_name, outgoing_healing, downed_healing)

			if outgoing_healing or downed_healing:

				if 'heal_targets' not in top_stats['player'][name_prof][stat_category]:
					top_stats['player'][name_prof][stat_category]['heal_targets'] = {}

				if heal_target_name not in top_stats['player'][name_prof][stat_category]['heal_targets']:
					top_stats['player'][name_prof][stat_category]['heal_targets'][heal_target_name] = {
						'outgoing_healing': 0,
						'downed_healing': 0
					}

				top_stats['player'][name_prof][stat_category]['outgoing_healing'] = (
					top_stats['player'][name_prof][stat_category].get('outgoing_healing', 0) + outgoing_healing
				)

				top_stats['player'][name_prof][stat_category]['heal_targets'][heal_target_name]['outgoing_healing'] = (
					top_stats['player'][name_prof][stat_category]['heal_targets'][heal_target_name].get('outgoing_healing', 0) + outgoing_healing
				)

				top_stats['fight'][fight_num][stat_category]['outgoing_healing'] = (
					top_stats['fight'][fight_num][stat_category].get('outgoing_healing', 0) + outgoing_healing
				)

				top_stats['overall'][stat_category]['outgoing_healing'] = (
					top_stats['overall'][stat_category].get('outgoing_healing', 0) + outgoing_healing
				)

				top_stats['player'][name_prof][stat_category]['downed_healing'] = (
					top_stats['player'][name_prof][stat_category].get('downed_healing', 0) + downed_healing
				)
				top_stats['player'][name_prof][stat_category]['heal_targets'][heal_target_name]['downed_healing'] = (
					top_stats['player'][name_prof][stat_category]['heal_targets'][heal_target_name].get('downed_healing', 0) + downed_healing
				)
				top_stats['fight'][fight_num][stat_category]['downed_healing'] = (
					top_stats['fight'][fight_num][stat_category].get('downed_healing', 0) + downed_healing
				)
				top_stats['overall'][stat_category]['downed_healing'] = (
					top_stats['overall'][stat_category].get('downed_healing', 0) + downed_healing
				)

	if stat_category == 'extBarrierStats' and 'extBarrierStats' in player:
		for index, barrier_target in enumerate(player[stat_category]['outgoingBarrierAllies']):
			barrier_target_name = players[index]['name']
			outgoing_barrier = barrier_target[0]['barrier']

			if outgoing_barrier:

				if 'barrier_targets' not in top_stats['player'][name_prof][stat_category]:
					top_stats['player'][name_prof][stat_category]['barrier_targets'] = {}

				if barrier_target_name not in top_stats['player'][name_prof][stat_category]['barrier_targets']:
					top_stats['player'][name_prof][stat_category]['barrier_targets'][barrier_target_name] = {
						'outgoing_barrier': 0
					}

				top_stats['player'][name_prof][stat_category]['outgoing_barrier'] = (
					top_stats['player'][name_prof][stat_category].get('outgoing_barrier', 0) + outgoing_barrier
				)

				top_stats['player'][name_prof][stat_category]['barrier_targets'][barrier_target_name]['outgoing_barrier'] = (
					top_stats['player'][name_prof][stat_category]['barrier_targets'][barrier_target_name].get('outgoing_barrier', 0) + outgoing_barrier
				)

				top_stats['fight'][fight_num][stat_category]['outgoing_barrier'] = (
					top_stats['fight'][fight_num][stat_category].get('outgoing_barrier', 0) + outgoing_barrier
				)

				top_stats['overall'][stat_category]['outgoing_barrier'] = (
					top_stats['overall'][stat_category].get('outgoing_barrier', 0) + outgoing_barrier
				)


def get_healing_skill_data(player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Collect data for extHealingStats and extBarrierStats

	Args:
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	if 'alliedHealingDist' in player[stat_category]:
		for heal_target in player[stat_category]['alliedHealingDist']:
			for skill in heal_target[0]:
				skill_id = skill['id']
				hits = skill['hits']
				min_value = skill['min']
				max_value = skill['max']

				if 'skills' not in top_stats['player'][name_prof][stat_category]:
					top_stats['player'][name_prof][stat_category]['skills'] = {}

				if skill_id not in top_stats['player'][name_prof][stat_category]['skills']:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id] = {}

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['hits'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('hits', 0) + hits
				)

				current_min = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('min', 0)
				current_max = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('max', 0)

				if min_value < current_min or current_min == 0:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id]['min'] = min_value
				if max_value > current_max or current_max == 0:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id]['max'] = max_value

				total_healing = skill['totalHealing']
				downed_healing = skill['totalDownedHealing']
				healing = total_healing - downed_healing

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['totalHealing'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('totalHealing', 0) + total_healing
				)

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['downedHealing'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('downedHealing', 0) + downed_healing
				)

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['healing'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('healing', 0) + healing
				)


def get_barrier_skill_data(player: dict, stat_category: str, name_prof: str) -> None:
	"""
	Collect data for extHealingStats and extBarrierStats

	Args:
		player (dict): The player dictionary.
		stat_category (str): The category of stats to collect.
		name_prof (str): The name of the profession.
	"""
	if 'alliedBarrierDist' in player[stat_category]:
		for barrier_target in player[stat_category]['alliedBarrierDist']:
			for skill in barrier_target[0]:
				skill_id = skill['id']
				hits = skill['hits']
				min_value = skill['min']
				max_value = skill['max']

				if 'skills' not in top_stats['player'][name_prof][stat_category]:
					top_stats['player'][name_prof][stat_category]['skills'] = {}

				if skill_id not in top_stats['player'][name_prof][stat_category]['skills']:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id] = {}

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['hits'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('hits', 0) + hits
				)

				current_min = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('min', 0)
				current_max = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('max', 0)

				if min_value < current_min or current_min == 0:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id]['min'] = min_value
				if max_value > current_max or current_max == 0:
					top_stats['player'][name_prof][stat_category]['skills'][skill_id]['max'] = max_value

				total_barrier = skill['totalBarrier']

				top_stats['player'][name_prof][stat_category]['skills'][skill_id]['totalBarrier'] = (
					top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('totalBarrier', 0) + total_barrier
				)


def get_damage_mod_by_player(fight_num: int, player: dict, name_prof: str) -> None:
	mod_list = ["damageModifiers", "damageModifiersTarget", "incomingDamageModifiers", "incomingDamageModifiersTarget"]

	for mod_cat in mod_list:
		if mod_cat in player:

			for modifier in player[mod_cat]:
				if "id" not in modifier:
					continue
				mod_id = "d" + str(modifier['id'])
				mod_hit_count = modifier["damageModifiers"][0]['hitCount']
				mod_total_hit_count = modifier["damageModifiers"][0]['totalHitCount']
				mod_damage_gain = modifier["damageModifiers"][0]['damageGain']
				mod_total_damage = modifier["damageModifiers"][0]['totalDamage']

				if mod_id not in top_stats['player'][name_prof]['damageModifiers']:
					top_stats['player'][name_prof]['damageModifiers'][mod_id] = {}

				top_stats['player'][name_prof]['damageModifiers'][mod_id]['hitCount'] = (
					top_stats['player'][name_prof]['damageModifiers'][mod_id].get('hitCount', 0) + mod_hit_count
				)
				top_stats['player'][name_prof]['damageModifiers'][mod_id]['totalHitCount'] = (
					top_stats['player'][name_prof]['damageModifiers'][mod_id].get('totalHitCount', 0) + mod_total_hit_count
				)
				top_stats['player'][name_prof]['damageModifiers'][mod_id]['damageGain'] = (
					top_stats['player'][name_prof]['damageModifiers'][mod_id].get('damageGain', 0) + mod_damage_gain
				)
				top_stats['player'][name_prof]['damageModifiers'][mod_id]['totalDamage'] = (
					top_stats['player'][name_prof]['damageModifiers'][mod_id].get('totalDamage', 0) + mod_total_damage
				)

				if mod_id not in top_stats['fight'][fight_num]['damageModifiers']:
					top_stats['fight'][fight_num]['damageModifiers'][mod_id] = {}

				top_stats['fight'][fight_num]['damageModifiers'][mod_id]['hitCount'] = (
					top_stats['fight'][fight_num]['damageModifiers'][mod_id].get('hitCount', 0) + mod_hit_count
				)
				top_stats['fight'][fight_num]['damageModifiers'][mod_id]['totalHitCount'] = (
					top_stats['fight'][fight_num]['damageModifiers'][mod_id].get('totalHitCount', 0) + mod_total_hit_count
				)
				top_stats['fight'][fight_num]['damageModifiers'][mod_id]['damageGain'] = (
					top_stats['fight'][fight_num]['damageModifiers'][mod_id].get('damageGain', 0) + mod_damage_gain
				)
				top_stats['fight'][fight_num]['damageModifiers'][mod_id]['totalDamage'] = (
					top_stats['fight'][fight_num]['damageModifiers'][mod_id].get('totalDamage', 0) + mod_total_damage
				)

				if mod_id not in top_stats['overall']['damageModifiers']:
					top_stats['overall']['damageModifiers'][mod_id] = {}

				top_stats['overall']['damageModifiers'][mod_id]['hitCount'] = (
					top_stats['overall']['damageModifiers'][mod_id].get('hitCount', 0) + mod_hit_count
				)
				top_stats['overall']['damageModifiers'][mod_id]['totalHitCount'] = (
					top_stats['overall']['damageModifiers'][mod_id].get('totalHitCount', 0) + mod_total_hit_count
				)
				top_stats['overall']['damageModifiers'][mod_id]['damageGain'] = (
					top_stats['overall']['damageModifiers'][mod_id].get('damageGain', 0) + mod_damage_gain
				)
				top_stats['overall']['damageModifiers'][mod_id]['totalDamage'] = (
					top_stats['overall']['damageModifiers'][mod_id].get('totalDamage', 0) + mod_total_damage
				)


def parse_file(file_path, fight_num):
	json_stats = config.json_stats

	if file_path.endswith('.gz'):
		with gzip.open(file_path, mode="r") as f:
			json_data = json.loads(f.read().decode('utf-8'))
	else:
		json_datafile = open(file_path, encoding='utf-8')
		json_data = json.load(json_datafile)

	if 'usedExtensions' in json_data:
		for extension in json_data['usedExtensions']:
			if extension['name'] == 'Healing Stats':
				players_running_healing_addon = extension['runningExtension']
				break

	players = json_data['players']
	targets = json_data['targets']
	skill_map = json_data['skillMap']
	buff_map = json_data['buffMap']
	damage_mod_map = json_data.get('damageModMap', {})
	personal_buffs = json_data.get('personalBuffs', {})
	personal_damage_mods = json_data.get('personalDamageMods', {})
	fight_date, fight_end, fight_utc = json_data['timeEnd'].split(' ')
	inches_to_pixel = json_data['combatReplayMetaData']['inchToPixel']
	polling_rate = json_data['combatReplayMetaData']['pollingRate']
	upload_link = json_data['uploadLinks'][0]
	fight_duration = json_data['duration']
	fight_duration_ms = json_data['durationMS']
	check_detailed_wvw = json_data['detailedWvW']
	fight_name = json_data['fightName']
	fight_link = json_data['uploadLinks'][0]
	dist_to_com = []


	log_type, fight_name = determine_log_type_and_extract_fight_name(fight_name)


	#Initialize fight_num stats
	top_stats['fight'][fight_num] = {
		'log_type': log_type,
		'fight_name': fight_name,
		'fight_link': fight_link,
		'fight_date': fight_date,
		'fight_end': fight_end,
		'fight_utc': fight_utc,
		'fight_duration': fight_duration,
		'fight_durationMS': fight_duration_ms,
		'commander': "",
		'squad_count': 0,
		'non_squad_count': 0,
		'enemy_downed': 0,
		'enemy_killed': 0,
		'enemy_count': 0,
		'enemy_Red': 0,
		'enemy_Green': 0,
		'enemy_Blue': 0,
		'enemy_Unk': 0,
		'parties_by_fight': {},
	}
	
	#collect player counts and parties
	get_parties_by_fight(fight_num, players)

	get_enemy_downed_and_killed_by_fight(fight_num, targets, players, log_type)

	#collect enemy counts and team colors
	get_enemies_by_fight(fight_num, targets)

	#collect buff data
	get_buffs_data(buff_map)

	#collect skill data
	get_skills_data(skill_map) 

	#collect damage mods data
	get_personal_mod_data(personal_damage_mods)
	get_damage_mods_data(damage_mod_map, personal_damage_mod_data)

	#process each player in the fight
	for player in players:
		# skip players not in squad
		if player['notInSquad']:
			continue


		name = player['name']
		profession = player['profession']
		account = player['account']
		group = player['group']
		group_count = len(top_stats['parties_by_fight'][fight_num][group])
		squad_count = top_stats['fight'][fight_num]['squad_count']
		tag = player['hasCommanderTag']
		team = player['teamID']
		active_time = player['activeTimes'][0]
		name_prof = name + "|" + profession

		if 'guildID' in player:
			guild_id = player['guildID']
		else:
			guild_id = None

		if tag:
			top_stats['fight'][fight_num]['commander'] = name_prof

		if name_prof not in top_stats['player']:
			print('Found new player: '+name_prof)
			top_stats['player'][name_prof] = {
				'name': name,
				'profession': profession,
				'account': account,
				'team': team,
				'guild': guild_id,
				'num_fights': 0,
			}

		#get_max_hits(player['targetDamageDist'], skill_map, buff_map, name, profession)

		# Cumulative group and squad supported counts
		top_stats['player'][name_prof]['num_fights'] = top_stats['player'][name_prof].get('num_fights', 0) + 1
		top_stats['player'][name_prof]['group_supported'] = top_stats['player'][name_prof].get('group_supported', 0) + group_count
		top_stats['player'][name_prof]['squad_supported'] = top_stats['player'][name_prof].get('squad_supported', 0) + squad_count

		#Cumulative fight time  for player, fight and overall    
		top_stats['player'][name_prof]['fight_time'] = top_stats['player'][name_prof].get('fight_time', 0) + fight_duration_ms
		top_stats['fight'][fight_num]['fight_time'] = top_stats['fight'][fight_num].get('fight_time', 0) + fight_duration_ms
		top_stats['overall']['fight_time'] = top_stats['overall'].get('fight_time', 0) + fight_duration_ms

		#Cumulative active time  for player, fight and overall
		top_stats['player'][name_prof]['active_time'] = top_stats['player'][name_prof].get('active_time', 0) + active_time
		top_stats['fight'][fight_num]['active_time'] = top_stats['fight'][fight_num].get('active_time', 0) + active_time
		top_stats['overall']['active_time'] = top_stats['overall'].get('active_time', 0) + active_time

		for stat_cat in json_stats:

			# Initialize dictionaries for player, fight, and overall stats if they don't exist
			top_stats['player'].setdefault(name_prof, {}).setdefault(stat_cat, {})
			top_stats['fight'][fight_num].setdefault(stat_cat, {})
			top_stats['overall'].setdefault(stat_cat, {})

			# format: player[stat_category][0][stat]
			if stat_cat in ['defenses', 'support', 'statsAll']:
				get_stat_by_key(fight_num, player, stat_cat, name_prof)

			# format: player[stat_cat][target][0][skill][stat]
			if stat_cat in ['targetDamageDist']:
				get_stat_by_target_and_skill(fight_num, player, stat_cat, name_prof)

			# format: player[stat_cat][target[0][stat:value]
			if stat_cat in ['dpsTargets', 'statsTargets']:
				get_stat_by_target(fight_num, player, stat_cat, name_prof)

			# format: player[stat_cat][0][skill][stat:value]
			if stat_cat in ['totalDamageTaken']:
				get_stat_by_skill(fight_num, player, stat_cat, name_prof)

			# format: player[stat_cat][buff][buffData][0][stat:value]
			if stat_cat in ['buffUptimes', 'buffUptimesActive']:
				get_buff_uptimes(fight_num, player, stat_cat, name_prof, fight_duration_ms, active_time)

			# format: player[stat_category][buff][buffData][0][generation]
			if stat_cat in ['squadBuffs', 'groupBuffs', 'selfBuffs']:
				get_buff_generation(fight_num, player, stat_cat, name_prof, fight_duration_ms, buff_data, squad_count, group_count)
			if stat_cat in ['squadBuffsActive', 'groupBuffsActive', 'selfBuffsActive']:                
				get_buff_generation(fight_num, player, stat_cat, name_prof, active_time, buff_data, squad_count, group_count)

			# format: player[stat_category][skill][skills][casts]
			if stat_cat == 'rotation' and 'rotation' in player:
				get_skill_cast_by_prof_role(active_time, player, stat_cat, name_prof)

			if stat_cat in ['extHealingStats', 'extBarrierStats']:
				get_healStats_data(fight_num, player, players, stat_cat, name_prof)
				if stat_cat == 'extHealingStats':
					get_healing_skill_data(player, stat_cat, name_prof)
				else:
					get_barrier_skill_data(player, stat_cat, name_prof)

			if stat_cat in ['targetBuffs']:
				get_target_buff_data(fight_num, player, targets, stat_cat, name_prof)

			if stat_cat in ['damageModifiers']:
				get_damage_mod_by_player(fight_num, player, name_prof)
