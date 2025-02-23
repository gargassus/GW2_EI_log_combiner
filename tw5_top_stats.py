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


import argparse
import configparser
import sys
import os.path
from os import listdir
from enum import Enum
import json
import datetime
import gzip

from collections import OrderedDict

import config
import config_output
from parser_functions import *
from output_functions import *


if __name__ == '__main__':
	config_ini = configparser.ConfigParser()
	config_ini.read('top_stats_config.ini')
	weights ={
		'Boon_Weights': {
			'Aegis': 1,
			'Alacrity': 1,
			'Fury': 1,
			'Might': 1,
			'Protection': 1,
			'Quickness': 1,
			'Regeneration': 1,
			'Resistance': 1,
			'Resolution': 1,
			'Stability': 1,
			'Swiftness': 1,
			'Vigor': 1,
			'Superspeed': 1
		},
		'Condition_Weights': {
			'Bleed': 1,
			'Burning': 1,
			'Confusion': 1,
			'Poisoned': 1,
			'Torment': 1,
			'Blinded': 1,
			'Chilled': 1,
			'Crippled': 1,
			'Fear': 1,
			'Immobilized': 1,
			'Slow': 1,
			'Taunt': 1,
			'Weakness': 1,
			'Vulnerability': 1
		}
	}

	for section in config_ini.sections():
		if section == "Boon_Weights":
			weights[section] = dict(config_ini[section])
		if section == "Condition_Weights":
			weights[section] = dict(config_ini[section])
	
	parser = argparse.ArgumentParser(description='This reads a set of arcdps reports in xml format and generates top stats.')
	parser.add_argument('-i', '--input', dest='input_directory', help='Directory containing .json files from Elite Insights')
	parser.add_argument('-o', '--output', dest="output_filename", help="Not required. Override json file name to write the computed summary")
	parser.add_argument('-x', '--xls_output', dest="xls_output_filename", help="Not required. Override .xls file to write the computed summary")    
	parser.add_argument('-j', '--json_output', dest="json_output_filename", help="Not required. Override .json file to write the computed stats data")    
	#parser.add_argument('-l', '--log_file', dest="log_file", help="Not required. Override Logging file with program log entries")
	args = parser.parse_args()

	input_directory = config_ini.get('TopStatsCfg', 'input_directory', fallback='./')
	guild_name = config_ini.get('TopStatsCfg', 'guild_name', fallback=None)
	guild_id = config_ini.get('TopStatsCfg', 'guild_id', fallback=None)
	api_key = config_ini.get('TopStatsCfg', 'api_key', fallback=None)
	db_update = config_ini.getboolean('TopStatsCfg', 'db_update', fallback=False)
	write_all_data_to_json = config_ini.getboolean('TopStatsCfg', 'write_all_data_to_json', fallback=False)

	parse_date = datetime.datetime.now()
	tid_date_time = parse_date.strftime("%Y%m%d%H%M")

	if args.input_directory is None:
		args.input_directory = input_directory
	if not os.path.isdir(args.input_directory):
		print("Directory ",args.input_directory," is not a directory or does not exist!")
		sys.exit()
	if args.output_filename is None:
		args.output_filename = f"{args.input_directory}/Drag_and_Drop_Log_Summary_for_{tid_date_time}.json"
	else:
		args.output_filename = args.input_directory+"/"+args.output_filename
	if args.xls_output_filename is None:
		args.xls_output_filename = args.input_directory+"/TW5_top_stats_"+tid_date_time+".xls"
	if args.json_output_filename is None:
		args.json_output_filename = args.input_directory+"/TW5_top_stats_"+tid_date_time+".json"                
	#if args.log_file is None:
	#	args.log_file = args.input_directory+"/log_detailed_"+tid_date_time+".txt"

	# Change input_directory to match json log location
	input_directory = args.input_directory

	#log_file = open(args.log_file, 'w')

	files = listdir(input_directory)
	sorted_files = sorted(files)

	file_date = datetime.datetime.now()

	fight_num = 0

	print_string = "Using input directory "+args.input_directory+", writing output to "+args.output_filename
	print(print_string)

	guild_data = None
	if guild_id and api_key:
		guild_data = fetch_guild_data(guild_id, api_key)
	
	print("guild_id: ", guild_id)
	print("API_KEY: ", api_key)
	for filename in sorted_files:
		
		# skip files of incorrect filetype
		file_start, file_extension = os.path.splitext(filename)
		# if args.filetype not in file_extension or "top_stats" in file_start:
		if file_extension not in ['.json', '.gz'] or "Drag_and_Drop_" in file_start or "TW5_top_stats_" in file_start:
			continue

		print_string = "parsing " + filename
		print(print_string)
		file_path = "".join((input_directory, "/", filename))

		fight_num += 1
		
		parse_file(file_path, fight_num, guild_data)

	print("Parsing Complete")

	tag_data, tag_list = build_tag_summary(top_stats)

	#create the main tiddler and append to tid_list
	build_main_tid(tid_date_time, tag_list, guild_name)

	output_tag_summary(tag_data, tid_date_time)

	#create the menu tiddler and append to tid_list
	build_menu_tid(tid_date_time)

	build_dashboard_menu_tid(tid_date_time)
	
	build_general_stats_tid(tid_date_time)

	build_buffs_stats_tid(tid_date_time)

	build_boon_stats_tid(tid_date_time)

	build_damage_modifiers_menu_tid(tid_date_time)

	build_healer_menu_tabs(top_stats, "Healers", tid_date_time)
	build_healer_outgoing_tids(top_stats, skill_data, buff_data, "Healers", tid_date_time)

	build_profession_damage_modifier_stats_tid(personal_damage_mod_data, "Damage Modifiers", tid_date_time)

	build_shared_damage_modifier_summary(top_stats, damage_mod_data, "Shared Damage Mods", tid_date_time)
		
	defense_stats = config_output.defenses_table
	build_category_summary_table(top_stats, defense_stats, "Defenses", tid_date_time)

	support_stats = config_output.support_table
	build_category_summary_table(top_stats, support_stats, "Support", tid_date_time)

	offensive_stats = config_output.offensive_table
	build_category_summary_table(top_stats, offensive_stats, "Offensive", tid_date_time)

	boons = config_output.boons
	build_uptime_summary(top_stats, boons, buff_data, "Uptimes", tid_date_time)

	boon_categories = {"selfBuffs", "groupBuffs", "squadBuffs"}
	for boon_category in boon_categories:
		build_boon_summary(top_stats, boons, boon_category, buff_data, tid_date_time)

	#get incoming condition uptimes on Squad Players
	conditions = config_output.buffs_conditions
	condition_list = {}
	for condition in conditions:
		if condition in top_stats["overall"]["buffUptimes"]:
			if top_stats["overall"]["buffUptimes"][condition]["uptime_ms"] > 0:
				condition_list[condition] = conditions[condition]
	build_uptime_summary(top_stats, condition_list, buff_data, "Conditions-In", tid_date_time)

	#get outgoing debuff uptimes on Enemy Players
	debuffs = config_output.buffs_debuff
	debuff_list = {}
	for debuff in debuffs:
		if debuff in top_stats["overall"]["targetBuffs"]:
			if top_stats["overall"]["targetBuffs"][debuff]["uptime_ms"] > 0:
				debuff_list[debuff] = debuffs[debuff]
	build_debuff_uptime_summary(top_stats, debuff_list, buff_data, "Debuffs-Out", tid_date_time)

	#get outgoing condition uptimes on Enemy Players
	conditions = config_output.buffs_conditions
	condition_list = {}
	for condition in conditions:
		if condition in top_stats["overall"]["targetBuffs"]:
			if top_stats["overall"]["targetBuffs"][condition]["uptime_ms"] > 0:
				condition_list[condition] = conditions[condition]
	build_debuff_uptime_summary(top_stats, condition_list, buff_data, "Conditions-Out", tid_date_time)

	#get support buffs found and output table
	support_buffs = config_output.buffs_support
	support_buff_list = {}
	for buff in support_buffs:
		if buff in top_stats["overall"]["buffUptimes"]:
			if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
				support_buff_list[buff] = support_buffs[buff]
	build_uptime_summary(top_stats, support_buff_list, buff_data, "Support Buffs", tid_date_time)

	#get defensive buffs found and output table
	defensive_buffs = config_output.buffs_defensive
	defensive_buff_list = {}
	for buff in defensive_buffs:
		if buff in top_stats["overall"]["buffUptimes"]:
			if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
				defensive_buff_list[buff] = defensive_buffs[buff]
	build_uptime_summary(top_stats, defensive_buff_list, buff_data, "Defensive Buffs", tid_date_time)

	#get offensive buffs found and output table
	offensive_buffs = config_output.buffs_offensive
	offensive_buff_list = {}
	for buff in offensive_buffs:
		if buff in top_stats["overall"]["buffUptimes"]:
			if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
				offensive_buff_list[buff] = offensive_buffs[buff]
	build_uptime_summary(top_stats, offensive_buff_list, buff_data, "Offensive Buffs", tid_date_time)

	#get offensive debuffs found and output table
	debuffs_buffs = config_output.buffs_debuff
	debuff_list = {}
	for buff in debuffs_buffs:
		if buff in top_stats["overall"]["buffUptimes"]:
			if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
				debuff_list[buff] = debuffs_buffs[buff]
	build_uptime_summary(top_stats, debuff_list, buff_data, "Debuffs-In", tid_date_time)

	#get squad comp and output table
	build_squad_composition(top_stats, tid_date_time, tid_list)


	#get heal stats found and output table
	build_healing_summary(top_stats, "Heal Stats", tid_date_time)

	#get personal buffs found and output table
	build_personal_buff_summary(top_stats, buff_data, personal_buff_data, "Personal Buffs", tid_date_time)

	#get profession damage modifiers found and output table
	build_personal_damage_modifier_summary(top_stats, personal_damage_mod_data, damage_mod_data, "Damage Modifiers", tid_date_time)

	#get skill casts by profession and role and output table
	build_skill_cast_summary(top_stats["skill_casts_by_role"], skill_data, "Skill Usage", tid_date_time)

	build_skill_usage_stats_tid(top_stats["skill_casts_by_role"], "Skill Usage", tid_date_time)

	#get overview stats found and output table
	#overview_stats = config_output.overview_stats
	build_fight_summary(top_stats, "Overview", tid_date_time)

	#get combat resurrection stats found and output table
	build_combat_resurrection_stats_tid(top_stats, skill_data, buff_data, "Combat Resurrect", tid_date_time)

	#get FB Pages and output table
	build_fb_pages_tid(fb_pages, "FB Pages", tid_date_time)

	build_high_scores_tid(high_scores, skill_data, buff_data, "High Scores", tid_date_time)

	build_mechanics_tid(mechanics, top_stats['player'], "Mechanics", tid_date_time)

	build_minions_tid(minions, top_stats['player'], "Minions", tid_date_time)

	build_top_damage_by_skill(top_stats['overall']['totalDamageTaken'], top_stats['overall']['targetDamageDist'], skill_data, buff_data, "Top Damage By Skill", tid_date_time)


	#build_damage_outgoing_by_player_skill_tids
	build_damage_outgoing_by_skill_tid(tid_date_time, tid_list)
	build_damage_outgoing_by_player_skill_tids(top_stats, skill_data, buff_data, tid_date_time, tid_list)

	#build_gear_buff_summary
	gear_buff_ids, gear_skill_ids = extract_gear_buffs_and_skills(buff_data, skill_data)
	build_gear_buff_summary(top_stats, gear_buff_ids, buff_data, tid_date_time)
	build_gear_skill_summary(top_stats, gear_skill_ids, skill_data, tid_date_time)

	build_damage_summary_table(top_stats, "Damage", tid_date_time)

	build_on_tag_review(death_on_tag, tid_date_time)

	build_mesmer_clone_usage(mesmer_clone_usage, tid_date_time, tid_list)

	profession_color = config_output.profession_color
	build_support_bubble_chart(top_stats, buff_data, weights, tid_date_time, tid_list, profession_color)
	build_DPS_bubble_chart(top_stats, tid_date_time, tid_list, profession_color)
	build_utility_bubble_chart(top_stats, buff_data, weights, tid_date_time, tid_list, profession_color)
	
	build_dps_stats_tids(DPSStats, tid_date_time, tid_list)
	build_dps_stats_menu(tid_date_time)

	#attendance
	build_attendance_table(top_stats,tid_date_time, tid_list)

	#commander Tag summary
	if build_commander_summary_menu:
		build_commander_summary(commander_summary_data, skill_data, buff_data, tid_date_time, tid_list)
		build_commander_summary_menu(commander_summary_data, tid_date_time, tid_list)

	write_tid_list_to_json(tid_list, args.output_filename)

	if write_all_data_to_json:
		output_top_stats_json(top_stats, buff_data, skill_data, damage_mod_data, high_scores, personal_damage_mod_data, personal_buff_data, fb_pages, mechanics, minions, mesmer_clone_usage, death_on_tag, DPSStats, commander_summary_data, args.json_output_filename)

	if db_update:
		write_data_to_db(top_stats, top_stats['overall']['last_fight'])
