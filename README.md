# GW2_EI_log_combiner
GW2 - Elite Insight Multiple Log Summary

Combines multiple ArcDps logs processed by GW2-Elite-Insights-Parser to json output.

### To Do
- [ ] Parse multiple json logs
   - [x] fight data
      - [x] skillMap
      - [x] buffMap
      - [x] damage_mod_map
      - [X] personal_buff_map
   - [ ] player data
      - [x] defenses
      - [x] support
      - [x] statsAll
      - [x] statsTargets
      - [x] targetDamageDist
      - [x] dpsTargets
      - [x] totalDamageTaken
      - [x] buffUptimes
      - [x] buffUptimesActive
      - [x] squadBuffs
      - [x] groupBuffs
      - [x] selfBuffs
      - [x] squadBuffsActive
      - [x] groupBuffsActive
      - [x] selfBuffsActive
      - [X] rotation
      - [x] HealStats Data
         - [x] Outgoing Healing
         - [x] Downed Healing
         - [x] Outgoing Barrier
         - [X] Outgoing Healing by Target
         - [X] Outgoing Barrier by Target
         - [X] Outgoing Healing by Skill
         - [X] Outgoing Barrier by Skill
      - [ ] teamID
         - [x] Enemy Team Colors
         - [ ] Ally Team Colors ??
      - [X] Damage Mod Data         
         - [X] Shared
         - [X] Profession  
   - [ ] target data
      - [X] teamID
   - [ ] Highlights / High Scores
      - [ ] damage
      - [ ] defense
      - [ ] support
      - [ ] tbd

- [ ] Output summary
   - [ ] Mirror EI html output via TW5
   - [ ] Chart Dashboard?
   - [ ] hypertable?
