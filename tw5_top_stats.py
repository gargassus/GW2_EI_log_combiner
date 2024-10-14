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

import config
import config_output
from parser_functions import *
from output_functions import *


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='This reads a set of arcdps reports in xml format and generates top stats.')
	parser.add_argument('input_directory', help='Directory containing .xml or .json files from arcdps reports')
	parser.add_argument('-o', '--output', dest="output_filename", help="Text file to write the computed top stats")
	parser.add_argument('-x', '--xls_output', dest="xls_output_filename", help="xls file to write the computed top stats")    
	parser.add_argument('-j', '--json_output', dest="json_output_filename", help="json file to write the computed top stats to")    
	parser.add_argument('-l', '--log_file', dest="log_file", help="Logging file with all the output")
	args = parser.parse_args()

	parse_date = datetime.datetime.now()

	if not os.path.isdir(args.input_directory):
		print("Directory ",args.input_directory," is not a directory or does not exist!")
		sys.exit()
	if args.output_filename is None:
		args.output_filename = args.input_directory+"/TW5_top_stats_"+parse_date.strftime("%Y%m%d%H%M")+".tid"
	else:
		args.output_filename = args.input_directory+"/"+args.output_filename
	if args.xls_output_filename is None:
		args.xls_output_filename = args.input_directory+"/TW5_top_stats_"+parse_date.strftime("%Y%m%d%H%M")+".xls"
	if args.json_output_filename is None:
		args.json_output_filename = args.input_directory+"/TW5_top_stats_"+parse_date.strftime("%Y%m%d%H%M")+".json"                
	if args.log_file is None:
		args.log_file = args.input_directory+"/log_detailed_"+parse_date.strftime("%Y%m%d%H%M")+".txt"

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


json_stats = config.json_stats



def parse_file(file_path, fight_num):
    if file_path.endswith('.gz'):
        with gzip.open(file_path, mode="r") as f:
            json_data = json.loads(f.read().decode('utf-8'))
    else:
        json_datafile = open(file_path, encoding='utf-8')
        json_data = json.load(json_datafile)

    if 'usedExtensions' not in json_data:
        players_running_healing_addon = []
    else:
        extensions = json_data['usedExtensions']
        for extension in extensions:
            if extension['name'] == "Healing Stats":
                players_running_healing_addon = extension['runningExtension']

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
    dist_to_com = []


    if "Detailed WvW" in fight_name or "World vs World" in fight_name:
        log_type = "WVW"
        fight_name = fight_name.split(" - ")[1]
    else:
        log_type = "PVE"


    #Initialize fight_num stats
    top_stats['fight'][fight_num] = {
        'fight_date': fight_date,
        'fight_end': fight_end,
        'fight_utc': fight_utc,
        'fight_duration': fight_duration,
        'fight_durationMS': fight_duration_ms,
        'commander': "",
        'squad_count': 0,
        'non_squad_count': 0,
        'enemy_count': 0,
        'enemy_Red': 0,
        'enemy_Green': 0,
        'enemy_Blue': 0,
        'enemy_Unk': 0,
        'parties_by_fight': {},
    }
    
    #collect player counts and parties
    get_parties_by_fight(fight_num, players)

    #collect enemy counts and team colors
    get_enemies_by_fight(fight_num, targets)

    #collect buff data
    get_buffs_data(buff_map)

    #collect skill data
    get_skills_data(skill_map) 

    #collect damage mods data
    get_damage_mods_data(damage_mod_map)

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
            if stat_cat == 'rotation':
                get_skill_cast_by_prof_role(active_time, player, stat_cat, name_prof)

            if stat_cat in ['extHealingStats', 'extBarrierStats']:
                if name in players_running_healing_addon:
                    get_healStats_data(fight_num, player, players, stat_cat, name_prof)
                    get_healstats_skills(player, stat_cat, name_prof)

for filename in sorted_files:
    
    # skip files of incorrect filetype
    file_start, file_extension = os.path.splitext(filename)
    # if args.filetype not in file_extension or "top_stats" in file_start:
    if file_extension not in ['.json', '.gz'] or "top_stats" in file_start:
        continue

    print_string = "parsing " + filename
    print(print_string)
    file_path = "".join((input_directory, "/", filename))

    fight_num += 1
    
    parse_file(file_path, fight_num)

print("Parsing Complete")



json_dict = {}
json_dict["overall_raid_stats"] = {key: value for key, value in top_stats['overall'].items()}
json_dict["fights"] = {key: value for key, value in top_stats['fight'].items()}
json_dict["parties_by_fight"] = {key: value for key, value in top_stats["parties_by_fight"].items()}
json_dict["players"] = {key: value for key, value in top_stats['player'].items()}
json_dict["buff_data"] = {key: value for key, value in buff_data.items()}
json_dict["skill_data"] = {key: value for key, value in skill_data.items()}
json_dict["damage_mod_data"] = {key: value for key, value in damage_mod_data.items()}
json_dict["skill_casts_by_role"] = {key: value for key, value in top_stats["skill_casts_by_role"].items()}


with open(args.json_output_filename, 'w') as json_file:
    json.dump(json_dict, json_file, indent=4)

print("JSON File Complete : "+args.json_output_filename)

defense_stats = config_output.defenses_table
build_category_summary_table(top_stats, defense_stats)

support_stats = config_output.support_table
build_category_summary_table(top_stats, support_stats)

offensive_stats = config_output.offensive_table
build_category_summary_table(top_stats, offensive_stats)

boons = config_output.boons

build_uptime_summary(top_stats, boons, buff_data, "Boon")

boon_categories = {"selfBuffs", "groupBuffs", "squadBuffs"}
for boon_category in boon_categories:
    build_boon_summary(top_stats, boons, boon_category, buff_data)

#get conditions found and output table
conditions = config_output.buffs_conditions
condition_list = {}
for condition in conditions:
    if condition in top_stats["overall"]["buffUptimes"]:
        if top_stats["overall"]["buffUptimes"][condition]["uptime_ms"] > 0:
            condition_list[condition] = conditions[condition]
build_uptime_summary(top_stats, condition_list, buff_data, "Condition")

#get support buffs found and output table
support_buffs = config_output.buffs_support
support_buff_list = {}
for buff in support_buffs:
     if buff in top_stats["overall"]["buffUptimes"]:
         if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
              support_buff_list[buff] = support_buffs[buff]
build_uptime_summary(top_stats, support_buff_list, buff_data, "Support Buff")

#get defensive buffs found and output table
defensive_buffs = config_output.buffs_defensive
defensive_buff_list = {}
for buff in defensive_buffs:
     if buff in top_stats["overall"]["buffUptimes"]:
         if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
              defensive_buff_list[buff] = defensive_buffs[buff]
build_uptime_summary(top_stats, defensive_buff_list, buff_data, "Defensive Buff")

offensive_buffs = config_output.buffs_offensive
offensive_buff_list = {}
for buff in offensive_buffs:
     if buff in top_stats["overall"]["buffUptimes"]:
         if top_stats["overall"]["buffUptimes"][buff]["uptime_ms"] > 0:
              offensive_buff_list[buff] = offensive_buffs[buff]
build_uptime_summary(top_stats, offensive_buff_list, buff_data, "Offensive Buff")