# Route case/config evaluation summary

All indices are **base 0**, matching Python/JSON array indexing.


## Case 1: Tehtaankatu 27-29 → Tehtaankatu 23
**Category:** I. Direct route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `16, 172, 174, 176, 248`  
  No successful valid route result. ok 4/5; valid JSON 0/5; valid path 0/5; exact 0/5. Main labels: invalid_json×4, provider_call_failed×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `92, 94, 96`  
  Mixed result: some exact matches, some non-exact or failed runs. ok 3/3; valid JSON 3/3; valid path 2/3; exact 2/3; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 94.4%; avg edge overlap 92.8%. Main labels: exact_match×2, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `dynamic, budget=None` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `144, 146`  
  No successful valid route result. ok 2/2; valid JSON 0/2; valid path 0/2; exact 0/2. Main labels: invalid_json×2.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `150, 152, 154, 156, 158, 160, 162, 164, 166, 168, 170`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 11/11; valid JSON 2/11; valid path 0/11; exact 0/11; avg node overlap 66.7%; avg edge overlap 60.9%. Main labels: invalid_json×9, missing_edges×1, unknown_nodes×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `208, 210`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 62.5%; avg edge overlap 56.5%. Main labels: missing_edges×1, invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `246`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `209, 211, 249`  
  All runs matched the ground-truth route exactly. ok 3/3; valid JSON 3/3; valid path 3/3; exact 3/3; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 100.0%; avg edge overlap 100.0%. Main labels: exact_match×3.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `247`  
  All runs matched the ground-truth route exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 1/1; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 100.0%; avg edge overlap 100.0%. Main labels: exact_match×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `17, 173, 175, 177`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 4/4; valid path 0/4; exact 0/4; avg node overlap 53.1%; avg edge overlap 42.4%. Main labels: missing_edges×4.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `93, 95, 97`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 31.9%; avg edge overlap 23.2%. Main labels: missing_edges×2, wrong_destination+missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `145, 147, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 171`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 13/13; valid JSON 13/13; valid path 0/13; exact 0/13; avg node overlap 17.3%; avg edge overlap 8.0%. Main labels: missing_edges×13.

## Case 2: Kankurinkatu 5 → Merimiehenkatu 23
**Category:** I. Direct route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `12, 14, 136, 138, 140, 142, 240, 242`  
  Mixed result: some exact matches, some non-exact or failed runs. ok 8/8; valid JSON 7/8; valid path 2/8; exact 2/8; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 96.8%; avg edge overlap 93.2%. Main labels: missing_edges×5, exact_match×2, invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `86, 88, 90`  
  Mixed result: some exact matches, some non-exact or failed runs. ok 3/3; valid JSON 3/3; valid path 1/3; exact 1/3; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 97.0%; avg edge overlap 93.7%. Main labels: missing_edges×2, exact_match×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `204, 206`  
  All runs failed at the provider/API-call level. ok 0/2; valid JSON 0/2; valid path 0/2; exact 0/2. Main labels: provider_call_failed×2.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `244`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `205, 207, 241, 243`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 4/4; valid path 0/4; exact 0/4; avg node overlap 14.8%; avg edge overlap 9.5%. Main labels: wrong_destination×3, missing_edges×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `245`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 0/1; avg length error 1388.6 m; avg relative error 751.0%; avg node overlap 18.2%; avg edge overlap 9.5%. Main labels: valid_but_not_shortest×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `13, 15, 137, 139, 141, 143`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 6/6; valid JSON 6/6; valid path 0/6; exact 0/6; avg node overlap 42.4%; avg edge overlap 31.0%. Main labels: missing_edges×6.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `87, 89, 91`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 25.8%; avg edge overlap 14.3%. Main labels: missing_edges×2, unknown_nodes×1.

## Case 3: Tehtaankatu 27-29 → Erottajankatu 5
**Category:** II. Long multi-hop route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `8, 10`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 11.1%; avg edge overlap 7.5%. Main labels: missing_edges×1, provider_call_failed×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `72, 74, 76, 78, 80, 82, 84`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 7/7; valid JSON 3/7; valid path 0/7; exact 0/7; avg node overlap 10.3%; avg edge overlap 7.1%. Main labels: invalid_json×4, missing_edges×2, empty_path×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=4352` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `98`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=1024` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `100`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `102`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `104`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `99, 101, 103`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 3/3; valid JSON 3/3; valid path 3/3; exact 0/3; avg length error 624.5 m; avg relative error 49.1%; avg node overlap 30.5%; avg edge overlap 28.3%. Main labels: valid_but_not_shortest×3.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `9, 11`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 2/2; valid path 0/2; exact 0/2; avg node overlap 3.1%; avg edge overlap 0.6%. Main labels: wrong_destination×1, missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `73, 75, 77, 79, 81, 83, 85`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 7/7; valid JSON 5/7; valid path 0/7; exact 0/7; avg node overlap 3.0%; avg edge overlap 0.5%. Main labels: missing_edges×3, wrong_destination+missing_edges×2, invalid_json×2.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `105`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 3.7%; avg edge overlap 0.0%. Main labels: missing_edges×1.

## Case 4: Ratakatu 2 → Perämiehenkatu 11 A
**Category:** II. Long multi-hop route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `58, 60, 62, 64, 66, 68, 70`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 7/7; valid JSON 2/7; valid path 0/7; exact 0/7; avg node overlap 26.8%; avg edge overlap 24.1%. Main labels: invalid_json×5, missing_edges×2.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `234`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `236`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `238`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `235`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 36.6%; avg edge overlap 35.8%. Main labels: wrong_destination×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `237`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 36.6%; avg edge overlap 35.8%. Main labels: wrong_destination×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `239`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 37.8%; avg edge overlap 35.8%. Main labels: missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `59, 61, 63, 65, 67, 69, 71`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 7/7; valid JSON 6/7; valid path 0/7; exact 0/7; avg node overlap 4.9%; avg edge overlap 2.5%. Main labels: missing_edges×5, invalid_json×1, wrong_destination×1.

## Case 5: Laivurinkatu 10 → Ratakatu 2
**Category:** III. Junction-heavy route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `6`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 88.5%; avg edge overlap 84.0%. Main labels: missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `52, 54, 56`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 46.2%; avg edge overlap 40.0%. Main labels: missing_edges×3.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=1024` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `196`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 34.6%; avg edge overlap 28.0%. Main labels: missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `198, 200, 202, 216, 218`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 5/5; valid JSON 2/5; valid path 0/5; exact 0/5; avg node overlap 30.8%; avg edge overlap 8.0%. Main labels: invalid_json×3, missing_edges×2.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `JSON Generator` | SSAL: `default_length_name_oneway_coords` | indices_base0: `220, 222`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 15.4%; avg edge overlap 8.0%. Main labels: missing_edges×1, invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Node to Node Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `224`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Validation Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `226, 228`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 2/2; valid path 0/2; exact 0/2; avg node overlap 53.8%; avg edge overlap 48.0%. Main labels: missing_edges×2.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `232`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `197, 199, 201, 203, 217, 219`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 6/6; valid JSON 6/6; valid path 0/6; exact 0/6; avg node overlap 20.5%; avg edge overlap 16.7%. Main labels: missing_edges×3, empty_path×3.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `JSON Generator` | SSAL: `default_length_name_oneway_coords` | indices_base0: `221, 223`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 2/2; valid path 0/2; exact 0/2; avg node overlap 44.2%; avg edge overlap 38.0%. Main labels: missing_edges×2.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Node to Node Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `225`  
  All runs matched the ground-truth route exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 1/1; avg length error 0.0 m; avg relative error 0.0%; avg node overlap 100.0%; avg edge overlap 100.0%. Main labels: exact_match×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Validation Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `227, 229`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 26.9%; avg edge overlap 24.0%. Main labels: wrong_destination+missing_edges×1, invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `233`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `7`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 19.2%; avg edge overlap 12.0%. Main labels: missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `53, 55, 57`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 14.1%; avg edge overlap 6.7%. Main labels: missing_edges×3.

## Case 6: Tehtaankatu 23 → Fredrikinkatu 16
**Category:** III. Junction-heavy route

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `44, 46, 48, 50`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 1/4; valid path 0/4; exact 0/4; avg node overlap 5.0%; avg edge overlap 0.0%. Main labels: invalid_json×3, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `106`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 5.0%; avg edge overlap 0.0%. Main labels: missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `148, 184, 188`  
  No successful valid route result. ok 3/3; valid JSON 0/3; valid path 0/3; exact 0/3. Main labels: invalid_json×3.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Node to Node Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `186`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=1024` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `190, 192, 194`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 1/3; valid path 0/3; exact 0/3; avg node overlap 12.5%; avg edge overlap 7.7%. Main labels: invalid_json×2, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `230`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `VoT Template` | SSAL: `default_length_name_oneway_coords` | indices_base0: `107`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 0/1; avg length error 489.7 m; avg relative error 88.5%; avg node overlap 45.0%; avg edge overlap 41.0%. Main labels: valid_but_not_shortest×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `149, 185, 189, 191, 193, 195`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 6/6; valid JSON 6/6; valid path 0/6; exact 0/6; avg node overlap 0.8%; avg edge overlap 0.0%. Main labels: empty_path×4, wrong_destination×2.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Node to Node Routing Engine` | SSAL: `default_length_name_oneway_coords` | indices_base0: `187`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 0/1; avg length error 491.4 m; avg relative error 88.8%; avg node overlap 45.0%; avg edge overlap 41.0%. Main labels: valid_but_not_shortest×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `231`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 0/1; avg length error 489.7 m; avg relative error 88.5%; avg node overlap 45.0%; avg edge overlap 41.0%. Main labels: valid_but_not_shortest×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `45, 47, 49, 51`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 4/4; valid path 0/4; exact 0/4; avg node overlap 16.9%; avg edge overlap 9.6%. Main labels: missing_edges×3, wrong_destination+missing_edges×1.

## Case 7: Kankurinkatu 5 → Tehtaankatu 27-29
**Category:** IV. Near shortest alternatives

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `38, 40, 42`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 1/3; valid path 0/3; exact 0/3; avg node overlap 79.2%; avg edge overlap 73.9%. Main labels: invalid_json×2, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `108, 110, 214`  
  Some runs produced valid paths, but no exact shortest-path match. ok 3/3; valid JSON 2/3; valid path 1/3; exact 0/3; avg length error 39.0 m; avg relative error 10.6%; avg node overlap 75.0%; avg edge overlap 69.6%. Main labels: valid_but_not_shortest×1, invalid_json×1, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `180, 182`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 2/2; valid path 0/2; exact 0/2; avg node overlap 64.6%; avg edge overlap 56.5%. Main labels: missing_edges×2.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=8192` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `212`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `39, 41, 43`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 6.9%; avg edge overlap 0.0%. Main labels: missing_edges×2, wrong_destination×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `109, 111, 181, 183, 213, 215`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 6/6; valid JSON 6/6; valid path 0/6; exact 0/6; avg node overlap 9.7%; avg edge overlap 1.4%. Main labels: missing_edges×6.

## Case 8: Bulevardi 40 → Erottajankatu 5
**Category:** IV. Near shortest alternatives

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `32, 34, 36`  
  No successful valid route result. ok 3/3; valid JSON 0/3; valid path 0/3; exact 0/3. Main labels: invalid_json×3.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `178`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 75.8%; avg edge overlap 73.8%. Main labels: missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `33, 35, 37`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 17.2%; avg edge overlap 11.8%. Main labels: missing_edges×2, unknown_nodes×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `179`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 4.5%; avg edge overlap 1.5%. Main labels: missing_edges×1.

## Case 9: Albertinkatu 15 → Bulevardi 40
**Category:** V. Shortest alternative is a one-way street

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `18, 20, 22, 24`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 1/4; valid path 0/4; exact 0/4; avg node overlap 32.8%; avg edge overlap 28.8%. Main labels: invalid_json×3, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `120, 126`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 16.4%; avg edge overlap 7.6%. Main labels: invalid_json×1, missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `132`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `134`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `19, 21, 23, 25`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 4/4; valid JSON 2/4; valid path 0/4; exact 0/4; avg node overlap 11.2%; avg edge overlap 8.3%. Main labels: invalid_json×2, missing_edges×2.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `121, 127`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 1/2; valid path 0/2; exact 0/2; avg node overlap 14.9%; avg edge overlap 10.6%. Main labels: invalid_json×1, missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `133`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 1.5%; avg edge overlap 0.0%. Main labels: wrong_destination×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `135`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.

## Case 10: Tehtaankatu 27-29 → Laivurinkatu 10
**Category:** V. Shortest alternative is a one-way street

- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `2, 4, 128`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 9.5%; avg edge overlap 4.9%. Main labels: missing_edges×3.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `26, 28, 30`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 2/3; valid path 0/3; exact 0/3; avg node overlap 4.8%; avg edge overlap 0.0%. Main labels: missing_edges×2, invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Intermediate Sub Route Validation Prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `112, 114, 116`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 2/3; valid path 0/3; exact 0/3; avg node overlap 7.1%; avg edge overlap 2.4%. Main labels: missing_edges×2, invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Intermediate Sub Route Validation Prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `118`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `122`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 9.5%; avg edge overlap 4.9%. Main labels: missing_edges×1.
- **Gemini / gemini-2.5-flash** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `124`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-flash** | thinking: `custom, budget=2048` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `130`  
  No successful valid route result. ok 1/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: invalid_json×1.
- **Gemini / gemini-2.5-pro** | thinking: `off, budget=0` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `0`  
  All runs failed at the provider/API-call level. ok 0/1; valid JSON 0/1; valid path 0/1; exact 0/1. Main labels: provider_call_failed×1.
- **OpenAI / gpt-5.4** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `1`  
  All runs produced valid paths, but none matched the shortest path exactly. ok 1/1; valid JSON 1/1; valid path 1/1; exact 0/1; avg length error 104.8 m; avg relative error 16.0%; avg node overlap 40.5%; avg edge overlap 36.6%. Main labels: valid_but_not_shortest×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `3, 5, 129`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 2/3; valid path 0/3; exact 0/3; avg node overlap 4.8%; avg edge overlap 1.2%. Main labels: wrong_destination×1, invalid_json×1, missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `VoT Template` | SSAL: `length_name_oneway` | indices_base0: `27, 29, 31`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 3/3; valid path 0/3; exact 0/3; avg node overlap 11.9%; avg edge overlap 6.5%. Main labels: missing_edges×3.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Intermediate Sub Route Validation Prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `113, 115, 117`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 3/3; valid JSON 2/3; valid path 0/3; exact 0/3; avg node overlap 6.0%; avg edge overlap 2.4%. Main labels: invalid_json×1, missing_edges×1, wrong_destination+unknown_nodes×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Intermediate Sub Route Validation Prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `119`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 9.5%; avg edge overlap 2.4%. Main labels: missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `123`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 1/1; valid JSON 1/1; valid path 0/1; exact 0/1; avg node overlap 7.1%; avg edge overlap 2.4%. Main labels: missing_edges×1.
- **OpenAI / gpt-5.4-mini** | thinking: `—` | prompt: `Built-in default route prompt` | SSAL: `default_length_name_oneway_coords` | indices_base0: `125, 131`  
  Responses were at least partly parseable JSON, but no run produced a valid path. ok 2/2; valid JSON 2/2; valid path 0/2; exact 0/2; avg node overlap 7.1%; avg edge overlap 2.4%. Main labels: missing_edges×2.
