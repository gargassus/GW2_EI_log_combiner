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


# Elite Insights json stat categories
json_stats = [
    "defenses",
    "support",
    "statsAll",
    "statsTargets",
    "targetDamageDist",
    "dpsTargets",
    "totalDamageTaken",
    "buffUptimes",
    "buffUptimesActive",
    "squadBuffs",
    "groupBuffs",
    "selfBuffs",
    "squadBuffsActive",
    "groupBuffsActive",
    "selfBuffsActive",
    "rotation",
    "extHealingStats",
    "extBarrierStats",
    "targetBuffs",
    "damageModifiers",
]

# Top stats dictionary to store combined log data
top_stats = {
    "overall": {"last_fight": "", "group_data": {}},
    "fight": {},
    "player": {},
    "parties_by_fight": {},
    "enemies_by_fight": {},
    "skill_casts_by_role": {},
    "players_running_healing_addon": [],
}

# Team colors - team_id:color
team_colors = {
    0: "Unk",
    705: "Red",
    706: "Red",
    882: "Red",
    2520: "Red",
    2739: "Green",
    2741: "Green",
    2752: "Green",
    2763: "Green",
    432: "Blue",
    1277: "Blue",
}


# High scores stats
high_scores = [
    "dodgeCount",
    "evadedCount",
    "blockedCount",
    "invulnedCount",
    "boonStrips",
    "condiCleanse",
    "receivedCrowdControl",
]

#mesmer F_skills
mesmer_shatter_skills = [
"Split Second",
"Rewinder",
"Time Sink",
"Distortion",
"Continuum Split",
"Mind Wrack",
"Cry of Frustration",
"Diversion",
"Distortion",
"Geistiges Wrack",
"Schrei der Frustration",
"Ablenkung",
"Verzerrung",
"Sekundenbruchteil",
"R\u00FCckspuler",
"Zeitfresser",
"Kontinuum-Spaltung"
]