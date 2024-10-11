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

tid_list = []

temp_tid = {
    'created': 20130308044406417,
    'creator': "Drevarr",
    'modified': 20240523132529893,
    'modifier': "Drevarr",
    'tags': [],
    'title': "",
    'text': ""
}

tid_list.append(temp_tid)

#export tid_list to json
def write_tid_list_to_json(infile):
    with open('tid_list.json', 'w') as outfile:
        json.dump(infile, outfile)

write_tid_list_to_json()