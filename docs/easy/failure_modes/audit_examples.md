# 자동 분류가 어떤 문구를 잡았는지 보기

아래는 실제 신고에서 의도적으로 뽑은 근거 예시입니다. 전체 신고를 대표하는 무작위 표본도, 사람이 정답을 붙인 정확도 평가 자료도 아닙니다. 근거 문구가 실제 문맥에 맞는지 검토하는 용도입니다. 신고 증상 표시와 리콜 1/0은 별개입니다. [라벨링 설명](../LABELING_GUIDE.md)

# Complaint failure/symptom rule audit

These are weak rule-based pseudo-labels, not expert truth. No measured accuracy is available.

Classified 1,603,647 complaint IDs using 23 fixed symptom modes.

Source data is read-only; recall text, recall outcomes, component labels and outcome flags are not classification inputs.

A primary mode is populated only for one-mode records. Unmatched descriptions remain `no_forced_class`. Conflicting narratives retain separate evidence and combined indicators.

## Coverage

| Mode | Complaint IDs with rule evidence |
|---|---:|
| engine_stall | 122,581 |
| failure_to_start | 30,559 |
| reduced_engine_power | 22,721 |
| unintended_acceleration | 20,918 |
| loss_of_braking | 56,329 |
| unintended_braking | 12,456 |
| steering_loss | 65,107 |
| transmission_shift_failure | 50,589 |
| fluid_leak | 47,080 |
| overheating | 18,301 |
| fire_smoke | 44,771 |
| airbag_non_deployment | 26,397 |
| unintended_airbag_deployment | 1,597 |
| electrical_power_loss | 6,861 |
| tire_failure | 18,216 |
| wheel_detachment | 2,959 |
| suspension_failure | 16,153 |
| restraint_failure | 12,424 |
| visibility_failure | 20,803 |
| lighting_failure | 17,811 |
| door_latch_failure | 4,877 |
| rough_running | 18,707 |
| abnormal_vibration | 39,784 |

## Actual-data examples

Examples are deterministic and selected for inspection, not a representative validation set. Full compact evidence is in `audit_examples.json`.

- **engine_stall** — `C-331d2f69b741983255437309d554da93af079d736e9a274021e4df50eb6be846`: , VEHICLE WOULD SUDDENLY STALL FOR NO APPARENT REASON.
- **failure_to_start** — `C-8d8ef686e4a90410fbf185fe87bedd95340ebe1187db61ae84d2eee6d8413000`: RAL OTHER OCCASIONS, THE CAR WOULD NOT START EVEN WITH A 1/4 TANK OF
- **reduced_engine_power** — `C-23750de9c383d0cf42eb8774c718105277bfb39e1abe04b5e0666c69ec2e9e5f`: ERS TURN ON AND OFF, AND VEHICLE COMPLETELY LOSES POWER AT 75 MPH. BATTERY APPEA
- **unintended_acceleration** — `C-6b6fa1b27d3c5f0e29fe10b337e96ca076bfe0f86808f42b0cccde023d7353aa`: VEHICLE SURGES UNEXPECTEDLY AT IDLE; AT
- **loss_of_braking** — `C-9a18ab37bd388454fc2f762d61eff61a3be83e9a01585de04948fa7ad578b8e7`: ABS BRAKING SYSTEM FAILED WHILE DRIVING ON ANY TYP
- **unintended_braking** — `C-271da090734b2785fb7b10e4e344664e12d9783dd26690b012a319a03a88cc85`: ABS BRAKE SYSTEM LOCKED UP ON WET SURFACE. *AK
- **steering_loss** — `C-ebf2bbb1a62904ab67fcfa204e5f6b74f411d3f74d4f4a133edf78dfcb6172d4`: VEHICLE IS DIFFICULT TO STEER AND WHEN A BUMP IS HIT I
- **transmission_shift_failure** — `C-bb085c7fff5d3b54924a24aa4283c5c7fea16520b02c2538c2622b99d1e88ac4`: TRANSMISSION JERKS/GEARS STICK. *SD
- **fluid_leak** — `C-beab7e4a6428b0f2cf481fc1393f02a888239a5847e1b230f2722f323bd73426`: GASKET SLIPPING, CAUSING OIL LEAK ONTO THE EXHAUST, RESULT
- **overheating** — `C-d8dde32f4ae9d43ffdd6675c104674ca8aa55cf7f636f2d882c8555b9043f7ee`: , AND VEHICLE STARTED TO OVERHEAT. PULLED OVER TO THE SHOU
- **fire_smoke** — `C-e2d0de433c8a4984f258d12becce0ad0fd5b4b95ed0b8c0e5674b02181c6a021`: CABLE ASSEMBLY SHORTED, CAUSING FIRE IN STEERING COLUMN/MELTI
- **airbag_non_deployment** — `C-5802fd949503ecbd683999945d4bebf23745012acdaca4944562e2bfefc5aaa0`: KING, ISUZU HIT VEHICLE, AIRBAGS DID NOT DEPLOY ON IMPACT, *AK
- **unintended_airbag_deployment** — `C-11313cf267b2ed7599714f964e9c1a9dbfc6b3f673a7e1b923ceb3d847c11dc9`: MINOR POTHOLE THE FRONT AIR BAG UNEXPECTEDLY DEPLOYED. *NLM
- **electrical_power_loss** — `C-57fd02b5b6e7b852b519304210281593c342b8133fa3758055d2d2a5fea5bb9a`: T. UNABLE TO REMOVE KEY. BATTERY GOES DEAD. 2 GM DEALERSHIPS SAY TH
- **tire_failure** — `C-37a1e5830e637216997a11364a0516b18e002d8d6fed595fc3852497c065c52d`: MICHELIN TIRE SIDEWALL BLEW OUT. *SD
- **wheel_detachment** — `C-34a639fcbede64cca8af994be923833acade0055e6057fa9fd54a9acde2659d4`: LACK OF TENSION, CAUSING WHEEL TO DETACH FROM AXEL, ALSO REAR HAT
- **suspension_failure** — `C-207a2ec45392612b1146a29496cded9a57ff469e6014539111686a3625ef0f97`: STRUT FAILED.
- **restraint_failure** — `C-4cfef59385bbca331557cb2f28de197d502c57d44d9f98ff87987cef51214857`: REAR SEAT BELTS FAILED TWICE. *DSH
- **visibility_failure** — `C-f75d5b7a496c533bdb2e62bfb42e4761774d444a39a3edafb6e51d493ef52f5b`: THE REAR WINDOW SHATTERED WHEN THE DEFROSTER WAS T
- **lighting_failure** — `C-39e4a83208426226806d3f0f0fcd28e8bc1ecbc492cb8204125236a02cb9e837`: HEADLIGHTS FLICKER ON AND OFF IN PULSATING
- **door_latch_failure** — `C-36f6983c3694d4401c448ad8a27420a2681feb22b9cfb90a71507e30697cd08e`: UNG OPEN IN PARKING LOT. DOOR WILL NOT CLOSE AT ALL AND IT WILL NOT LATCH, CAR IS NOT DRIVABLE. IT
- **rough_running** — `C-0b61e3ac4b86a88b50b6df15b18a1451be5782fb285ca13b5408b067d7191e2e`: STALLING INCIDENTS. (2) VEHICLE BEGAN HESITATING WHILE DOWNHILL ON A DRIV
- **abnormal_vibration** — `C-5034efaaeb05f71c7f31604e5fc0116bc491ef74b5f306b86a2a2f0453ab7b65`: UPON ACCELERATION, VEHICLE VIBRATES W/POOR ACCELERATION AND

## Negation behavior

54 synthetic checks passed, including `no fire`, `airbag did not deploy`, `no warning`, hypothetical failures, component-only text, and each symptom class. This is a rule-contract check, not model accuracy.

## Practical limits

- Conservative English regex rules miss paraphrases, typos, multilingual descriptions, and implicit symptoms.
- Local negation/hypothetical rules are incomplete; complex narrative scope can produce false positives or false negatives.
- Historical, repaired, quoted or manufacturer-risk statements may still match; no causal or temporal truth is inferred.
- Descriptions can mention other vehicles or multiple incidents; subject attribution is not reliably resolved.
- A mode is a symptom mentioned in text, not a diagnosis, defect finding, recall outcome, or expert label.
- Zero indicators mean no accepted rule evidence, not verified absence of a failure.
- Conflict union retains all variants and can combine incompatible accounts. Use conflict flags/sensitivity analyses.
