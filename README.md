# GW2_EI_log_combiner  ![GitHub Release](https://img.shields.io/github/v/release/Drevarr/GW2_EI_log_combiner?include_prereleases&display_name=release)

GW2 - Elite Insight Multiple Log Summary



Combines multiple ArcDps logs processed by GW2-Elite-Insights-Parser to json output.


Currently works with WVW and Detailed WVW logs. Partially working with PVElogs, still needs adjustments to handle the PVE formats.


- Parse [ArcDps](https://www.deltaconnected.com/arcdps/x64/) logs with [Elite Insight](https://github.com/baaron4/GW2-Elite-Insights-Parser/releases) utilizing the included `Example Elite Insight Config file for log parsing.conf` to load EI settings.


- Run compiled exe from the command line:

  -  `topstats.exe d:\path\to\logs`

- or run from source:

   -  `python tw5_top_stats.py d:\path\to\logs`


-  Drag and drop the `Drag_and_Drop_Log_Summary_for_datetime.json` file onto the `/Example_Output/Top_Stats_Index.html`


### Example Output of current state:[Log Summary](https://wvwlogs.com/#202411051122-Log-Summary)

---

![GitHub](https://img.shields.io/github/license/Drevarr/GW2_EI_log_combiner)


![Alt](https://repobeats.axiom.co/api/embed/d07727b06a0bcacb7692ccd3c30bd9cfdb2394f7.svg "Repobeats analytics image")

---

### To Do
- [ ] Parse multiple json logs
   - [x] fight data
      - [x] skillMap
      - [x] buffMap
      - [x] damage_mod_map
      - [X] personal_buff_map
      - [ ] Squad Comp (Friendly/Enemies)
      - [ ] Party Comp by Fight
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
      - [x] Gear Buffs
      - [x] Minion Data
      - [x] Top Dmg Skils      
      - [x] HealStats Data
         - [x] Outgoing Healing
         - [x] Downed Healing
         - [x] Outgoing Barrier
         - [x] Outgoing Healing by Target
         - [x] Outgoing Barrier by Target
         - [x] Outgoing Healing by Skill
         - [x] Outgoing Barrier by Skill
      - [ ] teamID
         - [x] Enemy Team Colors
         - [ ] Ally Team Colors ??
      - [X] Damage Mod Data         
         - [X] Shared
         - [X] Profession  
   - [ ] target data
      - [X] teamID
   - [ ] Highlights / High Scores
      - [x] damage
      - [x] defense
      - [x] support
      - [x] Highest single damage hit
      - [x] format output
- [ ] Output summary
   - [ ] Mirror EI html output via TW5
   - [ ] Chart Dashboard?
   - [ ] hypertable?
