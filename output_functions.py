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


def build_category_summary_table(top_stats, categpry_stats):
    """Print a table of defense stats for all players in the log."""

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !Fight Time (s) | !Active Time (s) |"
    for stat in categpry_stats:
        header += " !{{"+f"{stat}"+"}} |"
    header += "h"

    # Build the table body
    rows = []
    for player in top_stats["player"].values():
        row = f"|{player['name']}"+" | {{"+f"{player['profession']}"+"}} |"+f"{player['account']} | {player['fight_time'] / 1000:.2f}| {player['active_time'] / 1000:.2f}|"
        for stat in categpry_stats:
            cat = categpry_stats[stat]

            if "Time" in stat:
                stat_value = round(player[cat].get(stat, 0),1)
            elif stat == "criticalRate":
                critical_rate = player[cat].get(stat, 0)
                critable_direct_damage_count = player[cat].get("critableDirectDamageCount", 0)
                critical_rate_percentage = round((critical_rate / critable_direct_damage_count) * 100, 1)
                stat_value = f"{critical_rate_percentage}%"
            elif stat == "flankingRate":
                flanking_rate = player[cat].get(stat, 0)
                connected_direct_damage_count = player[cat].get("connectedDirectDamageCount", 0)
                flanking_rate_percentage = round((flanking_rate / connected_direct_damage_count) * 100, 1)
                stat_value = f"{flanking_rate_percentage}%"
            elif stat == "glanceRate":
                glance_rate = player[cat].get(stat, 0)
                connected_direct_damage_count = player[cat].get("connectedDirectDamageCount", 0)
                glance_rate_percentage = round((glance_rate / connected_direct_damage_count) * 100, 1)
                stat_value = f"{glance_rate_percentage}%"
            elif stat == "againstMovingRate":
                against_moving_rate = player[cat].get(stat, 0)
                connected_damage_count = player[cat].get("connectedDamageCount", 0)
                against_moving_rate_percentage = round((against_moving_rate / connected_damage_count) * 100, 1)
                stat_value = f"{against_moving_rate_percentage}%"
            else:
                stat_value = player[cat].get(stat, 0)
                stat_value = f"{stat_value:,}"

            row += f" {stat_value}|"
        rows.append(row)

    # Print the table
    print(header)
    print("\n".join(rows))
        