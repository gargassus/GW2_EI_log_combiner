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

# Elite Insight json stat categories
json_stats = [
    'defenses', 'support', 'statsAll',
    'statsTargets', 'targetDamageDist', 'dpsTargets',
    'totalDamageTaken', 'buffUptimes', 'buffUptimesActive',
    'squadBuffs', 'groupBuffs', 'selfBuffs',
    'squadBuffsActive', 'groupBuffsActive', 'selfBuffsActive',
]

# Top stats dictionary to store combined log data
top_stats = {
    'overall': {},
    'fight': {},
    'player': {},
    'parties_by_fight': {},
    'skill_casts_by_role': {}
}

# Team colors - team_id:color
team_colors = {
    705: 'Red', 
    706: 'Red', 
    882: 'Red', 
    2520: 'Red', 
    2739: 'Green', 
    2741: 'Green', 
    2752: 'Green', 
    2763: 'Green', 
    432: 'Blue', 
    1277: 'Blue'
    }