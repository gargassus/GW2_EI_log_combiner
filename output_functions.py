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
import json

#list of tid files to output
tid_list = []

def create_new_tid_from_template(
    title: str,
    caption: str,
    text: str,
    tags: list[str] = None,
    modified: str = None,
    created: str = None,
    creator: str = None,
    field: str = None,
    value: str = None,
) -> dict:
    """
    Create a new TID from the template.

    Args:
        title (str): The title of the TID.
        caption (str): The caption of the TID.
        text (str): The text of the TID.
        tags (list[str], optional): The tags for the TID. Defaults to None.
        modified (str, optional): The modified date of the TID. Defaults to None.
        created (str, optional): The created date of the TID. Defaults to None.
        creator (str, optional): The creator of the TID. Defaults to None.
        field (str, optional): The field to add to the TID. Defaults to None.
        value (str, optional): The value to add to the TID. Defaults to None.

    Returns:
        dict: The new TID.
    """
    temp_tid = {}
    temp_tid['title'] = title
    temp_tid['caption'] = caption
    temp_tid['text'] = text
    if tags:
        temp_tid['tags'] = tags
    if modified:
        temp_tid['modified'] = modified
    if created:
        temp_tid['created'] = created
    if creator:
        temp_tid['creator'] = creator
    if field and value:        
        temp_tid[field] = value

    return temp_tid

def append_tid_for_output(input, output):
	output.append(input)
	print(input['title']+'.tid has been created.')

def write_tid_list_to_json(tid_list: list, output_filename: str) -> None:
	"""
	Write the list of tid files to a json file

	Args:
		tid_list (list): The list of tid files.
		output_filename (str): The name of the output file.

	Returns:
		None
	"""
	with open(output_filename, 'w') as outfile:
		json.dump(tid_list, outfile, indent=4, sort_keys=True)

def convert_duration(milliseconds: int) -> str:
	"""
	Convert a duration in milliseconds to a human-readable string.

	Args:
		milliseconds (int): The duration in milliseconds.

	Returns:
		str: A string representing the duration in a human-readable format.
	"""
	seconds, milliseconds = divmod(milliseconds, 1000)
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)

	duration_parts = []
	if days:
		duration_parts.append(f"{days}d")
	if hours:
		duration_parts.append(f"{hours:02}h")
	if minutes:
		duration_parts.append(f"{minutes:02}m")
	duration_parts.append(f"{seconds:02}s {milliseconds:03}ms")

	return " ".join(duration_parts)

def calculate_average_squad_count(fight_data: dict) -> tuple:
	"""
	Calculate the average squad count for a fight.

	Args:
		fight_data (dict): The fight data.

	Returns:
		tuple: The average squad count, average ally count, and average enemy count.
	"""
	total_squad_count = 0
	total_ally_count = 0
	total_enemy_count = 0

	for fight in fight_data:
		total_squad_count += fight["squad_count"]
		total_ally_count += fight["non_squad_count"]
		total_enemy_count += fight["enemy_count"]

	avg_squad_count = total_squad_count / len(fight_data)
	avg_ally_count = total_ally_count / len(fight_data)
	avg_enemy_count = total_enemy_count / len(fight_data)

	return avg_squad_count, avg_ally_count, avg_enemy_count

def extract_gear_buffs_and_skills(buff_data: dict, skill_data: dict) -> tuple:
	"""
	Extract gear buffs and skills from the top stats data.

	Args:
		buff_data (dict): The buff data.
		skill_data (dict): The skill data.

	Returns:
		tuple: A tuple containing a list of gear buff IDs and a list of gear skill IDs.
	"""
	gear_buff_ids = []
	gear_skill_ids = []

	for buff, buff_data in buff_data.items():
		if "Relic of" in buff_data["name"] or "Superior Sigil of" in buff_data["name"]:
			gear_buff_ids.append(buff)

	for skill, skill_data in skill_data.items():
		if "Relic of" in skill_data["name"] or "Superior Sigil of" in skill_data["name"]:
			gear_skill_ids.append(skill)

	return gear_buff_ids, gear_skill_ids

def build_gear_buff_summary(top_stats: dict, gear_buff_ids: list, buff_data: dict, tid_date_time: str) -> str:
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	for buff_id in gear_buff_ids:
		buff_icon = buff_data[buff_id]["icon"]
		buff_name = buff_data[buff_id]["name"]
		header += f" ![img width=24 [{buff_name}|{buff_icon}]] |"
	header += "h"
	rows.append(header)

	for player in top_stats["player"].values():
		fight_time = player["fight_time"]
		profession = "{{"+player["profession"]+"}}"
		row = f"|{player['name']} | {profession} |{player['account'][:30]} | {fight_time/1000:.1f}|"

		for buff_id in gear_buff_ids:
			if buff_id in player["buffUptimes"]:
				buff_uptime_ms = player["buffUptimes"][buff_id]['uptime_ms']
				uptime_pct = f"{((buff_uptime_ms / fight_time) * 100):.2f}%"
			else:
				uptime_pct = " - "

			row += f" {uptime_pct} |"
		rows.append(row)
	rows.append(f"| Gear Buff Uptime Table|c")
	rows.append('\n\n</div>\n\n')
		#push table to tid_list for output
	tid_text = "\n".join(rows)
	temp_title = f"{tid_date_time}-Gear-Buff-Uptimes"

	append_tid_for_output(
		create_new_tid_from_template(temp_title, "Gear Buff Uptimes", tid_text),
		tid_list
		)    

def build_gear_skill_summary(top_stats: dict, gear_skill_ids: list, skill_data: dict, tid_date_time: str) -> str:
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	
	for skill_id in gear_skill_ids:
		skill_icon = skill_data[skill_id]["icon"]
		skill_name = skill_data[skill_id]["name"]
		header += f" ![img width=24 [{skill_name}|{skill_icon}]] |"
	header += "h"
	rows.append(header)

	for player in top_stats["player"].values():
		fight_time = player["fight_time"]
		profession = "{{"+player["profession"]+"}}"
		row = f"|{player['name']} | {profession} |{player['account'][:30]} | {fight_time/1000:.1f}|"

		for skill in gear_skill_ids:
			_skill = int(skill[1:])
			if _skill in player["targetDamageDist"]:
				totalDamage = player["targetDamageDist"][_skill]["totalDamage"]
				connectedHits = player["targetDamageDist"][_skill]["connectedHits"]
				crit = player["targetDamageDist"][_skill]["crit"]
				crit_pct = f"{crit/connectedHits*100:.2f}" if crit > 0 else "0"
				critDamage = player["targetDamageDist"][_skill]["critDamage"]
				tooltip = f"Connected Hits: {connectedHits} <br>Crit: {crit} - ({crit_pct}%) <br>Crit Damage: {critDamage:,.0f}"
				detailEntry = f'<div class="xtooltip"> {totalDamage:,.0f} <span class="xtooltiptext">'+tooltip+'</span></div>'
			else:
				detailEntry = " - "
			row += f" {detailEntry} |"
		rows.append(row)
	rows.append(f"| Gear Skill Damage Table|c")
	rows.append('\n\n</div>\n\n')

	#push table to tid_list for output
	tid_text = "\n".join(rows)
	temp_title = f"{tid_date_time}-Gear-Skill-Damage"

	append_tid_for_output(
		create_new_tid_from_template(temp_title, "Gear Skill Damage", tid_text),
		tid_list
	)

def get_total_shield_damage(fight_data: dict) -> int:
	"""Extract the total shield damage from the fight data.

	Args:
		fight_data (dict): The fight data.

	Returns:
		int: The total shield damage.
	"""
	total_shield_damage = 0
	for skill_id, skill_data in fight_data["targetDamageDist"].items():
		total_shield_damage += skill_data["shieldDamage"]
	return total_shield_damage

def build_tag_summary(top_stats):
	"""Build a summary of tags from the top stats data.

	Args:
		top_stats (dict): The top stats data.

	Returns:
		dict: A dictionary of tag summaries, where the keys are the tag names, and the values are dictionaries with the following keys:

			- num_fights (int): The number of fights for the tag.
			- fight_time (int): The total fight time for the tag in milliseconds.
			- kills (int): The total number of kills for the tag.
			- downs (int): The total number of downs for the tag.
			- downed (int): The total number of times the tag was downed.
			- deaths (int): The total number of deaths for the tag.

	"""
	tag_summary = {}

	for fight, fight_data in top_stats["fight"].items():
		commander = fight_data["commander"]
		if commander not in tag_summary:
			tag_summary[commander] = {
				"num_fights": 0,
				"fight_time": 0,
				"enemy_killed": 0,
				"enemy_downed": 0,
				"squad_downed": 0,
				"squad_deaths": 0,
			}

		tag_summary[commander]["num_fights"] += 1
		tag_summary[commander]["fight_time"] += fight_data["fight_durationMS"]
		tag_summary[commander]["enemy_killed"] += fight_data["enemy_killed"]
		tag_summary[commander]["enemy_downed"] += fight_data["enemy_downed"]
		tag_summary[commander]["squad_downed"] += fight_data["defenses"]["downCount"]
		tag_summary[commander]["squad_deaths"] += fight_data["defenses"]["deadCount"]

	return tag_summary

def output_tag_summary(tag_summary: dict, tid_date_time) -> None:
	"""Output a summary of the tag data in a human-readable format."""
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	rows.append("|thead-dark table-caption-top table-hover sortable|k")
	rows.append("| Summary by Command Tag |c")
	rows.append(
		"| | | | Enemy |<| Squad|<| |h"
	)	
	rows.append(
		"|Name | Prof | Fights | {{DownedEnemy}} | {{killed}} | {{DownedAlly}} | {{DeadAlly}} | KDR |h"
	)
	for tag, tag_data in tag_summary.items():
		name = tag.split("|")[0]
		if len(tag.split("|")) > 1:
			profession = "{{"+tag.split("|")[1]+"}}"
		else:
			profession = ""
		fights = tag_data["num_fights"]
		downs = tag_data["enemy_downed"]
		kills = tag_data["enemy_killed"]
		downed = tag_data["squad_downed"]
		deaths = tag_data["squad_deaths"]
		kdr = kills / deaths if deaths else kills
		rows.append(
			f"|{name} | {profession} | {fights} | {downs} | {kills} | {downed} | {deaths} | {kdr:.2f}|"
		)

		# Sum all tags
		total_fights = sum(tag_data["num_fights"] for tag_data in tag_summary.values())
		total_kills = sum(tag_data["enemy_killed"] for tag_data in tag_summary.values())
		total_downs = sum(tag_data["enemy_downed"] for tag_data in tag_summary.values())
		total_downed = sum(tag_data["squad_downed"] for tag_data in tag_summary.values())
		total_deaths = sum(tag_data["squad_deaths"] for tag_data in tag_summary.values())
		total_kdr = total_kills / total_deaths if total_deaths else total_kills

	rows.append(
		f"|Totals |<| {total_fights} | {total_downs} | {total_kills} | {total_downed} | {total_deaths} | {total_kdr:.2f}|f"
	)
	rows.append("\n\n</div>")

	text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(F"{tid_date_time}-Tag_Stats", "Tag Summary", text),
		tid_list
		)

def build_fight_summary(top_stats: dict, caption: str, tid_date_time : str) -> None:
	"""
	Build a summary of the top stats for each fight.

	Print a table with the following columns:
		- Fight number
		- Date-Time[upload link]
		- End time
		- Duration
		- Squad count
		- Ally count
		- Enemy count
		- R/G/B team count
		- Downs
		- Kills
		- Downed
		- Deaths
		- Damage out
		- Damage in
		- Barrier damage
		- Barrier percentage
		- Shield damage
		- Shield percentage

	Args:
		top_stats (dict): The top_stats dictionary containing the overall stats.
		caption (str): The table caption

	Returns:
		None
	"""
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += f"| {caption} |c\n"
	header += "|# |Fight Link | Duration | Squad | Allies | Enemy | R/G/B | {{DownedEnemy}} | {{killed}} | {{DownedAlly}} | {{DeadAlly}} | {{Damage}} | {{Damage Taken}} | {{damageBarrier}} | {{damageBarrier}} % | {{damageShield}} | {{damageShield}} % |h"

	rows.append(header)

	
	last_fight = 0
	last_end = ""
	total_durationMS = 0
	
	# Calculate average squad count
	avg_squad_count, avg_ally_count, avg_enemy_count = calculate_average_squad_count(top_stats["fight"].values())
	# Get the total downs, deaths, and damage out/in/barrier/shield
	enemy_downed = top_stats['overall']['enemy_downed']
	enemy_killed = top_stats['overall']['enemy_killed']
	squad_down = top_stats['overall']['defenses']['downCount']
	squad_dead = top_stats['overall']['defenses']['deadCount']
	total_damage_out = top_stats['overall']['statsTargets']['totalDmg']
	total_damage_in = top_stats['overall']['defenses']['damageTaken']
	total_barrier_damage = top_stats['overall']['defenses']['damageBarrier']
	total_shield_damage = get_total_shield_damage(top_stats['overall'])
	total_shield_damage_percent = (total_shield_damage / total_damage_out) * 100
	total_barrier_damage_percent = (total_barrier_damage / total_damage_in) * 100

	# Iterate over each fight and build the row
	for fight_num, fight_data in top_stats["fight"].items():
		row = ""
		# Get the total shield damage for this fight
		fight_shield_damage = get_total_shield_damage(fight_data)

		# Abbreviate the fight location
		abbrv=""
		for word in fight_data['fight_name'].split():
			abbrv += word[0]
		# construct the fight link    
		if fight_data['fight_link'] == "":
			fight_link = f"{fight_data['fight_date']} - {fight_data['fight_end']} - {abbrv}"
		else:
			fight_link = f"[[{fight_data['fight_date']} - {fight_data['fight_end']} - {abbrv}|{fight_data['fight_link']}]]"
		
		# Build the row
		damage_taken = fight_data['defenses']['damageTaken'] or 1
		row += f"|{fight_num} |{fight_link} | {fight_data['fight_duration']}| {fight_data['squad_count']} | {fight_data['non_squad_count']} | {fight_data['enemy_count']} "
		row += f"| {fight_data['enemy_Red']}/{fight_data['enemy_Green']}/{fight_data['enemy_Blue']} | {fight_data['statsTargets']['downed']} | {fight_data['statsTargets']['killed']} "
		row += f"| {fight_data['defenses']['downCount']} | {fight_data['defenses']['deadCount']} | {fight_data['statsTargets']['totalDmg']:,}| {fight_data['defenses']['damageTaken']:,}"
		row += f"| {fight_data['defenses']['damageBarrier']:,}| {(fight_data['defenses']['damageBarrier'] / damage_taken * 100):.2f}%| {fight_shield_damage:,}"
		# Calculate the shield damage percentage
		if fight_data['statsTargets']['totalDmg']:
			shield_damage_pct = (fight_shield_damage / fight_data['statsTargets']['totalDmg'] * 100)
		else:
			shield_damage_pct = 0
		row += f"| {shield_damage_pct:.2f}%|"
		# Keep track of the last fight number, end time, and total duration
		last_fight = fight_num
		total_durationMS += fight_data['fight_durationMS']

		rows.append(row)

	raid_duration = convert_duration(total_durationMS)
	# Build the footer
	footer = f"|Total Fights: {last_fight}|<| {raid_duration}| {avg_squad_count:.1f},,avg,,| {avg_ally_count:.1f},,avg,,| {avg_enemy_count:.1f},,avg,,|     | {enemy_downed} | {enemy_killed} | {squad_down} | {squad_dead} | {total_damage_out:,}| {total_damage_in:,}| {total_barrier_damage:,}| {total_shield_damage_percent:.2f}%| {total_shield_damage:,}| {total_barrier_damage_percent:.2f}%|f"
	rows.append(footer)
	rows.append("\n\n</div>")
	# push the table to tid_list

	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption}", "Fight Summary", tid_text),
		tid_list
		)

def build_damage_summary_table(top_stats: dict, caption: str, tid_date_time: str) -> None:
	"""
	Build a damage summary table.

	Args:
		top_stats (dict): The top_stats dictionary containing the overall stats.
		caption (str): The table caption

	Returns:
		None
	"""
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	# Build the table header
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += f"| {caption} |c\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	header += " !{{Target_Damage}} | !{{Target_Damage_PS}} | !{{Target_Power}} | !{{Target_Power_PS}} | !{{Target_Condition}} | !{{Target_Condition_PS}} | !{{Target_Breakbar_Damage}} | !{{All_Damage}}| !{{All_Power}} | !{{All_Condition}} | !{{All_Breakbar_Damage}} |h"

	rows.append(header)

	# Build the table body
	for player, player_data in top_stats["player"].items():
		fighttime = player_data["fight_time"] / 1000
		row = f"|{player_data['name']} |"+" {{"+f"{player_data['profession']}"+"}} "+f"|{player_data['account'][:30]} | {player_data['fight_time'] / 1000:.1f}|"
		row += " {:,}| {:,.0f}| {:,}| {:,.0f}| {:,}| {:,.0f}| {:,}| {:,}| {:,}| {:,}| {:,}|".format(
			player_data["dpsTargets"]["damage"],
			player_data["dpsTargets"]["damage"]/fighttime,
			player_data["dpsTargets"]["powerDamage"],
			player_data["dpsTargets"]["powerDamage"]/fighttime,			
			player_data["dpsTargets"]["condiDamage"],
			player_data["dpsTargets"]["condiDamage"]/fighttime,
			player_data["dpsTargets"]["breakbarDamage"],
			player_data["statsAll"]["totalDmg"],
			player_data["statsAll"]["directDmg"],
			player_data["statsAll"]["totalDmg"] - player_data["statsAll"]["directDmg"],
			player_data["dpsTargets"]["breakbarDamage"],
		)

		rows.append(row)

	# Print the table
	#print(header)
	#print("\n".join(rows))
	rows.append("\n\n</div>")
	#push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption}", caption, tid_text),
		tid_list
		)

def build_category_summary_table(top_stats: dict, category_stats: dict, caption: str, tid_date_time: str) -> None:
	"""
	Print a table of defense stats for all players in the log.

	Args:
		top_stats (dict): The top_stats dictionary containing the overall stats.
		category_stats (dict): A dictionary that maps a category name to a stat name.

	Returns:
		None
	"""
	pct_stats = {
		"criticalRate": "critableDirectDamageCount", "flankingRate":"connectedDirectDamageCount", "glanceRate":"connectedDirectDamageCount", "againstMovingRate": "connectedDamageCount"
	}
	time_stats = ["resurrectTime", "condiCleanseTime", "condiCleanseTimeSelf", "boonStripsTime", "removedStunDuration"]

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	for toggle in ["Total", "Average"]:
		rows.append(f'<$reveal stateTitle=<<currentTiddler>> stateField="radio" type="match" text="{toggle}" animate="yes">\n')
		# Build the table header
		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += "|!Name | !Prof |!Account | !{{FightTime}} |"
		for stat in category_stats:
			header += " !{{"+f"{stat}"+"}} |"
		header += "h"

		rows.append(header)

		# Build the table body
		for player in top_stats["player"].values():
			row = f"|{player['name']} | {{{{{player['profession']}}}}} |{player['account'][:30]} | {player['fight_time'] / 1000:.0f}|"
			fight_time = player["fight_time"] / 1000
			for stat, category in category_stats.items():
				stat_value = player[category].get(stat, 0)

				if stat in pct_stats:
					divisor_value = player[category].get(pct_stats[stat], 0)
					if divisor_value == 0:
						divisor_value = 1
					stat_value_percentage = round((stat_value / divisor_value) * 100, 1)
					stat_value = f"{stat_value_percentage:.2f}%"
				elif stat in time_stats:
					if toggle == "Average":
						stat_value = f"{stat_value/fight_time:.2f}"
					else:
						stat_value = f"{stat_value:,.1f}"
				else:
					if toggle == "Average":
						stat_value = f"{stat_value/fight_time:,.2f}"
					else:
						stat_value = f"{stat_value:,}"
				row += f" {stat_value}|"

			rows.append(row)
		rows.append(f'|<$radio field="radio" value="Total">Total</$radio> - <$radio field="radio" value="Average">Average</$radio> - {caption} Table|c')
		rows.append("\n</$reveal>")

	rows.append("\n\n</div>")
	#push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ', '-')}", caption, tid_text, field="radio", value="Total"),
		tid_list
		)

def build_boon_summary(top_stats: dict, boons: dict, category: str, buff_data: dict, tid_date_time: str) -> None:
	"""Print a table of boon uptime stats for all players in the log."""

	# Build the table header
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	for toggle in ["Total", "Average"]:
		rows.append(f'<$reveal stateTitle=<<currentTiddler>> stateField="radio" type="match" text="{toggle}" animate="yes">\n')

		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += "|!Name | !Prof |!Account | !{{FightTime}} |"
		for boon_id, boon_name in boons.items():
			header += "!{{"+f"{boon_name}"+"}}|"
		header += "h"

		rows.append(header)
		category_caption = {'selfBuffs': "Self Generation", 'groupBuffs': "Group Generation", 'squadBuffs': "Squad Generation", 'totalBuffs': "Total Generation"}
		caption = category_caption[category] or ""

		# Build the table body
		for player in top_stats["player"].values():
			row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:30]} | {player['fight_time'] / 1000:.1f}|"

			for boon_id in boons:
				if boon_id not in player[category]:
					entry = " - "

				else:
					stacking = buff_data[boon_id].get('stacking', False)                
					num_fights = player["num_fights"]
					group_supported = player["group_supported"]
					squad_supported = player["squad_supported"]

					if category == "selfBuffs":
						generation_ms = player[category][boon_id]["generation"]
						if stacking:
							uptime_percentage = round((generation_ms / player['fight_time'] / num_fights), 3)
						else:
							uptime_percentage = round((generation_ms / player['fight_time'] / num_fights) * 100, 3)
					elif category == "groupBuffs":
						generation_ms = player[category][boon_id]["generation"]
						if stacking:
							uptime_percentage = round((generation_ms / player['fight_time']) / (group_supported - num_fights), 3)
						else:
							uptime_percentage = round((generation_ms / player['fight_time']) / (group_supported - num_fights) * 100, 3)
					elif category == "squadBuffs":
						generation_ms = player[category][boon_id]["generation"]
						if stacking:
							uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported - num_fights), 3)
						else:
							uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported - num_fights) * 100, 3)
					elif category == "totalBuffs":
						generation_ms = 0
						if boon_id in player["selfBuffs"]:
							generation_ms += player["selfBuffs"][boon_id]["generation"] 
						if boon_id in player["squadBuffs"]:
							generation_ms += player["squadBuffs"][boon_id]["generation"]
						if stacking:
							uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported), 3)
						else:
							uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported) * 100, 3)
					else:
						raise ValueError(f"Invalid category: {category}")
					
					if stacking:
						if uptime_percentage:
							uptime_percentage = f"{uptime_percentage:.2f}"
						else:
							uptime_percentage = " - "
					else:
						if uptime_percentage:
							uptime_percentage = f"{uptime_percentage:.2f}%"
						else:
							uptime_percentage = " - "
					if toggle == "Total":
						entry = f"{generation_ms/1000:,.1f}"
					else:
						entry = uptime_percentage

				row += f" {entry}|"
			rows.append(row)
		#rows.append(f"|{caption} Table|c")
		rows.append(f'|<$radio field="radio" value="Total">Total Gen</$radio> - <$radio field="radio" value="Average">Uptime Gen</$radio> - {caption} Table|c')
		rows.append("\n</$reveal>")
	rows.append("\n\n</div>")
	#push table to tid_list for output
	tid_text = "\n".join(rows)
	temp_title = f"{tid_date_time}-{caption.replace(' ','-')}"

	append_tid_for_output(
		create_new_tid_from_template(temp_title, caption, tid_text),
		tid_list
		)    

def build_uptime_summary(top_stats: dict, boons: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	"""Print a table of boon uptime stats for all players in the log."""

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	# Build the player table header
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	for boon_id, boon_name in boons.items():
		if boon_id not in buff_data:
			continue
		skillIcon = buff_data[boon_id]["icon"]

		header += f" ![img width=24 [{boon_name}|{skillIcon}]] |"
	header += "h"

	# Build the Squad table rows
	header2 = f"|Squad Average Uptime |<|<|<|"
	for boon_id in boons:
		if boon_id not in buff_data:
			continue
		if boon_id not in top_stats["overall"]["buffUptimes"]:
			uptime_percentage = " - "
		else:
			uptime_ms = top_stats["overall"]["buffUptimes"][boon_id]["uptime_ms"]
			uptime_percentage = round((uptime_ms / top_stats['overall']["fight_time"]) * 100, 3)
			uptime_percentage = f"{uptime_percentage:.3f}%"
		header2 += f" {uptime_percentage}|" 
	header2 += "h"

	rows.append(header)
	rows.append(header2)

	# Build the table body
	for player in top_stats["player"].values():
		row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:30]} | {player['fight_time'] / 1000:.2f}|"
		for boon_id in boons:
			if boon_id not in buff_data:
				continue

			if boon_id not in player["buffUptimes"]:
				uptime_percentage = " - "
			else:
				uptime_ms = player["buffUptimes"][boon_id]["uptime_ms"]
				uptime_percentage = round(uptime_ms / player['fight_time'] * 100, 3)
				uptime_percentage = f"{uptime_percentage:.3f}%"

			row += f" {uptime_percentage}|"
		rows.append(row)
	rows.append(f"|{caption} Table|c")

	rows.append("\n\n</div>")
	#push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}", caption, tid_text),
		tid_list
	)

def build_debuff_uptime_summary(top_stats: dict, boons: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	"""Print a table of boon uptime stats for all players in the log."""

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	# Build the player table header
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	for boon_id, boon_name in boons.items():
		if boon_id not in buff_data:
			continue
		skillIcon = buff_data[boon_id]["icon"]

		header += f"! [img width=24 [{boon_name}|{skillIcon}]] |"
	header += " !Count|"
	header += "h"

	# Build the Squad table rows
	header2 = f"|Average Uptime |<|<|<|"
	applied_counts = 0
	for boon_id in boons:
		if boon_id not in buff_data:
			continue
		if boon_id not in top_stats["overall"]["targetBuffs"]:
			uptime_percentage = " - "
		else:
			applied_counts += top_stats["overall"]["targetBuffs"][boon_id]["applied_counts"]
			uptime_ms = top_stats["overall"]["targetBuffs"][boon_id]["uptime_ms"]
			uptime_percentage = round((uptime_ms / top_stats['overall']["fight_time"] / top_stats['overall']["enemy_count"]) * 100, 3)
			uptime_percentage = f"{uptime_percentage:.3f}%"
		header2 += f" {uptime_percentage}|" 
	header2 += f" {applied_counts}|" 
	header2 += "h"

	rows.append(header)
	rows.append(header2)

	# Build the table body
	for player in top_stats["player"].values():
		row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:32]} | {player['fight_time'] / 1000:.2f}|"
		applied_counts = 0
		for boon_id in boons:
			if boon_id not in buff_data:
				continue

			if boon_id not in player["targetBuffs"]:
				uptime_percentage = " - "
			else:
				applied_counts += player["targetBuffs"][boon_id]["applied_counts"]
				uptime_ms = player["targetBuffs"][boon_id]["uptime_ms"]
				uptime_percentage = round((uptime_ms / player['fight_time'] / player['enemy_engaged_count']) * 100, 3)
				uptime_percentage = f"{uptime_percentage:.3f}%"

			row += f" {uptime_percentage}|"
		row += f" {applied_counts}|"

		rows.append(row)
	rows.append(f"|{caption} Table|c")

	rows.append("\n\n</div>")
	#push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}", caption, tid_text),
		tid_list
	)

def build_healing_summary(top_stats: dict, caption: str, tid_date_time: str) -> None:
	"""Print a table of healing stats for all players in the log running the extension."""

	healing_stats = {}

	for player in top_stats['player'].values():
		if 'extHealingStats' in player or 'extBarrierStats' in player:
			healing_stats[player['name']] = {
				'account': player['account'],
				'profession': player['profession'],
				'fight_time': player['fight_time']
			}

		if 'extHealingStats' in player:
			healing_stats[player['name']]['healing'] = player['extHealingStats'].get('outgoing_healing', 0)
			healing_stats[player['name']]['downed_healing'] = player['extHealingStats'].get('downed_healing', 0)

		if 'extBarrierStats' in player:
			healing_stats[player['name']]['barrier'] = player['extBarrierStats'].get('outgoing_barrier', 0)

	# Sort healing stats by healing amount in descending order
	sorted_healing_stats = sorted(healing_stats.items(), key=lambda x: x[1]['healing'], reverse=True)
	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	# Build the table header
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} | !{{Healing}} | !{{HealingPS}} | !{{Barrier}} | !{{BarrierPS}} | !{{DownedHealing}} | !{{DownedHealingPS}} |h"

	# Build the table body
	rows.append(header)

	for healer in sorted_healing_stats:
		if (healer[1]['healing'] + healer[1]['downed_healing'] + healer[1]['barrier']):
			fighttime = healer[1]['fight_time'] / 1000
			row = f"|{healer[0]} |"+" {{"+f"{healer[1]['profession']}"+"}} "+f"|{healer[1]['account'][:32]} | {fighttime:.2f}|"
			row += f" {healer[1]['healing']:,}| {healer[1]['healing'] / fighttime:,.2f}| {healer[1]['barrier']:,}|"
			row += f"{healer[1]['barrier'] / fighttime:,.2f}| {healer[1]['downed_healing']:,}| {healer[1]['downed_healing'] / fighttime:,.2f}|"
			rows.append(row)
	rows.append(f"|{caption} Table|c")

	rows.append("\n\n</div>")
	# Push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}", caption, tid_text),
		tid_list
	)

def build_personal_damage_modifier_summary(top_stats: dict, personal_damage_mod_data: dict, damage_mod_data: dict, caption: str, tid_date_time: str) -> None:
	"""Print a table of personal damage modifier stats for all players in the log running the extension."""
	for profession in personal_damage_mod_data:
		if profession == 'total':
			continue
		prof_mod_list = personal_damage_mod_data[profession]

		rows = []
		rows.append('<div style="overflow-x:auto;">\n\n')
		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += f"| {caption} |c\n"
		header += "|!Name | !Prof |!Account | !{{FightTime}} |"
		
		for mod_id in prof_mod_list:
			icon = damage_mod_data[mod_id]["icon"]
			name = damage_mod_data[mod_id]["name"]
			header += f"![img width=24 [{name}|{icon}]]|"
		header += "h"

		rows.append(header)

		for player_name, player_data in top_stats['player'].items():
			if player_data['profession'] == profession:
				row = f"|{player_data['name']} | {player_data['profession']} |{player_data['account'][:32]} | {player_data['fight_time'] / 1000:.2f}|"
				for mod in prof_mod_list:
					if mod in player_data['damageModifiers']:
						hit_count = player_data['damageModifiers'][mod]['hitCount']
						total_count = player_data['damageModifiers'][mod]['totalHitCount']
						damage_gain = player_data['damageModifiers'][mod]['damageGain']
						total_damage = player_data['damageModifiers'][mod]['totalDamage']
						damage_pct = damage_gain / total_damage * 100
						hit_pct = hit_count / total_count * 100
						tooltip = f"{hit_count} of {total_count} ({hit_pct:.2f}% hits)<br>Damage Gained: {damage_gain:,}<br>"
						detailEntry = f'<div class="xtooltip"> {damage_pct:.2f}% <span class="xtooltiptext">'+tooltip+'</span></div>'
						row += f" {detailEntry}|"
					else:
						row += f" - |"
				rows.append(row)
		rows.append(f"|{profession} Damage Modifiers Table|c")
		
		rows.append("\n\n</div>")

		# Push table to tid_list for output
		tid_text = "\n".join(rows)

		append_tid_for_output(
			create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}-{profession}", "{{"+f"{profession}"+"}}", tid_text),
			tid_list
		)

def build_shared_damage_modifier_summary(top_stats: dict, damage_mod_data: dict, caption: str, tid_date_time: str) -> None:
	"""Print a table of shared damage modifier stats for all players in the log running the extension."""
	shared_mod_list = []
	for modifier in damage_mod_data:
		if damage_mod_data[modifier]['shared']:
			shared_mod_list.append(modifier)

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += f"| {caption} |c\n"
	header += "|!Name | !Prof |!Account | !{{FightTime}} |"
	for mod_id in shared_mod_list:
		icon = damage_mod_data[mod_id]["icon"]
		name = damage_mod_data[mod_id]["name"]
		header += f"![img width=24 [{name}|{icon}]]|"
	header += "h"

	rows.append(header)

	for player in top_stats['player'].values():
		row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:32]} | {player['fight_time'] / 1000:.2f}|"
		for modifier_id in shared_mod_list:
			if modifier_id in player['damageModifiers']:
				modifier_data = player['damageModifiers'][modifier_id]
				hit_count = modifier_data['hitCount']
				total_count = modifier_data['totalHitCount']
				damage_gain = modifier_data['damageGain']
				total_damage = modifier_data['totalDamage']
				damage_pct = damage_gain / total_damage * 100
				hit_pct = hit_count / total_count * 100
				tooltip = f"{hit_count} of {total_count} ({hit_pct:.2f}% hits)<br>Damage Gained: {damage_gain:,}<br>"
				detail_entry = f'<div class="xtooltip"> {damage_pct:.2f}% <span class="xtooltiptext">{tooltip}</span></div>'
				row += f" {detail_entry}|"
			else:
				row += f" - |"
		rows.append(row)
	rows.append(f"|{caption} Damage Modifiers Table|c")

	rows.append("\n\n</div>")

	# Push table to tid_list for output
	tid_text = "\n".join(rows)

	append_tid_for_output(
		create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}", caption, tid_text),
		tid_list
	)

def build_skill_cast_summary(skill_casts_by_role: dict, skill_data: dict, caption: str, tid_date_time: str) -> None:
	"""
	Print a table of skill cast stats for all players in the log running the extension.
	"""
	for prof_role, cast_data in skill_casts_by_role.items():
		cast_skills = cast_data['total']
		sorted_cast_skills = sorted(cast_skills.items(), key=lambda x: x[1], reverse=True)
		rows = []
		rows.append('<div style="overflow-x:auto;">\n\n')
		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += f"| {caption} |c\n"
		header += "|!Name | !Prof | !{{FightTime}} |"
		i = 0
		for skill, count in sorted_cast_skills:
			if i < 35:
				skill_icon = skill_data[skill]['icon']
				skill_name = skill_data[skill]['name']
				header += f"![img width=24 [{skill_name}|{skill_icon}]]|"
			i+=1
		header += "h"

		rows.append(header)

		for player, player_data in cast_data.items():
			if player == 'total':
				continue

			name, profession = player.split("|")
			profession = "{{" + profession + "}}"
			time_secs = player_data['ActiveTime']
			time_mins = time_secs / 60

			row = f"|{name} |" + " " + f"{profession} " + f"|{time_secs:.2f}|"
			i = 0
			for skill, count in sorted_cast_skills:
				if i < 35:
					if skill in player_data['Skills']:
						row += f" {(player_data['Skills'][skill] / time_mins):.2f}|"
					else:
						row += f" - |"
				i+=1
			rows.append(row)

		rows.append(f"|{caption} / Minute|c")

		rows.append("\n\n</div>")
		# Push table to tid_list for output
		tid_text = "\n".join(rows)
		tid_title = f"{tid_date_time}-{caption.replace(' ','-')}-{prof_role}"
		tid_caption = profession + f" {prof_role.split('-')[1]}"

		append_tid_for_output(
			create_new_tid_from_template(tid_title, tid_caption, tid_text),
			tid_list
		)

def build_combat_resurrection_stats_tid(top_stats: dict, skill_data: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	"""Build a table of combat resurrection stats for all players in the log running the extension."""

	combat_resurrect = {
		'res_skills': {},
		'players': {}
		}

	for player, player_data in top_stats['player'].items():

		if 'skills' in player_data['extHealingStats']:

			prof_name = player_data['profession'] + '|' + player_data['name'] + '|' + str(player_data['fight_time'])

			for skill in player_data['extHealingStats']['skills']:

				if 'downedHealing' in player_data['extHealingStats']['skills'][skill]:
					if player_data['extHealingStats']['skills'][skill]['downedHealing'] > 0:
						downed_healing = player_data['extHealingStats']['skills'][skill]['downedHealing']

						if skill not in combat_resurrect['res_skills']:
							combat_resurrect['res_skills'][skill] = combat_resurrect['res_skills'].get(skill, 0) + downed_healing

						if prof_name not in combat_resurrect['players']:
							combat_resurrect['players'][prof_name] = {}

						combat_resurrect['players'][prof_name][skill] = combat_resurrect['players'].get(skill, 0) + downed_healing

	sorted_res_skills = sorted(combat_resurrect['res_skills'], key=combat_resurrect['res_skills'].get, reverse=True)

	combat_resurrect_tags = f"{tid_date_time}"
	combat_resurrect_title = f"{tid_date_time}-Combat-Resurrect"
	combat_resurrect_caption = f"{caption}"
	combat_resurrect_text = ""

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|thead-dark table-caption-top table-hover sortable|k\n"
	header += "|@@display:block;width:150px;!Name@@ | !Prof | !{{FightTime}} |"
	for skill in sorted_res_skills:
		if skill in skill_data:
			skill_icon = skill_data[skill]['icon']
			skill_name = skill_data[skill]['name']
		elif skill in buff_data:
			skill_icon = buff_data[skill]['icon']
			skill_name = buff_data[skill]['name']
		else:
			skill_icon = "unknown.png"
			skill_name = skill
		header += f" ![img width=24 [{skill} - {skill_name}|{skill_icon}]] |"

	header += "h"

	rows.append(header)

	for player in combat_resurrect['players']:
		profession, name, fight_time = player.split('|')
		time_secs = int(fight_time) / 1000
		profession = "{{" + profession + "}}"

		row = f"|{name} | {profession} | {time_secs:,.1f}|"
		for skill in sorted_res_skills:
			row += f" {combat_resurrect['players'][player].get(skill, 0):,.0f}|"

		rows.append(row)
	rows.append(f"| {caption} |c")
	rows.append('\n\n</div>\n\n')
	combat_resurrect_text = "\n".join(rows)
	append_tid_for_output(
		create_new_tid_from_template(combat_resurrect_title, combat_resurrect_caption, combat_resurrect_text, combat_resurrect_tags),
		tid_list
	)

def build_main_tid(datetime):
	main_created = f"{datetime}"
	main_modified = f"{datetime}"
	main_tags = f"{datetime} Logs"
	main_title = f"{datetime}-Log-Summary"
	main_caption = f"{datetime} - Log Summary"
	main_creator = f"Drevarr@github.com"

	main_text = "{{"+datetime+"-Tag_Stats}}\n\n{{"+datetime+"-Menu}}"

	append_tid_for_output(
		create_new_tid_from_template(main_title, main_caption, main_text, main_tags, main_modified, main_created, main_creator),
		tid_list
	)

def build_menu_tid(datetime: str) -> None:
    """
    Build a TID for the main menu.

    Args:
        datetime (str): The datetime string of the log.

    Returns:
        None
    """
    tags = f"{datetime}"
    title = f"{datetime}-Menu"
    caption = "Menu"
    
    text = (
        f'<<tabs "[[{datetime}-Overview]] [[{datetime}-General-Stats]] [[{datetime}-Buffs]] '
        f'[[{datetime}-Damage-Modifiers]] [[{datetime}-Mechanics]] [[{datetime}-Skill-Usage]] '
        f'[[{datetime}-Minions]] [[{datetime}-High-Scores]] [[{datetime}-Top-Damage-By-Skill]]" '
        f'"{datetime}-Overview" "$:/temp/menutab1">>'
    )

    append_tid_for_output(
        create_new_tid_from_template(title, caption, text, tags, field='radio', value='Total'),
        tid_list
    )


def build_general_stats_tid(datetime):
	"""
	Build a TID for general stats menu.
	"""
	tags = f"{datetime}"
	title = f"{datetime}-General-Stats"
	caption = "General Stats"
	creator = "Drevarr@github.com"
	text = (f"<<tabs '[[{datetime}-Damage]] [[{datetime}-Offensive]] "
			f"[[{datetime}-Defenses]] [[{datetime}-Support]] [[{datetime}-Heal-Stats]] [[{datetime}-Healers]] [[{datetime}-Combat-Resurrect]] [[{datetime}-FB-Pages]]' "
			f"'{datetime}-Offensive' '$:/temp/tab1'>>")

	append_tid_for_output(
		create_new_tid_from_template(title, caption, text, tags, creator=creator, field='radio', value='Total'),
		tid_list
	)

def build_damage_modifiers_menu_tid(datetime: str) -> None:
	"""
	Build a TID for the damage modifiers menu.
	"""

	tags = f"{datetime}"
	title = f"{datetime}-Damage-Modifiers"
	caption = "Damage Modifiers"
	creator = "Drevarr@github.com"

	text = (f"<<tabs '[[{datetime}-Shared-Damage-Mods]] [[{datetime}-Profession_Damage_Mods]]' "
			f"'{datetime}-Shared-Damage-Mods' '$:/temp/tab1'>>")

	append_tid_for_output(
		create_new_tid_from_template(title, caption, text, tags, creator=creator),
		tid_list
	)

def build_buffs_stats_tid(datetime):
	"""
	Build a TID for buffs menu.
	"""
	tags = f"{datetime}"
	title = f"{datetime}-Buffs"
	caption = "Buffs"
	creator = "Drevarr@github.com"

	text = (f"<<tabs '[[{datetime}-Boons]] [[{datetime}-Offensive-Buffs]] [[{datetime}-Support-Buffs]] [[{datetime}-Defensive-Buffs]]"
			f" [[{datetime}-Gear-Buff-Uptimes]] [[{datetime}-Gear-Skill-Damage]]"
			f"[[{datetime}-Conditions-In]] [[{datetime}-Debuffs-In]] [[{datetime}-Conditions-Out]] [[{datetime}-Debuffs-Out]]' "
			f"'{datetime}-Boons' '$:/temp/tab1'>>")

	append_tid_for_output(
		create_new_tid_from_template(title, caption, text, tags, creator=creator),
		tid_list
	)

def build_boon_stats_tid(datetime):
	buff_stats_tags = f"{datetime}"
	buff_stats_title = f"{datetime}-Boons"
	buff_stats_caption = f"Boons"
	buff_stats_creator = f"Drevarr@github.com"

	buff_stats_text = f"<<tabs '[[{datetime}-Uptimes]] [[{datetime}-Self-Generation]] [[{datetime}-Group-Generation]] [[{datetime}-Squad-Generation]]' '{datetime}-Uptimes' '$:/temp/tab1'>>"

	append_tid_for_output(
		create_new_tid_from_template(buff_stats_title, buff_stats_caption, buff_stats_text, buff_stats_tags, creator=buff_stats_creator),
		tid_list
	)

def build_profession_damage_modifier_stats_tid(personal_damage_mod_data: dict, caption: str, tid_date_time: str):

	prof_mod_stats_tags = f"{tid_date_time}"
	prof_mod_stats_title = f"{tid_date_time}-Profession_Damage_Mods"
	prof_mod_stats_caption = f"Profession Damage Modifiers"
	prof_mod_stats_creator = f"Drevarr@github.com"
	prof_mod_stats_text ="<<tabs '"
	tab_name = ""
	for profession in personal_damage_mod_data:
		if  'total' in profession:
			continue
		tab_name = f"{tid_date_time}-{caption.replace(' ','-')}-{profession}"
		prof_mod_stats_text += f'[[{tab_name}]]'
	prof_mod_stats_text += f"' '{tab_name}' '$:/temp/tab1'>>"
	append_tid_for_output(
		create_new_tid_from_template(prof_mod_stats_title, prof_mod_stats_caption, prof_mod_stats_text, prof_mod_stats_tags, creator=prof_mod_stats_creator),
		tid_list
	)   

def build_skill_usage_stats_tid(skill_casts_by_role: dict, caption: str, tid_date_time: str):
	skill_stats_tags = f"{tid_date_time}"
	skill_stats_title = f"{tid_date_time}-Skill-Usage"
	skill_stats_caption = f"{caption}"
	skill_stats_creator = f"Drevarr@github.com"
	skill_stats_text ="<<tabs '"

	for prof_role in skill_casts_by_role:
		tab_name = f"{tid_date_time}-{caption.replace(' ','-')}-{prof_role}"
		skill_stats_text += f'[[{tab_name}]]'
	skill_stats_text += f"' '{tab_name}' '$:/temp/tab1'>>"
	append_tid_for_output(
		create_new_tid_from_template(skill_stats_title, skill_stats_caption, skill_stats_text, skill_stats_tags, creator=skill_stats_creator),
		tid_list
	)

def fmt_firebrand_page_total(page_casts, page_cost, fight_time, page_total):
	output_string = ' <span data-tooltip="'

	if page_cost:
		output_string += "{:.2f}".format(round(100 * page_casts * page_cost / page_total, 4))
		output_string += '% of total pages '
		output_string += "{:.2f}".format(round(60 * page_casts / fight_time, 4))
		output_string += ' casts / minute">'
	else:
		output_string += "{:.2f}".format(round(100 * page_casts / page_total, 4))
		output_string += '% of total pages">'

	if page_cost:
		output_string += "{:.2f}".format(round(60 * page_casts * page_cost / fight_time, 4))
	else:
		output_string += "{:.2f}".format(round(60 * page_casts / fight_time, 4))

	output_string += '</span>|'

	return output_string

def build_fb_pages_tid(fb_pages: dict, caption: str, tid_date_time: str):
	# Firebrand pages
	tome1_skill_ids = ["41258", "40635", "42449", "40015", "42898"]
	tome2_skill_ids = ["45022", "40679", "45128", "42008", "42925"]
	tome3_skill_ids = ["42986", "41968", "41836", "40988", "44455"]

	tome_skill_ids = [
		*tome1_skill_ids,
		*tome2_skill_ids,
		*tome3_skill_ids,
	]

	tome_skill_page_cost = {
		"41258": 1, "40635": 1, "42449": 1, "40015": 1, "42898": 1,
		"45022": 1, "40679": 1, "45128": 1, "42008": 2, "42925": 2,
		"42986": 1, "41968": 1, "41836": 2, "40988": 2, "44455": 2,
	}
	rows = []	
	rows.append('<div style="overflow-x:auto;">\n\n')
	header = "|table-caption-top|k\n"
	header += "|Firebrand page utilization, pages/minute|c\n"
	header += "|thead-dark table-hover sortable|k"
	rows.append(header)

	output_header =  '|!Name '
	output_header += ' | ! <span data-tooltip="Number of seconds player was in squad logs">Seconds</span>'
	output_header += '| !Pages/min| | !T1 {{Tome_of_Justice}}| !C1 {{Chapter_1_Searing_Spell}}| !C2 {{Chapter_2_Igniting_Burst}}| !C3 {{Chapter_3_Heated_Rebuke}}| !C4 {{Chapter_4_Scorched_Aftermath}}| !Epi {{Epilogue_Ashes_of_the_Just}}| | !T2 {{Tome_of_Resolve}} | !C1 {{Chapter_1_Desert_Bloom}}| !C2 {{Chapter_2_Radiant_Recovery}}| !C3 {{Chapter_3_Azure_Sun}}| !C4 {{Chapter_4_Shining_River}}| !Epi {{Epilogue_Eternal_Oasis}}|  | !T3 {{Tome_of_Courage}}| !C1 {{Chapter_1_Unflinching_Charge}}| !C2 {{Chapter_2_Daring_Challenge}}| !C3 {{Chapter_3_Valiant_Bulwark}}| !C4 {{Chapter_4_Stalwart_Stand}}| !Epi {{Epilogue_Unbroken_Lines}}'
	output_header += '|h'
	rows.append(output_header)

	pages_sorted_stacking_uptime_Table = []
	for player_name, player_data in fb_pages.items():

		fight_time = player_data["fightTime"]/1000 or 1

		firebrand_pages = player_data['firebrand_pages']
		all_tomes_total = 0

		for skill_id in tome_skill_ids:
			all_tomes_total += firebrand_pages.get(skill_id, 0) * tome_skill_page_cost[skill_id]

		pages_sorted_stacking_uptime_Table.append([player_name, all_tomes_total / fight_time])
	pages_sorted_stacking_uptime_Table = sorted(pages_sorted_stacking_uptime_Table, key=lambda x: x[1], reverse=True)
	pages_sorted_stacking_uptime_Table = list(map(lambda x: x[0], pages_sorted_stacking_uptime_Table))

	for player_name in pages_sorted_stacking_uptime_Table:
		name = fb_pages[player_name]['name']
		fight_time = fb_pages[player_name]["fightTime"]/1000 or 1
		firebrand_pages = fb_pages[player_name]['firebrand_pages']

		tome1_total = 0
		for skill_id in tome1_skill_ids:
			tome1_total += firebrand_pages.get(skill_id, 0) * tome_skill_page_cost[skill_id]

		tome2_total = 0
		for skill_id in tome2_skill_ids:
			tome2_total += firebrand_pages.get(skill_id, 0) * tome_skill_page_cost[skill_id]
	
		tome3_total = 0
		for skill_id in tome3_skill_ids:
			tome3_total += firebrand_pages.get(skill_id, 0) * tome_skill_page_cost[skill_id]
	
		all_tomes_total = tome1_total + tome2_total + tome3_total

		if all_tomes_total == 0:
			continue

		row = f"|{name}"
		row += f" | {fight_time:.2f} | "
		row += f"{round(60 * all_tomes_total / fight_time, 4):.2f} | |"

		row += fmt_firebrand_page_total(tome1_total, 0, fight_time, all_tomes_total)
		for skill_id in tome1_skill_ids:
			page_total = firebrand_pages.get(skill_id, 0)
			page_cost = tome_skill_page_cost[skill_id]
			row += fmt_firebrand_page_total(page_total, page_cost, fight_time, all_tomes_total)
		row += " |"

		row += fmt_firebrand_page_total(tome2_total, 0, fight_time, all_tomes_total)
		for skill_id in tome2_skill_ids:
			page_total = firebrand_pages.get(skill_id, 0)
			page_cost = tome_skill_page_cost[skill_id]
			row += fmt_firebrand_page_total(page_total, page_cost, fight_time, all_tomes_total)
		row += " |"

		row += fmt_firebrand_page_total(tome3_total, 0, fight_time, all_tomes_total)
		for skill_id in tome3_skill_ids:
			page_total = firebrand_pages.get(skill_id, 0)
			page_cost = tome_skill_page_cost[skill_id]
			row += fmt_firebrand_page_total(page_total, page_cost, fight_time, all_tomes_total)

		rows.append(row)
	rows.append("| Firebrand Pages |c")
	rows.append("\n\n</div>")
	firebrand_pages_tags = f"{tid_date_time}"
	firebrand_pages_title = f"{tid_date_time}-FB-Pages"
	firebrand_pages_caption = f"{caption}"
	firebrand_pages_text = "\n".join(rows)
	append_tid_for_output(
		create_new_tid_from_template(firebrand_pages_title, firebrand_pages_caption, firebrand_pages_text, firebrand_pages_tags),
		tid_list
	)

def build_high_scores_tid(high_scores: dict, skill_data: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	caption_dict = {
	"statTarget_max": "Highest Outgoing Skill Damage", "totalDamageTaken_max": "Highest Incoming Skill Damage",
	"fight_dps": "Damage per Second", "statTarget_killed": "Kills per Second", "statTarget_downed": "Downs per Second", "statTarget_downContribution": "Down Contrib per Second",
	"defenses_blockedCount": "Blocks per Second", "defenses_evadedCount": "Evades per Second", "defenses_dodgeCount":  "Dodges per Second", "defenses_invulnedCount": "Invulned per Second",
	"support_condiCleanse": "Cleanses per Second", "support_boonStrips": "Strips per Second", "extHealingStats_Healing": "Healing per Second",  "extBarrierStats_Barrier": "Barrier per Second", 
	}

	high_scores_tags = f"{tid_date_time}"
	high_scores_title = f"{tid_date_time}-High-Scores"
	high_scores_caption = f"{caption}"
	high_scores_text = ""

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	rows.append('<div class="flex-row">\n\n')
	for category in caption_dict:

		table_title = caption_dict[category]
		header = '    <div class="flex-col">\n\n'
		header += "|thead-dark table-caption-top table-hover|k\n"
		if category in ["statTarget_max", "totalDamageTaken_max"]:
			header += "|@@display:block;width:200px;Player@@  |@@display:block;width:250px;Skill@@ | @@display:block;width:100px;Score@@|h"
		else:
			header += "|@@display:block;width:200px;Player@@ | @@display:block;width:100px;Score@@|h"
		
		rows.append(header)

		sorted_high_scores = sorted(high_scores[category].items(), key=lambda x: x[1], reverse=True)
		for player in sorted_high_scores:
			player, score = player

			if category in ["statTarget_max", "totalDamageTaken_max"]:
				skill_id = player.split("| ")[1]
				prof_name = player.split(" |")[0]
				if "s"+str(skill_id) in skill_data:
					skill_name = skill_data["s"+str(skill_id)]['name']
					skill_icon = skill_data["s"+str(skill_id)]['icon']
				elif "b"+str(skill_id) in buff_data:
					skill_name = buff_data["b"+str(skill_id)]['name']
					skill_icon = buff_data["b"+str(skill_id)]['icon']
				else:
					skill_name = skill_id
					skill_icon = "unknown.png"
				detailEntry = f'[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}'

				row = f"|{prof_name} |{detailEntry} | {score:03,.2f}|"
			else:
				prof_name = player.split(" |")[0]
				row = f"|{prof_name} | {score:03,.2f}|"
			rows.append(row)

		rows.append(f"| ''{table_title}'' |c")
		rows.append("\n\n    </div>\n\n")
		if category == "totalDamageTaken_max":
			rows.append('\n<div class="flex-row">\n\n')
	rows.append("</div>\n\n")
	rows.append("</div>\n\n")
	high_scores_text = "\n".join(rows)
	append_tid_for_output(
		create_new_tid_from_template(high_scores_title, high_scores_caption, high_scores_text, high_scores_tags),
		tid_list
	)

def build_mechanics_tid(mechanics: dict, players: dict, caption: str, tid_date_time: str) -> None:
	rows = []
	for fight in mechanics:
		player_list = mechanics[fight]['player_list']
		mechanics_list = []
		for mechanic in mechanics[fight]:
			if mechanic in ['player_list', 'enemy_list']:
				continue
			else:
				mechanics_list.append(mechanic)

		rows.append('<div style="overflow-x:auto;">\n\n')
		header = "|thead-dark table-caption-top-left table-hover sortable freeze-col|k\n"
		header += "|!Player |"
		for mechanic in mechanics_list:
			tooltip = f"{mechanics[fight][mechanic]['tip']}"
			detailed_entry = f"<span class=\"tooltip\" title=\"{tooltip}\">{mechanic}</span>"
			header += f" !{detailed_entry} |"

		header += "h"
		rows.append(header)

		for player in player_list:
			row = f"|{player} |"
			for mechanic in mechanics_list:
				if player in mechanics[fight][mechanic]['data']:
					row += f" {mechanics[fight][mechanic]['data'][player]} |"
				else:
					row += " - |"
			rows.append(row)
		if fight == "WVW":
			rows.append(f"|''Fight-WVW-Mechanics'' |c")
		else:
			rows.append(f"|''Fight-{fight:02d}-Mechanics'' |c")
		rows.append("\n\n</div>\n\n")
	text = "\n".join(rows)
	mechanics_title = f"{tid_date_time}-Mechanics"
	append_tid_for_output(
		create_new_tid_from_template(f"{mechanics_title}", caption, text, tid_date_time),
		tid_list
	)

def build_minions_tid(minions: dict, players: dict, caption: str, tid_date_time: str) -> None:
	minion_stats_tags = f"{tid_date_time}"
	minion_stats_title = f"{tid_date_time}-Minions"
	minion_stats_caption = f"{caption}"
	minion_stats_creator = f"Drevarr@github.com"
	minion_stats_text ="<<tabs '"
	tab_name = ""
	for profession in minions:
		tab_name = f"{tid_date_time}-{caption.replace(' ','-')}-{profession}"
		minion_stats_text += f'[[{tab_name}]]'

	minion_stats_text += f"' '{tab_name}' '$:/temp/tab1'>>"
	append_tid_for_output(
		create_new_tid_from_template(minion_stats_title, minion_stats_caption, minion_stats_text, minion_stats_tags, creator=minion_stats_creator),
		tid_list
	)

	for profession in minions:
		rows = []
		rows.append('<div style="overflow-x:auto;">\n\n')
		header = "|thead-dark table-caption-top-left table-hover sortable freeze-col|k\n"
		header += "|!Player | Fights| Fight Time|"
		for minion in minions[profession]['pets_list']:
			header += f" !{minion} |"
		header += "h"
		rows.append(header)

		for player in minions[profession]['player']:
			name_prof = f"{player}|{profession}"
			prof_name = "{{"+profession+"}}"+player
			fights = players[name_prof]['num_fights']
			fight_time = f"{players[name_prof]['fight_time']/1000:,.1f}"

			row = f"|{prof_name} | {fights}| {fight_time}|"
			for minion in minions[profession]['pets_list']:
				if minion in minions[profession]['player'][player]:
					entry = f" {minions[profession]['player'][player][minion]} |"
				else:
					entry = " - |"
				row += entry
			rows.append(row)
		#rows.append(f"| {profession}_{caption} |c")
		rows.append("\n\n</div>\n\n")
		text = "\n".join(rows)
		minion_stats_title = f"{tid_date_time}-{caption.replace(' ','-')}-{profession}"
		profession = "{{"+f"{profession}"+"}}"
		prof_caption = f"{profession}-Minions"

		append_tid_for_output(
			create_new_tid_from_template(minion_stats_title, prof_caption, text, tid_date_time),
			tid_list
		)

def build_top_damage_by_skill(total_damage_taken: dict, target_damage_dist: dict, skill_data: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	"""Builds a table of top damage by skill."""

	sorted_total_damage_taken = dict(sorted(total_damage_taken.items(), key=lambda item: item[1]["totalDamage"], reverse=True))
	sorted_target_damage_dist = dict(sorted(target_damage_dist.items(), key=lambda item: item[1]["totalDamage"], reverse=True))

	total_damage_taken_value = sum(skill["totalDamage"] for skill in sorted_total_damage_taken.values())
	total_damage_distributed_value = sum(skill["totalDamage"] for skill in sorted_target_damage_dist.values())

	rows = []
	rows.append('<div style="overflow-x:auto;">\n\n')
	rows.append("|thead-dark table-borderless w-75 table-center|k")
	rows.append("|!Top 25 Skills by Damage Output|")
	rows.append("\n\n")
	rows.append('\n<div class="flex-row">\n\n    <div class="flex-col">\n\n')
	header = "|thead-dark table-caption-top-left table-hover table-center sortable freeze-col|k\n"
	header += "|!Skill Name | Damage Taken | % of Total|h"
	rows.append(header)
	for i, (skill_id, skill) in enumerate(sorted_target_damage_dist.items()):
		if i < 25:
			skill_name = skill_data.get(f"s{skill_id}", {}).get("name", buff_data.get(f"b{skill_id}", {}).get("name", ""))
			skill_icon = skill_data.get(f"s{skill_id}", {}).get("icon", buff_data.get(f"b{skill_id}", {}).get("icon", ""))
			entry = f"[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}"
			row = f"|{entry} | {skill['totalDamage']:,.0f} | {skill['totalDamage']/total_damage_distributed_value*100:,.1f}% |"

			rows.append(row)

	rows.append(f"| Squad Damage Output |c")
	rows.append('\n\n</div>\n\n    <div class="flex-col">\n\n')

	header = "|thead-dark table-caption-top-left table-hover table-center sortable freeze-col|k\n"
	header += "|!Skill Name | Damage Taken | % of Total|h"
	rows.append(header)
	for i, (skill_id, skill) in enumerate(sorted_total_damage_taken.items()):
		if i < 25:
			skill_name = skill_data.get(f"s{skill_id}", {}).get("name", buff_data.get(f"b{skill_id}", {}).get("name", ""))
			skill_icon = skill_data.get(f"s{skill_id}", {}).get("icon", buff_data.get(f"b{skill_id}", {}).get("icon", ""))
			entry = f"[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}"
			row = f"|{entry} | {skill['totalDamage']:,.0f} | {skill['totalDamage']/total_damage_taken_value*100:,.1f}% |"

			rows.append(row)

	rows.append(f"| Enemy Damage Output |c")
	rows.append("\n\n</div>\n\n</div>")

	rows.append("\n\n</div>\n\n")
	text = "\n".join(rows)

	top_skills_title = f"{tid_date_time}-{caption.replace(' ', '-')}"

	append_tid_for_output(
		create_new_tid_from_template(top_skills_title, caption, text, tid_date_time),
		tid_list
	)

def build_healer_menu_tabs(top_stats: dict, caption: str, tid_date_time: str) -> None:
	"""Builds a menu tab macro for healers."""

	# Get the list of healers
	healers = {}
	for name_prof in top_stats['players_running_healing_addon']:
		name = name_prof.split('|')[0]
		prof = name_prof.split('|')[1]
		healers[name] = prof

	# Sort healers by profession
	sorted_healers = dict(sorted(healers.items(), key=lambda item: item[1]))

	# Build the menu tab macro
	menu_tags = f"{tid_date_time}"
	menu_title = f"{tid_date_time}-Healers"
	menu_caption = f"Healer - Outgoing"
	menu_creator = f"Drevarr@github.com"
	menu_text = "<<tabs '"
	tab_name = ""
	for healer_name, healer_profession in sorted_healers.items():
		tab_name = f"{tid_date_time}-{caption.replace(' ', '-')}-{healer_profession}-{healer_name}"
		menu_text += f"[[{tab_name}]]"
	menu_text += f"' '{tab_name}' '$:/temp/tab1'>>"

	# Push the menu tab to the output list
	append_tid_for_output(
		create_new_tid_from_template(menu_title, menu_caption, menu_text, menu_tags, creator=menu_creator),
		tid_list
	)

def build_healer_outgoing_tids(top_stats: dict, skill_data: dict, buff_data: dict, caption: str, tid_date_time: str) -> None:
	"""
	Builds tables of outgoing healing and barrier by player and skill.

	Iterates through each healer and builds a table of their outgoing healing and barrier by skill.
	It also builds a table of the total healing and barrier by target.
	"""

	# Iterate through each healer
	for healer in top_stats['players_running_healing_addon']:
		name = healer.split('|')[0]
		profession = healer.split('|')[1]
		healer_name = name
		healer_profession = profession
		healer_tags = f"{tid_date_time}"
		healer_title = f"{tid_date_time}-{caption.replace(' ', '-')}-{healer_profession}-{healer_name}"
		healer_caption = "{{"+healer_profession+"}}"+f" - {healer_name}"

		rows = []

		rows.append("---\n\n")
		rows.append('<div style="overflow-x:auto;">\n\n')
		rows.append("|thead-dark table-borderless w-75 table-center|k")
		rows.append("|!Healer Outgoing Stats - excludes downed healing|")
		rows.append("\n\n")
		rows.append('\n<div class="flex-row">\n\n    <div class="flex-col">\n\n')

		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += "|!Skill Name |!Hits | !Total Healing| !Avg Healing| !Pct|h"
		rows.append(header)

		outgoing_healing = top_stats['player'][healer]['extHealingStats'].get('outgoing_healing', 0)
		for skill in top_stats['player'][healer]['extHealingStats']['skills']:
			skill_name = skill_data.get(skill, {}).get("name", buff_data.get(skill.replace("s", "b"), {}).get("name", ""))
			skill_icon = skill_data.get(skill, {}).get("icon", buff_data.get(skill.replace("s", "b"), {}).get("icon", ""))
			entry = f"[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}"

			hits = top_stats['player'][healer]['extHealingStats']['skills'][skill]['hits']
			total_healing = top_stats['player'][healer]['extHealingStats']['skills'][skill]['healing']
			avg_healing = total_healing/hits if hits > 0 else 0

			row = f"|{entry} | {hits:,.0f} | {total_healing:,.0f}| {avg_healing:,.0f}| {total_healing/outgoing_healing*100:,.2f}%|"

			rows.append(row)

		rows.append(f"| Total Healing |c")

		rows.append("\n\n</div>")

		rows.append("\n\n")
		rows.append('\n<div class="flex-col">\n\n')

		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += "| Total Barrier |c\n"
		header += "|!Skill Name |!Hits | !Total Barrier| !Avg Barrier| !Pct|h"
		rows.append(header)

		outgoing_barrier = top_stats['player'][healer]['extBarrierStats'].get('outgoing_barrier', 0)
		if outgoing_barrier:

			for skill in top_stats['player'][healer]['extBarrierStats']['skills']:
				skill_name = skill_data.get(skill, {}).get("name", buff_data.get(skill.replace("s", "b"), {}).get("name", ""))
				skill_icon = skill_data.get(skill, {}).get("icon", buff_data.get(skill.replace("s", "b"), {}).get("icon", ""))
				entry = f"[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}"

				hits = top_stats['player'][healer]['extBarrierStats']['skills'][skill]['hits']
				total_barrier = top_stats['player'][healer]['extBarrierStats']['skills'][skill]['totalBarrier']
				avg_barrier = total_barrier/hits if hits > 0 else 0

				row = f"|{entry} | {hits:,.0f} | {total_barrier:,.0f}| {avg_barrier:,.0f}| {total_barrier/outgoing_barrier*100:,.2f}%|"

				rows.append(row)

		rows.append("\n\n</div>")

		rows.append("\n\n")
		rows.append('\n<div class="flex-col">\n\n')

		header = "|thead-dark table-caption-top table-hover sortable|k\n"
		header += "| Heal/Barrier by Target |c\n"
		header += "|!Player |!Total Healing | !Downed Healing| !Total Barrier|h"
		rows.append(header)

		targets_used = []
		if 'heal_targets' in top_stats['player'][healer]['extHealingStats']:
			for target in top_stats['player'][healer]['extHealingStats']['heal_targets']:
				target_barrier = 0
				targets_used.append(target)
				target_healing = top_stats['player'][healer]['extHealingStats']['heal_targets'][target]['outgoing_healing']
				target_downed = top_stats['player'][healer]['extHealingStats']['heal_targets'][target]['downed_healing']
				if 'barrier_targets' in top_stats['player'][healer]['extBarrierStats']:
					if target in top_stats['player'][healer]['extBarrierStats']['barrier_targets']:
						target_barrier = top_stats['player'][healer]['extBarrierStats']['barrier_targets'][target]['outgoing_barrier']

				row = f"|{target} | {target_healing:,.0f} | {target_downed:,.0f}| {target_barrier:,.0f}|"

				rows.append(row)

		if 'barrier_targets' in top_stats['player'][healer]['extBarrierStats']:
			for target in top_stats['player'][healer]['extBarrierStats']['barrier_targets']:
				if target not in targets_used:
					target_healing = 0
					target_downed = 0
					target_barrier = top_stats['player'][healer]['extBarrierStats']['barrier_targets'][target]['outgoing_barrier']

				row = f"|{target} | {target_healing:,.0f} | {target_downed:,.0f}| {target_barrier:,.0f}|"

				rows.append(row)

		rows.append("\n\n</div>\n\n</div>")

		rows.append("\n\n</div>")

		text = "\n".join(rows)

		append_tid_for_output(
			create_new_tid_from_template(healer_title, healer_caption, text, healer_tags),
			tid_list
		)

def build_damage_outgoing_by_player_skill_tids(top_stats: dict, skill_data: dict, buff_data: dict, tid_list: list) -> None:
	damage_totals = {}
	for player in top_stats['player']:
		damage_totals[player] = top_stats['player'][player]['statsTargets']['totalDmg']
	sorted_damage_totals = sorted(damage_totals.items(), key=lambda x: x[1], reverse=True)

	for player, damage in sorted_damage_totals:
		player_damage = {}
		for skill in top_stats['player'][player]['targetDamageDist']['skills']:
			player_damage[skill] = top_stats['player'][player]['targetDamageDist']['skills'][skill]['totalDamage']

		sorted_player_damage = sorted(player_damage.items(), key=lambda x: x[1], reverse=True)

		rows = []

		name, profession = player.split("|")
		spacedName = name.ljust(21, '.')
		rows.append('<div style="overflow-x:auto;">\n\n')
		rows.append(f'<$reveal type="match" stateTitle="$:/temp/Player_Selected" stateField="{spacedName}{profession}" text="{spacedName}{profession}">')
		rows.append('\n<div class="flex-col">\n\n')
		header = "|thead-dark table-borderless w-75 table-center|k\n"
		header += "|@@display:block;width:50px;Player@@ | Profession | Total Damage|h"

		rows.append(header)
		rows.append("|"+name+" | {{"+profession +"}} | "+f"{damage:,.0f}|")

		for skill in sorted_player_damage:
			skill_name = skill_data.get(f"s{skill[0]}", {}).get("name", buff_data.get(f"b{skill[0]}", {}).get("name", ""))
			skill_icon = skill_data.get(f"s{skill[0]}", {}).get("icon", buff_data.get(f"b{skill[0]}", {}).get("icon", ""))
			entry = f"[img width=24 [{skill_name}|{skill_icon}]]-{skill_name}"
			row = f"|{entry} | {skill[1]:,.0f} | {skill[1]/damage*100:,.1f}%|"

			rows = []
			rows.append("\n\n")

def output_top_stats_json(top_stats: dict, buff_data: dict, skill_data: dict, damage_mod_data: dict, high_scores: dict, personal_damage_mod_data: dict, fb_pages: dict, mechanics: dict, minions: dict, outfile: str) -> None:
	"""Print the top_stats dictionary as a JSON object to the console."""

	json_dict = {}
	json_dict["overall_raid_stats"] = {key: value for key, value in top_stats['overall'].items()}
	json_dict["fights"] = {key: value for key, value in top_stats['fight'].items()}
	json_dict["parties_by_fight"] = {key: value for key, value in top_stats["parties_by_fight"].items()}
	json_dict["players"] = {key: value for key, value in top_stats['player'].items()}
	json_dict["buff_data"] = {key: value for key, value in buff_data.items()}
	json_dict["skill_data"] = {key: value for key, value in skill_data.items()}
	json_dict["damage_mod_data"] = {key: value for key, value in damage_mod_data.items()}
	json_dict["skill_casts_by_role"] = {key: value for key, value in top_stats["skill_casts_by_role"].items()}
	json_dict["high_scores"] = {key: value for key, value in high_scores.items()}    
	json_dict["personal_damage_mod_data"] = {key: value for key, value in personal_damage_mod_data.items()}
	json_dict["fb_pages"] = {key: value for key, value in fb_pages.items()}
	json_dict["mechanics"] = {key: value for key, value in mechanics.items()}
	json_dict["minions"] = {key: value for key, value in minions.items()}    	
	with open(outfile, 'w') as json_file:
		json.dump(json_dict, json_file, indent=4)

		print("JSON File Complete : "+outfile)
	json_file.close()