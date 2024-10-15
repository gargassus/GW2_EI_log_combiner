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
import config_output


#list of tid files to output
tid_list = []

def create_new_tid_from_template(title, caption, text, tags=None, modified=None) -> dict:
    """Create a new TID from the template."""
    temp_tid = {}
    temp_tid['title'] = title
    temp_tid['caption'] = caption
    temp_tid['text'] = text
    if tags:
        temp_tid['tags'] = tags
    if modified:
        temp_tid['modified'] = modified

    return temp_tid

def append_tid_for_output(input, output):
    output.append(input)
    print(input['title']+' .tid has been created.')


def write_tid_list_to_json(tid_list):
    """
    Write the list of tid files to a json file
    """
    with open('tid_list.json', 'w') as outfile:
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
    duration_parts.append(f"{seconds:02}s, {milliseconds:03}ms")

    return ", ".join(duration_parts)


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
    tag_summary = {}

    for fight, fight_data in top_stats["fight"].items():
        if fight_data["commander"] not in tag_summary:
            tag_summary[fight_data["commander"]] = {
                "num_fights": 0,
                "fight_time": 0,
                "kills": 0,
                "downs": 0,
                "downed": 0,
                "deaths": 0,
                "KDR": 0,
            }

        tag_summary[fight_data["commander"]]["num_fights"] += 1
        tag_summary[fight_data["commander"]]["fight_time"] += fight_data["fight_durationMS"]
        tag_summary[fight_data["commander"]]["kills"] += fight_data["statsTargets"]["killed"]
        tag_summary[fight_data["commander"]]["downs"] += fight_data["statsTargets"]["downed"]
        tag_summary[fight_data["commander"]]["downed"] += fight_data["defenses"]["downCount"]
        tag_summary[fight_data["commander"]]["deaths"] += fight_data["defenses"]["deadCount"]

    return tag_summary


def output_tag_summary(tag_summary):
    print("|Name | Prof | Fights | Downs | Kills | Downed | Deaths | KDR |")
    for key, value in tag_summary.items():
        Name=key.split("|")[0]
        Profession="{{"+key.split("|")[1]+"}}"
        if value['deaths'] == 0:
            KDR = value['kills'] 
        else:
            KDR = value['kills'] / value['deaths']
        print(
            f"|{Name} | {Profession} | {value['num_fights']} | {value['downs']} | {value['kills']} | {value['downed']} | {value['deaths']} | {KDR:.2f}|"
        )

    #sum all tags
    total_fights = 0
    total_fight_time = 0
    total_kills = 0
    total_downs = 0
    total_downed = 0
    total_deaths = 0
    for key, value in tag_summary.items():
        total_fights += value['num_fights']
        total_fight_time += value['fight_time']
        total_kills += value['kills']
        total_downs += value['downs']
        total_downed += value['downed']
        total_deaths += value['deaths']

    print(
        f"|Totals |<| {total_fights} | {total_downs} | {total_kills} | {total_downed} | {total_deaths} | {total_kills/total_deaths:.2f}|"
    )


def build_fight_summary(top_stats, overview_stats):
    """Build a summary of the top stats for each fight."""
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += f"| {overview_stats} |c\n"
    header += "|# |Location |End Time | Duration| Squad | Allies | Enemy | R/G/B | Downs | Kills | Downed | Deaths | Damage Out| Damage In| Barrier Damage| Barrier % | Shield Damage| Shield % |h"

    print(header)

    rows = []
    last_fight = 0
    last_end = ""
    total_durationMS = 0
    
    avg_squad_count, avg_ally_count, avg_enemy_count = calculate_average_squad_count(top_stats["fight"].values())
    squad_down = top_stats['overall']['defenses']['downCount']
    squad_dead = top_stats['overall']['defenses']['deadCount']
    enemy_downed = top_stats['overall']['statsTargets']['downed']
    enemy_killed = top_stats['overall']['statsTargets']['killed']
    total_damage_out = top_stats['overall']['statsTargets']['totalDmg']
    total_damage_in = top_stats['overall']['defenses']['damageTaken']
    total_barrier_damage = top_stats['overall']['defenses']['damageBarrier']
    total_shield_damage = get_total_shield_damage(top_stats['overall'])
    total_shield_damage_percent = (total_shield_damage / total_damage_out) * 100
    total_barrier_damage_percent = (total_barrier_damage / total_damage_in) * 100

    for fight_num, fight_data in top_stats["fight"].items():
        row=""
        fight_shield_damage = get_total_shield_damage(fight_data)

        row+=(f"|{fight_num} |{fight_data['fight_name']} |{fight_data['fight_end']} | {fight_data['fight_duration']}| {fight_data['squad_count']} | {fight_data['non_squad_count']} | {fight_data['enemy_count']} ")
        row+=(f"| {fight_data['enemy_Red']}/{fight_data['enemy_Green']}/{fight_data['enemy_Blue']} | {fight_data['statsTargets']['downed']} | {fight_data['statsTargets']['killed']} ")
        row+=(f"| {fight_data['defenses']['downCount']} | {fight_data['defenses']['deadCount']} | {fight_data['statsTargets']['totalDmg']:,}| {fight_data['defenses']['damageTaken']:,}")
        row+=(f"| {fight_data['defenses']['damageBarrier']:,}| {(fight_data['defenses']['damageBarrier'] / fight_data['defenses']['damageTaken'] * 100):.2f}%| {fight_shield_damage:,}")
        shield_damage_pct = (fight_shield_damage / fight_data['statsTargets']['totalDmg'] * 100)
        row+=(f"| {shield_damage_pct:.2f}%|")
        last_fight = fight_num
        last_end = fight_data['fight_end']
        total_durationMS += fight_data['fight_durationMS']

        #print("".join(row))
        rows.append(row)

    raid_duration = convert_duration(total_durationMS)
    footer = f"|Total FIghts: {last_fight}|<|{last_end} | {raid_duration}| {avg_squad_count:.1f} | {avg_ally_count:.1f} | {avg_enemy_count:.1f} |     | {squad_down} | {squad_dead} | {enemy_downed} | {enemy_killed} | {total_damage_out:,}| {total_damage_in:,}| {total_barrier_damage:,}| {total_shield_damage_percent:.2f}%| {total_shield_damage:,}| {total_barrier_damage_percent:.2f}%|f"
    rows.append(footer)
    print("\n".join(rows))


def build_damage_summary_table(top_stats: dict, caption: str) -> None:
    """
    Print a table of damage stats for all players in the logs.

    Args:
        top_stats (dict): The top_stats dictionary containing the overall stats.

    Returns:
        None
    """

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += f"| {caption} |c\n"
    header += "|!Name | !Prof |!Account | !Fight Time (s) | !Active Time (s) |"
    header += " !{{Target_Damage}}| !{{Target_Power}} | !{{Target_Condition}} | !{{Target_Breakbar_Damage}} | !{{All_Damage}}| !{{All_Power}} | !{{All_Condition}} | !{{All_Breakbar_Damage}} |h"

    rows = []

    # Build the table body
    for player, player_data in top_stats["player"].items():
        row = f"|{player_data['name']} |"+" {{"+f"{player_data['profession']}"+"}} "+f"| {player_data['account']} | {player_data['fight_time'] / 1000:.2f}| {player_data['active_time'] / 1000:.2f}|"
        row += " {:,} | {:,}| {:,}| {:,}| {:,}| {:,}| {:,}| {:,}|".format(
            player_data["dpsTargets"]["damage"],
            player_data["dpsTargets"]["powerDamage"],
            player_data["dpsTargets"]["condiDamage"],
            player_data["dpsTargets"]["breakbarDamage"],
            player_data["statsAll"]["totalDmg"],
            player_data["statsAll"]["directDmg"],
            player_data["statsAll"]["totalDmg"] - player_data["statsAll"]["directDmg"],
            player_data["dpsTargets"]["breakbarDamage"],
        )

        rows.append(row)

    # Print the table
    print(header)
    print("\n".join(rows))


   
def build_category_summary_table(top_stats: dict, category_stats: dict, caption: str) -> None:
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
    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !Fight Time (s) | !Active Time (s) |"
    for stat in category_stats:
        header += " !{{"+f"{stat}"+"}} |"
    header += "h"

    # Build the table body
    rows = []
    for player in top_stats["player"].values():
        row = f"|{player['name']} | {{{{{player['profession']}}}}} | {player['account']} | {player['fight_time'] / 1000:.2f}| {player['active_time'] / 1000:.2f}|"

        for stat, category in category_stats.items():
            stat_value = player[category].get(stat, 0)
            #print(stat, stat_value, player['name'])
            if stat in pct_stats:
                divisor_value = player[category].get(pct_stats[stat], 0)
                if divisor_value == 0:
                    divisor_value = 1
                stat_value_percentage = round((stat_value / divisor_value) * 100, 1)
                stat_value = f"{stat_value_percentage:.2f}%"
            else:
                stat_value = f"{stat_value:,.1f}"
            row += f" {stat_value} |"

        rows.append(row)
    rows.append(f"|{caption} Uptime Table|c")
    # Print the table
    print(header)
    print("\n".join(rows))


def build_boon_summary(top_stats: dict, boons: dict, category: str, buff_data: dict) -> None:
    """Print a table of boon uptime stats for all players in the log."""

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !Fight Time (s) | !Active Time (s) |"
    for boon_id, boon_name in boons.items():
        header += " !{{"+f"{boon_name}"+"}} |"
    header += "h"

    # Build the table body
    rows = []

    for player in top_stats["player"].values():
        row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"| {player['account']} | {player['fight_time'] / 1000:.2f}| {player['active_time'] / 1000:.2f}|"

        for boon_id in boons:
            boon_id = str(boon_id)

            if boon_id not in player[category]:
                uptime_percentage = " - "
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
                else:
                    raise ValueError(f"Invalid category: {category}")
                
                if stacking:
                    if uptime_percentage:
                        uptime_percentage = f"{uptime_percentage:.1f}"
                    else:
                        uptime_percentage = " - "
                else:
                    if uptime_percentage:
                        uptime_percentage = f"{uptime_percentage:.1f}%"
                    else:
                        uptime_percentage = " - "

            row += f" {uptime_percentage} |"
        rows.append(row)
    rows.append(f"|{category} Table|c")
    print(header)
    print("\n".join(rows))


def build_uptime_summary(top_stats: dict, boons: dict, buff_data: dict, caption: str) -> None:
    """Print a table of boon uptime stats for all players in the log."""

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !Fight Time (s) | !Active Time (s) |"
    for boon_id, boon_name in boons.items():
        skillIcon = buff_data[str(boon_id)]["icon"]

        #"|[img width=24 ["+skillIcon+"]] "+skill+"
        #header += " !{{"+f"{boon_name}"+"}} |"
        header += f"![img width=24 [{boon_name}|{skillIcon}]] |"
    header += "h"

    # Build the table body
    rows = []
    for player in top_stats["player"].values():
        row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"| {player['account']} | {player['fight_time'] / 1000:.2f}| {player['active_time'] / 1000:.2f}|"
        for boon_id in boons:
            if boon_id not in player["buffUptimes"]:
                uptime_percentage = " - "
            else:
                uptime_ms = player["buffUptimes"][boon_id]["uptime_ms"]
                uptime_percentage = round(uptime_ms / player['fight_time'] * 100, 3)
                uptime_percentage = f"{uptime_percentage:.2f}%"
            row += f" {uptime_percentage} |"
        rows.append(row)
    rows.append(f"|{caption} Uptime Table|c")
    print(header)
    print("\n".join(rows))

