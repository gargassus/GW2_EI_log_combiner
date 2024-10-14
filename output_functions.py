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
    pass


def build_fight_summary(top_stats):
    pass


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
                        uptime_percentage = f"{uptime_percentage:.2f}"
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
