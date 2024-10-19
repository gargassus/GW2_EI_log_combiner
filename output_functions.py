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

def create_new_tid_from_template(title, caption, text, tags=None, modified=None, created=None, creator=None) -> dict:
    """Create a new TID from the template."""
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

    return temp_tid

def append_tid_for_output(input, output):
    output.append(input)
    print(input['title']+'.tid has been created.')

def write_tid_list_to_json(tid_list, output_filename):
    """
    Write the list of tid files to a json file
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
                "kills": 0,
                "downs": 0,
                "downed": 0,
                "deaths": 0,
            }

        tag_summary[commander]["num_fights"] += 1
        tag_summary[commander]["fight_time"] += fight_data["fight_durationMS"]
        tag_summary[commander]["kills"] += fight_data["statsTargets"]["killed"]
        tag_summary[commander]["downs"] += fight_data["statsTargets"]["downed"]
        tag_summary[commander]["downed"] += fight_data["defenses"]["downCount"]
        tag_summary[commander]["deaths"] += fight_data["defenses"]["deadCount"]

    return tag_summary

def output_tag_summary(tag_summary: dict, tid_date_time) -> None:
    """Output a summary of the tag data in a human-readable format."""
    rows = []
    rows.append("|thead-dark table-caption-top table-hover sortable|k")
    rows.append("| Summary by Command Tag |c")
    rows.append(
        "|Name | Prof | Fights | {{DownedEnemy}} | {{killed}} | {{DownedAlly}} | {{DeadAlly}} | KDR |h"
    )
    for tag, tag_data in tag_summary.items():
        name = tag.split("|")[0]
        profession = "{{"+tag.split("|")[1]+"}}"
        fights = tag_data["num_fights"]
        downs = tag_data["downs"]
        kills = tag_data["kills"]
        downed = tag_data["downed"]
        deaths = tag_data["deaths"]
        kdr = kills / deaths if deaths != 0 else kills
        rows.append(
            f"|{name} | {profession} | {fights} | {downs} | {kills} | {downed} | {deaths} | {kdr:.2f}|"
        )

    # Sum all tags
    total_fights = sum(tag_data["num_fights"] for tag_data in tag_summary.values())
    total_kills = sum(tag_data["kills"] for tag_data in tag_summary.values())
    total_downs = sum(tag_data["downs"] for tag_data in tag_summary.values())
    total_downed = sum(tag_data["downed"] for tag_data in tag_summary.values())
    total_deaths = sum(tag_data["deaths"] for tag_data in tag_summary.values())

    rows.append(
        f"|Totals |<| {total_fights} | {total_downs} | {total_kills} | {total_downed} | {total_deaths} | {total_kills/total_deaths:.2f}|f"
    )

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
        - Location
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

    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += f"| {caption} |c\n"
    header += "|# |Location |End Time | Duration| Squad | Allies | Enemy | R/G/B | {{DownedEnemy}} | {{killed}} | {{DownedAlly}} | {{DeadAlly}} | {{Damage}} | {{Damage Taken}} | {{damageBarrier}} | {{damageBarrier}} % | {{damageShield}} | {{damageShield}} % |h"

    rows.append(header)

    
    last_fight = 0
    last_end = ""
    total_durationMS = 0
    
    # Calculate average squad count
    avg_squad_count, avg_ally_count, avg_enemy_count = calculate_average_squad_count(top_stats["fight"].values())
    # Get the total downs, deaths, and damage out/in/barrier/shield
    enemy_downed = top_stats['overall']['defenses']['downCount']
    enemy_killed = top_stats['overall']['defenses']['deadCount']
    squad_down = top_stats['overall']['statsTargets']['downed']
    squad_dead = top_stats['overall']['statsTargets']['killed']
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
        # Build the row
        row += f"|{fight_num} |{fight_data['fight_name']} |{fight_data['fight_end']} | {fight_data['fight_duration']}| {fight_data['squad_count']} | {fight_data['non_squad_count']} | {fight_data['enemy_count']} "
        row += f"| {fight_data['enemy_Red']}/{fight_data['enemy_Green']}/{fight_data['enemy_Blue']} | {fight_data['statsTargets']['downed']} | {fight_data['statsTargets']['killed']} "
        row += f"| {fight_data['defenses']['downCount']} | {fight_data['defenses']['deadCount']} | {fight_data['statsTargets']['totalDmg']:,}| {fight_data['defenses']['damageTaken']:,}"
        row += f"| {fight_data['defenses']['damageBarrier']:,}| {(fight_data['defenses']['damageBarrier'] / fight_data['defenses']['damageTaken'] * 100):.2f}%| {fight_shield_damage:,}"
        # Calculate the shield damage percentage
        shield_damage_pct = (fight_shield_damage / fight_data['statsTargets']['totalDmg'] * 100)
        row += f"| {shield_damage_pct:.2f}%|"
        # Keep track of the last fight number, end time, and total duration
        last_fight = fight_num
        last_end = fight_data['fight_end']
        total_durationMS += fight_data['fight_durationMS']

        rows.append(row)

    raid_duration = convert_duration(total_durationMS)
    # Build the footer
    footer = f"|Total Fights: {last_fight}|<|{last_end} | {raid_duration}| {avg_squad_count:.1f},,avg,,| {avg_ally_count:.1f},,avg,,| {avg_enemy_count:.1f},,avg,,|     | {squad_down} | {squad_dead} | {enemy_downed} | {enemy_killed} | {total_damage_out:,}| {total_damage_in:,}| {total_barrier_damage:,}| {total_shield_damage_percent:.2f}%| {total_shield_damage:,}| {total_barrier_damage_percent:.2f}%|f"
    rows.append(footer)
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

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += f"| {caption} |c\n"
    header += "|!Name | !Prof |!Account | !{{FightTime}} |"
    header += " !{{Target_Damage}}| !{{Target_Power}} | !{{Target_Condition}} | !{{Target_Breakbar_Damage}} | !{{All_Damage}}| !{{All_Power}} | !{{All_Condition}} | !{{All_Breakbar_Damage}} |h"

    rows.append(header)

    # Build the table body
    for player, player_data in top_stats["player"].items():
        row = f"|{player_data['name']} |"+" {{"+f"{player_data['profession']}"+"}} "+f"|{player_data['account'][:30]} | {player_data['fight_time'] / 1000:.1f}|"
        row += " {:,}| {:,}| {:,}| {:,}| {:,}| {:,}| {:,}| {:,}|".format(
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
    #print(header)
    #print("\n".join(rows))

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
    rows = []
    pct_stats = {
        "criticalRate": "critableDirectDamageCount", "flankingRate":"connectedDirectDamageCount", "glanceRate":"connectedDirectDamageCount", "againstMovingRate": "connectedDamageCount"
    }
    time_stats = ["resurrectTime", "condiCleanseTime", "condiCleanseTimeSelf", "boonStripsTime", "removedStunDuration"]
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

        for stat, category in category_stats.items():
            stat_value = player[category].get(stat, 0)

            if stat in pct_stats:
                divisor_value = player[category].get(pct_stats[stat], 0)
                if divisor_value == 0:
                    divisor_value = 1
                stat_value_percentage = round((stat_value / divisor_value) * 100, 1)
                stat_value = f"{stat_value_percentage:.2f}%"
            elif stat in time_stats:
                stat_value = f"{stat_value:,.1f}"
            else:
                stat_value = f"{stat_value:,}"
            row += f" {stat_value}|"

        rows.append(row)
    rows.append(f"|{caption} Table|c")

    #push table to tid_list for output
    tid_text = "\n".join(rows)

    append_tid_for_output(
        create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ', '-')}", caption, tid_text),
        tid_list
        )

def build_boon_summary(top_stats: dict, boons: dict, category: str, buff_data: dict, tid_date_time: str) -> None:
    """Print a table of boon uptime stats for all players in the log."""

    # Build the table header
    rows = []
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !{{FightTime}} |"
    for boon_id, boon_name in boons.items():
        header += "!{{"+f"{boon_name}"+"}}|"
    header += "h"

    rows.append(header)

    caption = ""
    # Build the table body
    for player in top_stats["player"].values():
        row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:30]} | {player['fight_time'] / 1000:.1f}|"

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
                    caption = "Self Generation"
                    generation_ms = player[category][boon_id]["generation"]
                    if stacking:
                        uptime_percentage = round((generation_ms / player['fight_time'] / num_fights), 3)
                    else:
                        uptime_percentage = round((generation_ms / player['fight_time'] / num_fights) * 100, 3)
                elif category == "groupBuffs":
                    caption = "Group Generation"
                    generation_ms = player[category][boon_id]["generation"]
                    if stacking:
                        uptime_percentage = round((generation_ms / player['fight_time']) / (group_supported - num_fights), 3)
                    else:
                        uptime_percentage = round((generation_ms / player['fight_time']) / (group_supported - num_fights) * 100, 3)
                elif category == "squadBuffs":
                    caption = "Squad Generation"
                    generation_ms = player[category][boon_id]["generation"]
                    if stacking:
                        uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported - num_fights), 3)
                    else:
                        uptime_percentage = round((generation_ms / player['fight_time']) / (squad_supported - num_fights) * 100, 3)
                elif category == "totalBuffs":
                    caption = "Total Generation"
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
                        uptime_percentage = f"{uptime_percentage:.1f}"
                    else:
                        uptime_percentage = " - "
                else:
                    if uptime_percentage:
                        uptime_percentage = f"{uptime_percentage:.1f}%"
                    else:
                        uptime_percentage = " - "

            row += f" {uptime_percentage}|"
        rows.append(row)
    rows.append(f"|{caption} Table|c")

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
    # Build the Squad table header
    header = "|thead-dark table-caption-top table-hover|k\n"
    header += "|Squad Average Uptime |c\n"
    header += "| |"
    for boon_id, boon_name in boons.items():
        skillIcon = buff_data[str(boon_id)]["icon"]

        header += f"![img width=24 [{boon_name}|{skillIcon}]]|"
    header += "h"
    rows.append(header)

    row = f"|@@display:block;width:360px;Squad Average Uptime@@ |"
    for boon_id in boons:
        if boon_id not in top_stats['overall']["buffUptimes"]:
            uptime_percentage = " - "
        else:
            uptime_ms = top_stats['overall']["buffUptimes"][boon_id]["uptime_ms"]
            uptime_percentage = round((uptime_ms / top_stats['overall']["fight_time"]) * 100, 3)
            uptime_percentage = f"{uptime_percentage:.2f}%"
        row += f" {uptime_percentage}|" 
    row += "f"
    rows.append(row)    
    rows.append("\n\n")

    # Build the player table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !{{FightTime}} |"
    for boon_id, boon_name in boons.items():
        skillIcon = buff_data[str(boon_id)]["icon"]

        header += f"![img width=24 [{boon_name}|{skillIcon}]]|"
    header += "h"

    rows.append(header)

    # Build the table body
    for player in top_stats["player"].values():
        row = f"|{player['name']} |"+" {{"+f"{player['profession']}"+"}} "+f"|{player['account'][:32]} | {player['fight_time'] / 1000:.2f}|"
        for boon_id in boons:
            if boon_id not in player["buffUptimes"]:
                uptime_percentage = " - "
            else:
                uptime_ms = player["buffUptimes"][boon_id]["uptime_ms"]
                uptime_percentage = round(uptime_ms / player['fight_time'] * 100, 3)
                uptime_percentage = f"{uptime_percentage:.2f}%"
            row += f" {uptime_percentage}|"
        rows.append(row)
    rows.append(f"|{caption} Table|c")

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

    # Build the table header
    header = "|thead-dark table-caption-top table-hover sortable|k\n"
    header += "|!Name | !Prof |!Account | !{{FightTime}} | !{{Healing}} | !{{HealingPS}} | !{{Barrier}} | !{{BarrierPS}} | !{{DownedHealing}} | !{{DownedHealingPS}} |h"

    # Build the table body
    rows = [header]
    for healer in sorted_healing_stats:
        fighttime = healer[1]['fight_time'] / 1000
        row = f"|{healer[0]} |"+" {{"+f"{healer[1]['profession']}"+"}} "+f"|{healer[1]['account'][:32]} | {fighttime:.2f}|"
        row += f" {healer[1]['healing']:,}| {healer[1]['healing'] / fighttime:.2f}| {healer[1]['barrier']:,}|"
        row += f"{healer[1]['barrier'] / fighttime:.2f}| {healer[1]['downed_healing']:,}| {healer[1]['downed_healing'] / fighttime:.2f}|"
        rows.append(row)
    rows.append(f"|{caption} Table|c")

    # Push table to tid_list for output
    tid_text = "\n".join(rows)

    append_tid_for_output(
        create_new_tid_from_template(f"{tid_date_time}-{caption.replace(' ','-')}", caption, tid_text),
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


def build_menu_tid(datetime):
    menu_tags = f"{datetime}"
    menu_title = f"{datetime}-Menu"
    menu_caption = f"Menu"

    menu_text = f'<<tabs "[[{datetime}-Overview]] [[{datetime}-General-Stats]] [[{datetime}-Buffs]] [[{datetime}-Damage-Modifiers]] [[{datetime}-Player-Summary]]" "{datetime}-Overview" "$:/state/menutab1">>'

    append_tid_for_output(
        create_new_tid_from_template(menu_title, menu_caption, menu_text, menu_tags),
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
            f"[[{datetime}-Defenses]] [[{datetime}-Support]] [[{datetime}-Heal-Stats]]' "
            f"'{datetime}-Offensive' '$:/state/tab1'>>")

    append_tid_for_output(
        create_new_tid_from_template(title, caption, text, tags, creator=creator),
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
            f"'{datetime}-Shared-Damage-Mods' '$:/state/tab1'>>")

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

    text = (f"<<tabs '[[{datetime}-Boons]] [[{datetime}-Offensive-Buffs]] [[{datetime}-Support-Buffs]] "
            f"[[{datetime}-Defensive-Buffs]] [[{datetime}-Conditions-In]] [[{datetime}-Debuffs-In]]' "
            f"'{datetime}-Boons' '$:/state/tab1'>>")

    append_tid_for_output(
        create_new_tid_from_template(title, caption, text, tags, creator=creator),
        tid_list
    )


def build_boon_stats_tid(datetime):
    buff_stats_tags = f"{datetime}"
    buff_stats_title = f"{datetime}-Boons"
    buff_stats_caption = f"Boons"
    buff_stats_creator = f"Drevarr@github.com"

    buff_stats_text = f"<<tabs '[[{datetime}-Uptimes]] [[{datetime}-Self-Generation]] [[{datetime}-Group-Generation]] [[{datetime}-Squad-Generation]]' '{datetime}-Uptimes' '$:/state/tab1'>>"

    append_tid_for_output(
        create_new_tid_from_template(buff_stats_title, buff_stats_caption, buff_stats_text, buff_stats_tags, creator=buff_stats_creator),
        tid_list
    )


def output_top_stats_json(top_stats: dict, buff_data: dict, skill_data: dict, damage_mod_data: dict, personal_damage_mod_data: dict, outfile: str) -> None:
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
    #personal_damage_mod_data
    json_dict["personal_damage_mod_data"] = {key: value for key, value in personal_damage_mod_data.items()}
    with open(outfile, 'w') as json_file:
        json.dump(json_dict, json_file, indent=4)

    print("JSON File Complete : "+outfile)