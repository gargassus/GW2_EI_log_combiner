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
    "damageBarrier": 'defenses',
	"conditionDamageTaken": 'defenses',
	"powerDamageTaken": 'defenses',
	#"strikeDamageTaken": 'defenses',
	#"lifeLeechDamageTaken": 'defenses',
	#"breakbarDamageTaken": 'defenses',
	"blockedCount": 'defenses',
	"evadedCount": 'defenses',
	"missedCount": 'defenses',
	"dodgeCount": 'defenses',
	"invulnedCount": 'defenses',
	"interruptedCount": 'defenses',
	"boonStrips": 'defenses',
	#"boonStripsTime": 'defenses',
	"conditionCleanses": 'defenses',
	#"conditionCleansesTime": 'defenses',
	"receivedCrowdControl": 'defenses',
	#"receivedCrowdControlDuration": 'defenses'
	"downCount": 'defenses',
	#"downDuration": 'defenses',
    "downedDamageTaken": 'defenses',
	"deadCount": 'defenses',
	#"deadDuration": 'defenses',
	#"dcCount": 'defenses',
	#"dcDuration": 'defenses',
}

support_table = {
	"condiCleanse": 'support',
	"condiCleanseTime": 'support',
	"condiCleanseSelf": 'support',
	"condiCleanseTimeSelf": 'support',
	"boonStrips": 'support',
	"boonStripsTime": 'support',
	"stunBreak": 'support',
	"removedStunDuration": 'support',
	"resurrects": 'support',
	"resurrectTime": 'support'
}

offensive_table = {
    #"totalDamageCount": 'statsTargets',
    "totalDmg": 'statsTargets',
    #"directDamageCount": 'statsTargets',
    "directDmg": 'statsTargets',
    #"connectedDirectDamageCount": 'statsTargets',
    #"connectedDirectDmg": 'statsTargets',
    #"connectedDamageCount": 'statsTargets',
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
    "appliedCrowdControlDuration": 'statsTargets'
}

boons = {
	740: "Might", 725: "Fury", 1187: "Quickness", 30328: "Alacrity", 717: "Protection",
	718: "Regeneration", 726: "Vigor", 743: "Aegis", 1122: "Stability",
	719: "Swiftness", 26980: "Resistance", 873: "Resolution"
}

buffs_conditions = {
    736: "Bleeding", 737: "Burning", 861: "Confusion", 723: "Poison", 19426: "Torment", 720: "Blind",
    722: "Chilled", 721: "Crippled", 791: "Fear", 727: "Immobile", 26766: "Slow", 742: "Weakness",
    27705: "Taunt", 738: "Vulnerability"
}

buffs_support = {
    890: "Revealed", 5577: "Shocking Aura", 5579: "Frost Aura", 5677: "Fire Aura", 5684: "Magnetic Aura", 5974: "Superspeed",
    9231: "Merciful Intervention (Target)", 9235: "Merciful Intervention (Self)", 10269: "Hide in Shadows", 10332: "Chaos Aura",
    10346: "Illusion of Life", 13017: "Stealth", 13094: "Devourer Venom", 13095: "Ice Drake Venom", 13133: "Basilisk Venom",
    14450: "Banner of Tactics", 15788: "Conjure Earth Shield", 15789: "Conjure Flame Axe", 15790: "Conjure Frost Bow",
    15791: "Conjure Lightning Hammer", 15792: "Conjure Fiery Greatsword", 25518: "Light Aura", 30462: "Heat Sync",
    34236: "Search and Rescue!", 39978: "Dark Aura", 45038: "Moa Stance", 46280: "Griffon Stance", 50381: "Storm Spirit",
    51674: "Facet of Nature-Dragon", 51704: "Facet of Nature-Demon", 63093: "Shrouded"
}

buffs_defensive = {
    17047: "Virtue of Resolve (Battle Presence - Absolute Resolve)", 19083: "Oil Mastery III (Increased Armor)", 21484: "Iron Hide (Ram)",
    21780: "Skelk Venom", 24304: "Stone Heart", 26596: "Rite of the Great Dwarf", 27737: "Infuse Light", 29379: "Naturalistic Resonance",
    29726: "Last Rites", 29906: "Shield of Courage (Active)", 30285: "Vampiric Aura", 31229: "Watchful Eye", 31337: "Rebound",
    33330: "Rite of the Great Dwarf (Ancient Echo)", 33978: "Healing Mist", 34281: "Guard!", 40045: "Bear Stance", 41815: "Dolyak Stance",
    42249: "Photon Barrier Buff", 42925: "Eternal Oasis", 43194: "Unbroken Lines", 43401: "Unflinching Fortitude", 43487: "Signet of Courage (Shared)",
    44682: "Breakrazor's Bastion", 45910: "Defy Pain", 46554: "Signet of Resolve (Shared)", 50415: "Stone Spirit", 51677: "Facet of Nature-Dwarf",
    51699: "Facet of Nature-Centaur", 55026: "Glyph of the Stars (CA)", 55048: "Glyph of the Stars",
}

buffs_offensive = {
    36781: "Unblockable", 31487: "Static Charge", 38333: "Pinpoint Distribution", 41957: "Ashes of the Just", 9240: "Bane Signet (PI)",
    9237: "Signet of Wrath (PI)", 31803: "Glyph of Empowerment", 50421: "Frost Spirit", 50413: "Sun Spirit", 14055: "Spotter",
    44651: "Vulture Stance", 44139: "One Wolf Pack", 51692: "Facet of Nature-Assassin", 41016: "Razorclaw's Rage",
    45026: "Soulcleave's Summit", 26854: "Assassin's Presence", 63168: "Rot Wallow Venom", 13054: "Skale Venom", 13036: "Spider Venom",
    49083: "Soul Stone Venom", 14417: "Banner of Strength", 14449: "Banner of Discipline", 14222: "Empower Allies",
}

buffs_debuff = {
    46842: "Exhaustion", 1159: "Encumbered", 70350: "Relic of the Dragonhunter", 70806: "Relic of Isgarren", 69882: "Relic of Peitha",
    10179: "Morphed (Polymorph Moa)", 15859: "Morphed (Polymorph Tuna)", 14499: "Impaled", 30778: "Hunter's Mark", 44633:'Disenchantment',
    833: 'Daze', 872: 'Stun'
}
