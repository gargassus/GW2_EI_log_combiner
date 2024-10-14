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

#tid file template
temp_tid = {
    'created': 20130308044406417,
    'creator': "Drevarr",
    'modified': 20240523132529893,
    'modifier': "Drevarr",
    'tags': [],
    'title': "",
    'text': ""
}


def create_new_tid_from_template() -> dict:
    """Create a new TID from the template."""
    return {key: value for key, value in temp_tid.items()}


#append new tid to list
#tid_list.append(create_new_tid_from_template)


def write_tid_list_to_json(tid_list):
    """
    Write the list of tid files to a json file
    """
    with open('tid_list.json', 'w') as outfile:
        json.dump(tid_list, outfile, indent=4, sort_keys=True)


def build_stat_table(top_stats):
    pass


def build_overall_summary(top_stats):
    pass


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


def build_fight_summary(top_stats, overview_stats):
    """Build a summary of the top stats for each fight."""
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|# |Location |End Time | Duration| Squad | Allies | Enemy | R/G/B | Downs | Kills | Downed | Deaths | Damage Out| Damage In| Barrier Damage| Barrier % | Shield Damage| Shield % |h"

    print(header)

    rows = []

    for fight_num, fight_data in top_stats["fight"].items():
        row=""
        total_shield_damage = get_total_shield_damage(fight_data)

        row+=(f"|{fight_num} |{fight_data['fight_name']} |{fight_data['fight_end']} | {fight_data['fight_duration']}| {fight_data['squad_count']} | {fight_data['non_squad_count']} | {fight_data['enemy_count']} ")
        row+=(f"| {fight_data['enemy_Red']}/{fight_data['enemy_Green']}/{fight_data['enemy_Blue']} | {fight_data['statsTargets']['downed']} | {fight_data['statsTargets']['killed']} ")
        row+=(f"| {fight_data['defenses']['downCount']} | {fight_data['defenses']['deadCount']} | {fight_data['statsTargets']['totalDmg']:,}| {fight_data['defenses']['damageTaken']:,}")
        row+=(f"| {fight_data['defenses']['damageBarrier']:,}| {(fight_data['defenses']['damageBarrier'] / fight_data['defenses']['damageTaken'] * 100):.2f}%| {total_shield_damage:,}")
        shield_damage_pct = (total_shield_damage / fight_data['statsTargets']['totalDmg'] * 100)
        row+=(f"| {shield_damage_pct:.2f}%|")

        #print("".join(row))
        rows.append(row)

    print("\n".join(rows))

def build_category_summary_table(top_stats: dict, category_stats: dict) -> None:
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
        row = f"|{player['name']} | {{ {player['profession']} }} | {player['account']} | {player['fight_time'] / 1000:.2f}| {player['active_time'] / 1000:.2f}|"

        for stat, category in category_stats.items():
            stat_value = player[category].get(stat, 0)

            if stat in pct_stats:
                divisor_value = player[category].get(pct_stats[stat], 0)
                stat_value_percentage = round((stat_value / divisor_value) * 100, 1)
                stat_value = f"{stat_value_percentage:.2f}%"
            else:
                stat_value = f"{stat_value:,}"
            row += f" {stat_value} |"

        rows.append(row)

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
