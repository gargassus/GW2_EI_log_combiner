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


# Output file categories for tabs
test_tabs = ["Damage Stats", "Offensive Stats", "Defensive Stats", "Support Stats", "Healing Stats"]

overview_stats = {
	"fight": "Fight",
	"fight_name": "Location",
	"fight_end": "End Time",
	"fight_duration": "Duration",
	"squad_count": "Squad",
	"non_squad_count": "Allies",
	"enemy_count": "Enemy",
	"enemy_Red": "Red Team",
	"enemy_Green": "Green Team",
	"enemy_Blue": "Blue Team",
	"downed": "Downs",
	"killed": "Kills",
	"downCount":"Downed",
	"deadCount":"Deaths",
	"totalDmg": "Damage Out",
	"damageTaken": "Damage In",
	"damageBarrier": "Barrier Damage",
	"barrierPCT": "Barrier %",
	"total_shield_damage": "Shield Damage",
	"shieldPCT": "Shield %"
}

defenses_table = {
	"damageTaken": 'defenses',
	"damageTakenCount": 'defenses',
	"conditionDamageTaken": 'defenses',
	"conditionDamageTakenCount": 'defenses',
	"powerDamageTaken": 'defenses',
	"powerDamageTakenCount": 'defenses',
	#"strikeDamageTaken": 'defenses',
	#"strikeDamageTakenCount": 'defenses',
	#"lifeLeechDamageTaken": 'defenses',
	#"lifeLeechDamageTakenCount": 'defenses',
	"downedDamageTaken": 'defenses',
	"downedDamageTakenCount": 'defenses',
	"damageBarrier": 'defenses',
	"damageBarrierCount": 'defenses',
	#"breakbarDamageTaken": 'defenses',
	#"breakbarDamageTakenCount": 'defenses',
	"blockedCount": 'defenses',
	"evadedCount": 'defenses',
	"missedCount": 'defenses',
	"dodgeCount": 'defenses',
	"invulnedCount": 'defenses',
	"interruptedCount": 'defenses',
	"downCount": 'defenses',
	#"downDuration": 'defenses',
	"deadCount": 'defenses',
	#"deadDuration": 'defenses',
	#"dcCount": 'defenses',
	#"dcDuration": 'defenses',
	"boonStrips": 'defenses',
	#"boonStripsTime": 'defenses',
	"conditionCleanses": 'defenses',
	#"conditionCleansesTime": 'defenses',
	"receivedCrowdControl": 'defenses',
	#"receivedCrowdControlDuration": 'defenses',
}

support_table = {
	"condiCleanse": 'support',
	"condiCleanseTime": 'support',
	"condiCleanseSelf": 'support',
	"condiCleanseTimeSelf": 'support',
	"boonStrips": 'support',
	"boonStripsTime": 'support',
    "boonStripDownContribution": 'support',
	"boonStripDownContributionTime": 'support',
	"stunBreak": 'support',
	"removedStunDuration": 'support',
	"resurrects": 'support',
	"resurrectTime": 'support'
}

offensive_table = {
    #"totalDamageCount": 'statsTargets',
    "damage": 'dpsTargets',
    #"directDamageCount": 'statsTargets',
    "directDmg": 'statsTargets',
    "connectedDamageCount": 'statsTargets',
    "connectedDirectDamageCount": 'statsTargets',
    #"connectedDirectDmg": 'statsTargets',
    #"connectedDmg": 'statsTargets',
    #"critableDirectDamageCount": 'statsTargets',
    "criticalRate": 'statsTargets',
    "criticalDmg": 'statsTargets',
    "flankingRate": 'statsTargets',
    "againstMovingRate": 'statsTargets',
    "glanceRate": 'statsTargets',
    "missed": 'statsTargets',
    "evaded": 'statsTargets',
    "blocked": 'statsTargets',
    "interrupts": 'statsTargets',
    "invulned": 'statsTargets',
    "killed": 'statsTargets',
    "downed": 'statsTargets',
    "downContribution": 'statsTargets',
    #"connectedPowerCount": 'statsTargets',
    #"connectedPowerAbove90HPCount": 'statsTargets',
    #"connectedConditionCount": 'statsTargets',
    #"connectedConditionAbove90HPCount": 'statsTargets',
    #"againstDownedCount": 'statsTargets',
    "againstDownedDamage": 'statsTargets',
    "appliedCrowdControl": 'statsTargets',
    "appliedCrowdControlDuration": 'statsTargets',
    "appliedCrowdControlDownContribution": 'statsTargets',
	"appliedCrowdControlDurationDownContribution": 'statsTargets'
}

boons = {
	'b740': "Might", 'b725': "Fury", 'b1187': "Quickness", 'b30328': "Alacrity", 'b717': "Protection",
	'b718': "Regeneration", 'b726': "Vigor", 'b743': "Aegis", 'b1122': "Stability",
	'b719': "Swiftness", 'b26980': "Resistance", 'b873': "Resolution", 'b5974': "Superspeed", 'b13017': "Stealth", 'b10269': "Hide in Shadows"
}

buffs_conditions = {
    'b736': "Bleeding", 'b737': "Burning", 'b861': "Confusion", 'b723': "Poison", 'b19426': "Torment", 'b720': "Blind",
    'b722': "Chilled", 'b721': "Crippled", 'b791': "Fear", 'b727': "Immobile", 'b26766': "Slow", 'b742': "Weakness",
    'b27705': "Taunt", 'b738': "Vulnerability"
}

buffs_support = {
    'b890': "Revealed", 'b5577': "Shocking Aura", 'b5579': "Frost Aura", 'b5677': "Fire Aura", 'b5684': "Magnetic Aura", 'b5974': "Superspeed",
    'b9231': "Merciful Intervention (Target)", 'b9235': "Merciful Intervention (Self)", 'b10269': "Hide in Shadows", 'b10332': "Chaos Aura",
    'b10346': "Illusion of Life", 'b13017': "Stealth", 'b13094': "Devourer Venom", 'b13095': "Ice Drake Venom", 'b13133': "Basilisk Venom",
    'b14450': "Banner of Tactics", 'b15788': "Conjure Earth Shield", 'b15789': "Conjure Flame Axe", 'b15790': "Conjure Frost Bow",
    'b15791': "Conjure Lightning Hammer", 'b15792': "Conjure Fiery Greatsword", 'b25518': "Light Aura", 'b30462': "Heat Sync",
    'b34236': "Search and Rescue!", 'b39978': "Dark Aura", 'b45038': "Moa Stance", 'b46280': "Griffon Stance", 'b50381': "Storm Spirit",
    'b51674': "Facet of Nature-Dragon", 'b51704': "Facet of Nature-Demon", 'b63093': "Shrouded"
}

buffs_defensive = {
    'b17047': "Virtue of Resolve (Battle Presence - Absolute Resolve)", 'b19083': "Oil Mastery III (Increased Armor)", 'b21484': "Iron Hide (Ram)",
    'b21780': "Skelk Venom", 'b24304': "Stone Heart", 'b26596': "Rite of the Great Dwarf", 'b27737': "Infuse Light", 'b29379': "Naturalistic Resonance",
    'b29726': "Last Rites", 'b29906': "Shield of Courage (Active)", 'b30285': "Vampiric Aura", 'b31229': "Watchful Eye", 'b31337': "Rebound",
    'b33330': "Rite of the Great Dwarf (Ancient Echo)", 'b33978': "Healing Mist", 'b34281': "Guard!", 'b40045': "Bear Stance", 'b41815': "Dolyak Stance",
    'b42249': "Photon Barrier Buff", 'b42925': "Eternal Oasis", 'b43194': "Unbroken Lines", 'b43401': "Unflinching Fortitude", 'b43487': "Signet of Courage (Shared)",
    'b44682': "Breakrazor's Bastion", 'b45910': "Defy Pain", 'b46554': "Signet of Resolve (Shared)", 'b50415': "Stone Spirit", 'b51677': "Facet of Nature-Dwarf",
    'b51699': "Facet of Nature-Centaur", 'b55026': "Glyph of the Stars (CA)", 'b55048': "Glyph of the Stars",
}

buffs_offensive = {
    'b36781': "Unblockable", 'b31487': "Static Charge", 'b38333': "Pinpoint Distribution", 'b41957': "Ashes of the Just", 'b9240': "Bane Signet (PI)",
    'b9237': "Signet of Wrath (PI)", 'b31803': "Glyph of Empowerment", 'b50421': "Frost Spirit", 'b50413': "Sun Spirit", 'b14055': "Spotter",
    'b44651': "Vulture Stance", 'b44139': "One Wolf Pack", 'b51692': "Facet of Nature-Assassin", 'b41016': "Razorclaw's Rage",
    'b45026': "Soulcleave's Summit", 'b26854': "Assassin's Presence", 'b63168': "Rot Wallow Venom", 'b13054': "Skale Venom", 'b13036': "Spider Venom",
    'b49083': "Soul Stone Venom", 'b14417': "Banner of Strength", 'b14449': "Banner of Discipline", 'b14222': "Empower Allies",
}

buffs_debuff = {
    'b46842': "Exhaustion", 'b1159': "Encumbered", 'b70350': "Relic of the Dragonhunter", 'b70806': "Relic of Isgarren", 'b69882': "Relic of Peitha",
    'b10179': "Morphed (Polymorph Moa)", 'b15859': "Morphed (Polymorph Tuna)", 'b14499': "Impaled", 'b30778': "Hunter's Mark", 'b44633':'Disenchantment',
    'b833': 'Daze', 'b872': 'Stun'
}


arrow_cart_skill_ids = [18850, 18853, 18855, 18860, 18862, 18865, 18867, 18869, 18872]
trebuchet_skill_ids = [21037, 21038]
catapult_skill_ids = [20242, 20272]
cannon_skill_ids = [14626, 14658, 14659, 18535, 18531, 18543, 19626]
burning_oil_skill_ids = [18887]
dragon_banner_skill_ids = [32980, 31968, 33232]
golem_skills = [14627, 14639, 14709, 14710, 14708, 14713, 63185, 1656, 14642]
downed_skills = [9149, 9096, 9095, 28180, 27063, 27792, 14390, 14515, 14391, 5820,
				5962, 5963, 12486, 12485, 12515, 13003, 13138, 13140, 13033
               ]
other_skills = [14601, 14600, 23284, 23285, -2, 58083, 20285, 9284, 23275, 54877,
               54941, 54953, 21615, 23267, 18792, 18793, 25533, 27927, 30765, 34797
              ]

siege_skill_ids = [
	*arrow_cart_skill_ids,
	*trebuchet_skill_ids,
	*catapult_skill_ids,
	*cannon_skill_ids,
	*burning_oil_skill_ids,
	*dragon_banner_skill_ids,
    *golem_skills,    
]

exclude_skill_ids = [
	*arrow_cart_skill_ids,
	*trebuchet_skill_ids,
	*catapult_skill_ids,
	*cannon_skill_ids,
	*burning_oil_skill_ids,
	*dragon_banner_skill_ids,
    *golem_skills,
    *downed_skills,
    *other_skills
]

profession_color = {
	##WARRIORS
	"Warrior":"#FF9933", "Berserker":"#FFA750", "Spellbreaker":"#FFB66D", "Bladesworn":"#FFC48A",
	##GUARDIANS
	"Guardian":"#3399cc",	"Dragonhunter":"#50A7D3", "Firebrand":"#6DB6DA", "Willbender":"#8AC4E1",
	##REVENANTS
	"Revenant":"#CC6342", 	"Herald":"#D3795D", "Renegade":"#DA8F78", "Vindicator":"#E1A593",
	##ENGINEERS
	"Engineer":"#996633",	"Scrapper":"#A77B50",	"Holosmith":"#B6916D", "Mechanist":"#C4A78A",
	##RANGERS
	"Ranger":"#66CC33", "Druid":"#7BD350",	"Soulbeast":"#91DA6D", "Untamed":"#A7E18A",
	##THIEVES
	"Thief":"#CC6666", "Daredevil":"#D37B7B", "Deadeye":"#DA9191", "Specter":"#E1A7A7",
	##ELEMENTALISTS
	"Elementalist":"#EC5752", "Tempest":"#EE6F6A", "Weaver":"#F18783",	"Catalyst":"#F49F9C",
	#MESMERS
	"Mesmer":"#993399", "Chronomancer":"#A750A7", "Mirage":"#B66DB6", "Virtuoso":"#C48AC4",
	##NECROMANCERS
	"Necromancer":"#339966", "Reaper":"#50A77B", "Scourge":"#6DB691", "Harbinger":"#8AC4A7"
}

leaderboard_stats = {
    'damage': "DPS",
    'down_contribution': "Down Contribution",
    'downs': "Downs",
    'kills': "Kills",
    'damage_taken': "Damage Taken",
    'damage_barrier': "Barrier Damage",
    'downed': "Downed",
    'deaths': "Deaths",
    'cleanses': "Cleanses",
    'boon_strips': "Boon Strips",
    'resurrects': "Ressurects",
    'healing': "Healing",
    'barrier': "Barrier",
    'downed_healing': "Downed Healing",
    'stab_gen': "Stability",
    'migh_gen': "Might",
    'fury_gen': "Fury",
    'quic_gen': "Quickness",
    'alac_gen': "Alacrity",
    'prot_gen': "Protection",
    'rege_gen': "Regeneration",
    'vigo_gen': "Vigor",
    'aeg_gen': "Aegis",
    'swif_gen': "Swiftness",
    'resi_gen': "Resistance",
    'reso_gen': "Resolution"
}