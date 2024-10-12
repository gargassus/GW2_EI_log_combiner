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
        header += f" !{{ {stat} }} |"
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
                stat_value = f"{stat_value_percentage}%"
            else:
                stat_value = f"{stat_value:,}"
            row += f" {stat_value} |"

        rows.append(row)

    # Print the table
    print(header)
    print("\n".join(rows))
