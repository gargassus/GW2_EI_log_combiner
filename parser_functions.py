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

# Top stats dictionary to store combined log data
top_stats = config.top_stats

team_colors = config.team_colors

# Buff and skill data collected from al logs
buff_data = {}
skill_data = {}
damage_mod_data = {}
personal_damage_mod_data = {
    "total": [],
}

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
    if "Detailed WvW" in fight_name or "World vs World" in fight_name:
        # WVW log
        log_type = "WVW"
        fight_name = fight_name.split(" - ")[1]
    else:
        # PVE log
        log_type = "PVE"
    return log_type, fight_name


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


def get_damage_mods_data(damage_mod_map: dict) -> None:
    """
    Collect damage mod data across all fights.

    Args:
        damage_mod_map (dict): The dictionary of damage mod data.
    """
    for mod in damage_mod_map:
        mod_id = mod[1:]
        name = damage_mod_map[mod]['name']
        icon = damage_mod_map[mod]['icon']
        if mod_id not in damage_mod_data:
            damage_mod_data[mod_id] = {
                'name': name,
                'icon': icon
            }


def get_personal_mod_data(personal_damage_mods: dict) -> None:
    for profession, mods in personal_damage_mods.items():
        if profession not in personal_damage_mod_data:
            personal_damage_mod_data[profession] = []
        for mod_id in mods:
            if mod_id not in personal_damage_mod_data[profession]:
                personal_damage_mod_data[profession].append(mod_id)
                personal_damage_mod_data['total'].append(mod_id)

def get_enemies_by_fight(fight_num: int, targets: list) -> None:
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
    role = 'Imp_Role'
    prof_role = profession + ' {{' + role + '}}'
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

def get_healstats_skills(player: dict, stat_category: str, name_prof: str) -> None:
    """
    Collect data for extHealingStats and extBarrierStats

    Args:
        player (dict): The player dictionary.
        stat_category (str): The category of stats to collect.
        name_prof (str): The name of the profession.
    """
    if stat_category == 'extHealingStats' and 'extHealingStats' in player:
        healing_skill_data = player[stat_category]['alliedHealingDist']
    if stat_category == 'extBarrierStats' and 'extBarrierStats' in player:
        healing_skill_data = player[stat_category]['alliedBarrierDist']

        if healing_skill_data:
            for heal_target in healing_skill_data:
                for skill in heal_target[0]:
                    skill_id = skill['id']
                    skill_hits = skill['hits']
                    skill_min = skill['min']
                    skill_max = skill['max']

                    if 'skills' not in top_stats['player'][name_prof][stat_category]:
                        top_stats['player'][name_prof][stat_category]['skills'] = {}

                    if skill_id not in top_stats['player'][name_prof][stat_category]['skills']:
                        top_stats['player'][name_prof][stat_category]['skills'][skill_id] = {}

                    top_stats['player'][name_prof][stat_category]['skills'][skill_id]['hits'] = (
                        top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('hits', 0) + skill_hits
                    )

                    current_min = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('min', 0)
                    current_max = top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('max', 0)

                    if skill_min < current_min or current_min == 0:
                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['min'] = skill_min
                    if skill_max > current_max or current_max == 0:
                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['max'] = skill_max

                    if stat_category == 'extHealingStats':

                        skill_total_healing = skill['totalHealing']
                        skill_downed_healing = skill['totalDownedHealing']
                        skill_healing = skill_total_healing - skill_downed_healing

                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['totalHealing'] = (
                            top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('totalHealing', 0) + skill_total_healing
                        )

                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['downedHealing'] = (
                            top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('downedHealing', 0) + skill_downed_healing
                        )

                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['healing'] = (
                            top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('healing', 0) + skill_healing
                        )

                    else:

                        skill_total_barrier = skill['totalBarrier']

                        top_stats['player'][name_prof][stat_category]['skills'][skill_id]['totalBarrier'] = (
                            top_stats['player'][name_prof][stat_category]['skills'][skill_id].get('totalBarrier', 0) + skill_total_barrier
                        )

def get_damage_mod_by_player(fight_num: int, player: dict, name_prof: str) -> None:
    if 'damageModifiers' in player:

        for modifier in player['damageModifiers']:
            mod_id = modifier['id']
            mod_hit_count = modifier['damageModifiers'][0]['hitCount']
            mod_total_hit_count = modifier['damageModifiers'][0]['totalHitCount']
            mod_damage_gain = modifier['damageModifiers'][0]['damageGain']
            mod_total_damage = modifier['damageModifiers'][0]['totalDamage']

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
