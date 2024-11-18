# GW2_EI_log_combiner  ![GitHub Release](https://img.shields.io/github/v/release/Drevarr/GW2_EI_log_combiner?include_prereleases&display_name=release)

GW2 - Elite Insight Multiple Log Summary



Combines multiple [ArcDps](https://www.deltaconnected.com/arcdps/x64/) logs processed by [GW2 Elite Insight Parser](https://github.com/baaron4/GW2-Elite-Insights-Parser/releases) to json output into summarized drag and drop package for use with a [TW5](https://github.com/TiddlyWiki/TiddlyWiki5) static html file or [TW5](https://github.com/TiddlyWiki/TiddlyWiki5) nodejs server.  

This is a continuation of my efforts previously focused on a fork of @Freyavf /[arcdps_top_stats_parser](https://github.com/Drevarr/arcdps_top_stats_parser).  Influenced heavily by all the participants in the WvW Data Analysis discord 


Currently works with WVW and Detailed WVW logs. Partially working with PVElogs, still needs adjustments to handle the PVE formats.


Testing alpha releases with frequent changes.

**Steps for successful testing**

 - Parse your [ArcDps](https://www.deltaconnected.com/arcdps/x64/) WvW logs with [GW2 Elite Insight Parser](https://github.com/baaron4/GW2-Elite-Insights-Parser/releases) 
     - Ensure all options are checked under `Encounter` on the general tab 
     - Ensure you have `Output as JSON` checked on the Raw output tab
     - There is a provided example EI settings config file you can load via the `load settings` button in the `/EliteInsightConfig` folder
 - Decompress the [latest release](https://github.com/Drevarr/GW2_EI_log_combiner/releases) file to your preferred location
 - Edit the `top_stats_config.ini` file to set the `input_directory` so it points to the location of your saved JSON logs
 - Double click the `TopStats.exe` to run
 - Open the file `/Example_Output/Top_Stats_Index.html` in your browser of choice.
 - Drag and Drop the file `Drag_and_Drop_Log_Summary_for_2024yourdatatime.json` onto the opened `Top_Stats_Index.html` in your browser and click `import`
 - Open the 1. imported file link to view the summary
 - DM me with errors, suggestions and ideas. 
 - Send example arcdps logs generating issues would be appreciated 
 
**Optional**
 - You can run from source after installing required packages via cmd line: `python tw5_top_stats.py -i d:\path\to\logs`


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
      - [X] Squad Comp (Friendly/Enemies)
      - [X] Party Comp by Fight
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
      - [x] Player Dmg by Skils            
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
   - [X] target data
      - [X] teamID
   - [x] Highlights / High Scores
      - [x] damage
      - [x] defense
      - [x] support
      - [x] Highest single damage hit
      - [x] format output

