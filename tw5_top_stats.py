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
import sys
import os.path
from os import listdir
from enum import Enum
import json
import datetime
import gzip

from collections import OrderedDict

#from gooey import Gooey, GooeyParser

import config
import config_output
from parser_functions import *
from output_functions import *

#@Gooey(
#		program_name='GW2 - EI - Log Combiner',
#		image_dir='./',
#		default_size=(600, 750)
#)

if __name__ == '__main__':
	#parser = GooeyParser(description='This reads a set of arcdps reports in json format and generates a summary.')
	parser = argparse.ArgumentParser(description='This reads a set of arcdps reports in xml format and generates top stats.')
	#parser.add_argument('input_directory', help='Directory containing .json files from Elite Insights', widget="DirChooser")
	parser.add_argument('input_directory', help='Directory containing .json files from Elite Insights')
	parser.add_argument('-o', '--output', dest="output_filename", help="Not required. Override json file name to write the computed summary")
	parser.add_argument('-x', '--xls_output', dest="xls_output_filename", help="Not required. Override .xls file to write the computed summary")    
	parser.add_argument('-j', '--json_output', dest="json_output_filename", help="Not required. Override .json file to write the computed stats data")    
	parser.add_argument('-l', '--log_file', dest="log_file", help="Not required. Override Logging file with program log entries")
	args = parser.parse_args()

	parse_date = datetime.datetime.now()
	tid_date_time = parse_date.strftime("%Y%m%d%H%M")

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
	if args.log_file is None:
		args.log_file = args.input_directory+"/log_detailed_"+tid_date_time+".txt"

	#output = open(args.output_filename, "w",encoding="utf-8")
	#log = open(args.log_file, "w")

	print_string = "Using input directory "+args.input_directory+", writing output to "+args.output_filename+" and log to "+args.log_file
	print(print_string)

	# Change input_directory to match json log location
	input_directory = args.input_directory


	files = listdir(input_directory)
	sorted_files = sorted(files)


	file_date = datetime.datetime.now()
	# file_tid = file_date.strftime('%Y%m%d%H%M')+"_Fight_Review.tid"
	# output = open(file_tid, "w", encoding="utf-8")

	fight_num = 0



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
		
		parse_file(file_path, fight_num)

	print("Parsing Complete")

	#create the main tiddler and append to tid_list
	build_main_tid(tid_date_time)

	#create the menu tiddler and append to tid_list
	build_menu_tid(tid_date_time)

	build_general_stats_tid(tid_date_time)

	build_buffs_stats_tid(tid_date_time)

	build_boon_stats_tid(tid_date_time)

	build_damage_modifiers_menu_tid(tid_date_time)

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


	#get heal stats found and output table
	build_healing_summary(top_stats, "Heal Stats", tid_date_time)


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

	tag_data = build_tag_summary(top_stats)
	output_tag_summary(tag_data, tid_date_time)


	build_damage_summary_table(top_stats, "Damage", tid_date_time)

	write_tid_list_to_json(tid_list, args.output_filename)

	output_top_stats_json(top_stats, buff_data, skill_data, damage_mod_data, high_scores, personal_damage_mod_data, fb_pages, args.json_output_filename)

#if __name__ == '__main__':
#    main()