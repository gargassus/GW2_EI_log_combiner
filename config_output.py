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
	740: 	"Might",
	725: 	"Fury",
	1187: 	"Quickness",
	30328: 	"Alacrity",
	717: 	"Protection",
	718:	"Regeneration",
	726:	"Vigor",
	743:	"Aegis",
	1122:	"Stability",
	719:	"Swiftness",
	26980:	"Resistance",
	873:	"Resolution"
}