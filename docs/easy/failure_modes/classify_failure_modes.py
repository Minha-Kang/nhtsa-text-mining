"""Deterministic symptom-rule preprocessing; these labels are NOT expert truth.

Run from the workspace root:
  python outputs/nhtsa_model_ready_v2/failure_modes/classify_failure_modes.py
The source Parquet files are read only. No recall text or recall labels are read.
`classify_text` is reusable for another supplied description, but this CLI only
processes the complaint population. No model training or accuracy claim is made.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import time

VERSION = "failure-symptom-rules-v2.0.0"
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE_DIR = Path(__file__).resolve().parents[2] / "nhtsa_text_mining/processed"
DEPS = ROOT / "work/python_deps"
if DEPS.exists():
    sys.path.insert(0, str(DEPS))

# Each expression requires an observed symptom/failure, not a component alone.
# Short bounded gaps allow narrative wording while avoiding sentence-wide joins.
G = r"[^.;!?\n]{0,65}"
S = r"[^.;!?\n]{0,35}"
FAIL = r"(?:fail(?:ed|ure|ing|s)?|malfunction(?:ed|ing|s)?|inoperativ\w*|not work(?:ing)?|stopped work(?:ing)?)"
VEH = r"(?:engine|motor|vehicle|car|truck|suv|van)"

def definition(mode, description, triggers, patterns):
    return {"mode": mode, "description": description, "triggers": triggers,
            "patterns": patterns}

TAXONOMY = [
    definition("engine_stall", "Engine/vehicle stalls or stops running unexpectedly.",
               ["stall", "shut", "died", "cut out", "cuts out", "stopped running"], [
        r"\bstall(?:ed|ing|s)?\b",
        rf"\b{VEH}\b{S}\b(?:shut(?:s)? (?:off|down)|died|cut(?:s)? out|stopped running)\b",
    ]),
    definition("failure_to_start", "Engine/vehicle cannot start or restart.",
               ["start", "crank"], [
        rf"\b{VEH}\b{G}\b(?:would not|will not|won't|did not|does not|doesn't|could not|cannot|can't|failed to|fails to|unable to) (?:re)?start\b",
        rf"\b(?:unable|fail(?:ed|s)?) to (?:re)?start\b{S}\b{VEH}\b",
        r"\b(?:no[- ]start|crank(?:s|ed|ing)? but (?:will|would|does|did) not start)\b",
        rf"\b{VEH}\b{S}\b(?:would not|will not|won't|did not|does not|could not) crank\b",
    ]),
    definition("reduced_engine_power", "Explicit loss or reduction of engine/propulsion power or inability to accelerate.",
               ["power", "accelerat"], [
        r"\b(?:(?:loss|reduction|lack) of|lost|losing|reduced) (?:all |the )?(?:engine|motor|propulsion) power\b",
        rf"\b(?:engine|vehicle|car|truck)\b{S}\b(?:lost|loses|losing) (?:all |its )?power\b(?! (?:steering|brake|assist))",
        r"\b(?:reduced engine power|engine power (?:was )?reduced)\b",
        rf"\b{VEH}\b{S}\b(?:would not|will not|could not|failed to|unable to) accelerat\w*\b",
    ]),
    definition("unintended_acceleration", "Acceleration or throttle actuation without the intended driver request.",
               ["accelerat", "throttle", "surge", "sped up"], [
        r"\b(?:unintended|uncommanded|unexpected|sudden|uncontrolled) accelerat\w*\b",
        r"\baccelerat\w*\b[^.;!?\n]{0,45}\b(?:on its own|by itself|without (?:pressing|depressing|warning)|unintentionally|unexpectedly|uncontrollably)\b",
        r"\b(?:accelerator|gas pedal|throttle)\b[^.;!?\n]{0,35}\b(?:stuck|sticking|jammed)\b",
        rf"\b{VEH}\b{S}\b(?:surged|surges|sped up)\b",
    ]),
    definition("loss_of_braking", "Braking failure, ineffective stopping, or brake pedal losing resistance.",
               ["brak", "pedal", "stop"], [
        rf"\b(?:brak(?:e|es|ing)|brak(?:e|ing) system|abs|anti[- ]?lock brakes)\b{S}\b{FAIL}\b",
        r"\b(?:loss|lost|losing) (?:of )?(?:all )?(?:braking|brake power|brake function|brakes)\b",
        r"\bbrake pedal\b[^.;!?\n]{0,50}\b(?:went|goes|sank|sinks|fell|dropped|pressed|depressed)\b[^.;!?\n]{0,20}\b(?:floor|all the way down)\b",
        r"\b(?:brakes? (?:did|does|would|will) not (?:stop|engage|respond)|unable to stop (?:the )?vehicle)\b",
        r"\b(?:no|without) (?:any )?brak(?:es|ing)\b",
    ]),
    definition("unintended_braking", "Brakes engage, lock, or drag without appropriate request.",
               ["brak", "abs"], [
        r"\b(?:brak(?:e|es|ing)|abs)\b[^.;!?\n]{0,35}\b(?:lock(?:ed|ing|s)? up|locked|seized|dragging|dragged|engaged (?:on their own|by themselves)|activated (?:on its own|by itself))\b",
        r"\b(?:unintended|unexpected|phantom) braking\b",
        r"\bbrak(?:e|es|ing)\b[^.;!?\n]{0,45}\b(?:without (?:warning|input|reason)|on (?:its|their) own|by (?:itself|themselves))\b",
    ]),
    definition("steering_loss", "Loss of steering/assist, binding steering, or substantial difficulty steering.",
               ["steer", "turn the wheel"], [
        rf"\b(?:power steering|steering(?: system| assist)?)\b{S}\b(?:{FAIL}|lock(?:ed|ing|s)?(?: up)?|seized|lost|went out|cut out)\b",
        r"\b(?:lost|loss of|losing)\b[^.;!?\n]{0,25}\b(?:power steering|steering(?: control| assist)?)\b",
        r"\b(?:difficult|hard|unable|impossible) to (?:steer|turn (?:the )?(?:steering )?wheel)\b",
        r"\bsteering\b[^.;!?\n]{0,35}\b(?:became|was|is|felt) (?:very |extremely )?(?:stiff|hard|unresponsive)\b",
        r"\bsteering wheel\b[^.;!?\n]{0,25}\b(?:fell off|came off|detach\w*|broke off)\b",
    ]),
    definition("transmission_shift_failure", "Transmission slips, jerks, fails, or cannot select/hold a gear.",
               ["transmission", "gear", "shift", "clutch"], [
        rf"\b(?:transmission|gearbox|clutch)\b{S}\b(?:{FAIL}|slip(?:ped|ping|s)?|jerk(?:ed|ing|s)?|stuck|shudder(?:ed|ing|s)?)\b",
        r"\b(?:unable to|could not|would not|will not|failed to|won't) (?:shift|change gears|engage (?:a |the )?gear)\b",
        r"\b(?:gear(?:s)?|gear shift)\b[^.;!?\n]{0,25}\b(?:stuck|stick(?:s|ing)?|slip(?:ped|ping|s)?|disengag\w*|jump\w* out)\b",
        r"\b(?:harsh|hard|erratic|rough|delayed) shift(?:ing|s)?\b",
    ]),
    definition("fluid_leak", "Observed leak of fuel, oil, coolant, brake/transmission or other vehicle fluid.",
               ["leak", "leaking", "leakage", "spill"], [
        r"\b(?:fuel|gasoline|diesel|oil|coolant|antifreeze|brake fluid|transmission fluid|power steering fluid)\b[^.;!?\n]{0,40}\bleak\w*\b",
        r"\bleak\w*\b[^.;!?\n]{0,40}\b(?:fuel|gasoline|diesel|oil|coolant|antifreeze|brake fluid|transmission fluid|power steering fluid)\b",
        r"\b(?:fuel|gas|oil|coolant|brake|transmission) (?:tank|line|hose|pipe|reservoir|pump|system|seal)\b[^.;!?\n]{0,30}\bleak\w*\b",
    ]),
    definition("overheating", "Vehicle, engine, battery or a vehicle part overheats.",
               ["overheat", "temperature", "ran hot", "running hot"], [
        r"\boverheat(?:ed|ing|s)?\b",
        r"\b(?:engine|motor|battery)\b[^.;!?\n]{0,30}\b(?:ran hot|running hot|temperature (?:was |became )?(?:excessive|too high))\b",
    ]),
    definition("fire_smoke", "Reported actual fire, burning, flames, or visible smoke.",
               ["fire", "flame", "smok", "burn"], [
        r"\b(?:caught|catch(?:es|ing)?|on|engulfed in|burst into|erupted in(?:to)?) (?:a )?(?:fire|flames)\b",
        r"\b(?:fire|flames)\b[^.;!?\n]{0,30}\b(?:erupted|started|occurred|broke out|spread|came|coming|emerged|engulfed)\b",
        r"\b(?:caus(?:ed|ing)|result(?:ed|ing) in|ignited (?:a )?) (?:a )?fire\b",
        r"\b(?:smoke|smoking)\b[^.;!?\n]{0,40}\b(?:from|coming|came|emitting|under|inside|filled|pouring)\b",
        r"\b(?:emitt(?:ed|ing)|saw|observed|noticed|producing|billowing|filled with)\b[^.;!?\n]{0,25}\bsmoke\b",
        rf"\b{VEH}\b{S}\b(?:burned|burnt) (?:up|down|to the ground)\b",
    ]),
    definition("airbag_non_deployment", "Airbag explicitly fails to deploy/inflate (absence of deployment is positive failure evidence).",
               ["airbag", "air bag"], [
        r"\bair\s?bags?\b[^.;!?\n]{0,65}\b(?:did not|didn't|does not|would not|never|failed to|fails to) (?:deploy|inflate)\w*\b",
        r"\b(?:no|without) air\s?bag (?:deployment|deploying)\b",
        r"\bair\s?bag\b[^.;!?\n]{0,25}\bnon[- ]deployment\b",
    ]),
    definition("unintended_airbag_deployment", "Airbag deploys unexpectedly or without a reported crash/impact.",
               ["airbag", "air bag"], [
        r"\bair\s?bags?\b[^.;!?\n]{0,65}\bdeploy\w*\b[^.;!?\n]{0,45}\b(?:unexpectedly|inadvertently|spontaneously|without (?:a |any )?(?:crash|impact|collision)|on (?:its|their) own)\b",
        r"\bair\s?bags?\b[^.;!?\n]{0,45}\b(?:unexpectedly|inadvertently|spontaneously) deploy\w*\b",
        r"\b(?:inadvertent|unexpected|unintended|spontaneous) (?:air\s?bag )?deployment\b",
    ]),
    definition("electrical_power_loss", "Explicit electrical supply, battery, or total electrical-system power failure.",
               ["electrical", "battery", "batteries", "power", "alternator"], [
        r"\b(?:lost|loss of|losing|without|no) (?:all |any |complete )?electrical power\b",
        r"\b(?:electrical system|alternator)\b[^.;!?\n]{0,35}\b(?:shut(?:s)? down|went (?:dead|out)|died|stopped charging|not charging)\b",
        r"\b(?:battery|batteries)\b[^.;!?\n]{0,35}\b(?:died|dead|discharged|drained|would not hold (?:a )?charge|does not hold (?:a )?charge)\b",
        r"\b(?:all|entire)\b[^.;!?\n]{0,15}\b(?:electrical|electric)\b[^.;!?\n]{0,25}\b(?:power went out|power shut off|went dead)\b",
    ]),
    definition("tire_failure", "Tire blowout, tread/belt separation, rupture, or loss of inflation.",
               ["tire", "tyre", "tread", "blowout", "blew out"], [
        r"\b(?:tire|tyre|tread|tire belt)\b[^.;!?\n]{0,40}\b(?:blew|blow(?:n|out)?|separat\w*|ruptur\w*|burst|deflat\w*|went flat|lost (?:air|pressure)|losing (?:air|pressure)|split)\b",
        r"\b(?:tread|belt) separation\b",
        r"\b(?:tire |tyre )?blowout\b",
    ]),
    definition("wheel_detachment", "Wheel comes off, separates, or detaches.",
               ["wheel", "rim"], [
        r"(?<!steering )\b(?:wheel|rim)\b[^.;!?\n]{0,40}\b(?:fell off|came off|coming off|detach\w*|separat\w*|broke off)\b",
    ]),
    definition("suspension_failure", "Suspension part explicitly breaks, collapses, or fails.",
               ["suspension", "control arm", "ball joint", "tie rod", "strut", "spring", "axle"], [
        rf"\b(?:suspension|control arm|ball joint|tie rod|strut|coil spring|leaf spring|axle)\b{S}\b(?:{FAIL}|broke|broken|fractur\w*|separat\w*|collaps\w*|snapped)\b",
        r"\b(?:broken|fractured|snapped) (?:suspension|control arm|ball joint|tie rod|strut|coil spring|leaf spring|axle)\b",
    ]),
    definition("restraint_failure", "Seat belt/buckle or restraint explicitly fails, releases, jams, or cannot latch.",
               ["belt", "buckle", "restraint", "harness"], [
        rf"\b(?:seat\s?belts?|seat\s?belt buckles?|restraint|safety belt|shoulder belt|lap belt)\b{S}\b(?:{FAIL}|unlatch\w*|broke|broken|stuck|jammed|would not latch|did not lock|does not lock|would not retract)\b",
        r"\b(?:buckle|harness)\b[^.;!?\n]{0,25}\b(?:failed|broke|unlatched|will not latch|would not latch)\b",
    ]),
    definition("visibility_failure", "Wipers fail or window/windshield cracks, shatters, or obstructs visibility.",
               ["wiper", "windshield", "window", "visibility", "defrost"], [
        rf"\b(?:wipers?|windshield wipers?|defroster)\b{S}\b(?:{FAIL}|stopp\w*|stuck|broke|broken)\b",
        r"\b(?:windshield|window|rear glass)\b[^.;!?\n]{0,35}\b(?:shatter\w*|crack\w*|explod\w*|fogged|fogging)\b",
        r"\b(?:visibility|view)\b[^.;!?\n]{0,20}\b(?:obstructed|blocked|impaired)\b",
    ]),
    definition("lighting_failure", "Head/tail/brake/turn-signal lights explicitly fail or go out.",
               ["headlight", "head light", "headlamp", "tail light", "taillight", "brake light", "turn signal"], [
        rf"\b(?:head\s?lights?|headlamps?|tail\s?lights?|brake lights?|turn signals?)\b{S}\b(?:{FAIL}|went out|go out|flicker\w*|would not (?:turn on|illuminate)|did not (?:turn on|illuminate))\b",
        r"\b(?:loss of|lost) (?:both |all )?(?:head\s?lights?|headlamps?)\b",
    ]),
    definition("door_latch_failure", "Door/hood/tailgate latch fails or opens unintentionally.",
               ["door", "hood", "latch", "tailgate", "hatch"], [
        rf"\b(?:door latch|hood latch|tailgate latch|hatch latch)\b{S}\b(?:{FAIL}|broke|broken|stuck)\b",
        r"\b(?:door|hood|tailgate|hatch)\b[^.;!?\n]{0,35}\b(?:flew open|opened (?:unexpectedly|on its own|while driving)|would not (?:latch|close)|will not (?:latch|close)|won't (?:latch|close)|unlatched)\b",
    ]),
    definition("rough_running", "Engine misfires, runs rough, or hesitates.",
               ["misfir", "rough", "hesitat"], [
        r"\bmisfir(?:e|es|ed|ing)\b",
        r"\b(?:engine|motor|vehicle)\b[^.;!?\n]{0,35}\b(?:ran rough|runs rough|running rough|rough idle|hesitat\w*)\b",
    ]),
    definition("abnormal_vibration", "Explicit vehicle/steering vibration, shaking or wobble during operation.",
               ["vibrat", "shak", "shook", "wobbl", "shudder"], [
        r"\b(?:vehicle|car|truck|steering wheel|front end|rear end)\b[^.;!?\n]{0,35}\b(?:vibrat\w*|shak(?:e|es|ing)|shook|wobbl\w*|shudder\w*)\b",
        r"\b(?:severe|excessive|violent|abnormal) (?:vibration|shaking|wobbl\w*|shudder\w*)\b",
    ]),
]

MODE_NAMES = [x["mode"] for x in TAXONOMY]
COMPILED = [(d, [(f"{d['mode']}:{i+1}", re.compile(p, re.I)) for i, p in enumerate(d["patterns"])]) for d in TAXONOMY]
# These suppress negated, hypothetical, risk-only and explicitly resolved claims.
# They do NOT treat "no warning" as negation. Negated operation (did not deploy,
# would not start, no brakes) is deliberately encoded as positive failure above.
NEGATED_PREFIX = re.compile(r"\b(?:no (?:evidence|signs?|indication)s? of|no(?: reported| actual)?|not|never|without|denied|did not experience|does not experience|didn't experience|has not experienced|had not experienced|no longer|could not (?:duplicate|reproduce)|unable to (?:duplicate|reproduce))\s+(?:(?:that|any|a|an|the|further|additional|such|engine|vehicle|actual)\s+){0,4}$", re.I)
HYPOTHETICAL_PREFIX = re.compile(r"\b(?:may|might|could|can|possible|possibly|potential(?:ly)?|risk of|possibility of|to prevent|preventing|prevent)\s+(?:(?:a|an|the|engine|vehicle|cause|causing|result in)\s+){0,3}$", re.I)
NEGATED_INTERNAL = re.compile(r"\b(?:no (?:signs? of |evidence of )?|never |not |did not |does not |didn't |has not |had not |without )(?:(?:any|a|an|the|actually|ever)\s+)?(?:fail(?:ed|ure|ing)?|stall(?:ed|ing)?|leak\w*|overheat\w*|misfir\w*|vibrat\w*|shak\w*|shook|shatter\w*|crack\w*|separat\w*|deploy\w*|catch|caught|fire|smoke|flames|accelerat\w*|lose|lost|broke|broken|malfunction\w*|lock\w*|died)\b", re.I)
HYPOTHETICAL_INTERNAL = re.compile(r"\b(?:may|might|could|can|potentially|risk of)\s+(?:(?:have|cause|causing|result in|a|an|the|be)\s+){0,3}(?:fail\w*|stall\w*|leak\w*|overheat\w*|fire|smoke|flames|deploy\w*|accelerat\w*|lose|loss|lock\w*|break|broke|shatter\w*|separat\w*)\b", re.I)
HYPOTHETICAL_CAUSATION = re.compile(r"\b(?:may|might|could|can)\b[^.;!?\n]{0,100}\b(?:caus(?:e|ing)|result(?:ing)? in|lead(?:ing)? to|come into contact)\b", re.I)
POSITIVE_NEGATED_OPERATION = {"failure_to_start", "loss_of_braking", "airbag_non_deployment", "electrical_power_loss", "restraint_failure", "lighting_failure", "door_latch_failure", "transmission_shift_failure", "reduced_engine_power"}

def reject_match(text, match, mode):
    prefix = text[max(0, match.start()-90):match.start()]
    prefix = re.split(r"[.;!?\n]|\b(?:but|however|then)\b", prefix)[-1]
    body = match.group(0)
    suffix = text[match.end():match.end()+48]
    if mode == "airbag_non_deployment" and re.match(r"\s+(?:unexpectedly|inadvertently|spontaneously|without (?:warning|impact|a crash))\b", suffix):
        return True
    if mode == "loss_of_braking" and re.match(r"(?:no|without) (?:any )?brak(?:es|ing)$", body) and re.match(r"\s+(?:fail\w*|malfunction\w*|(?:were |was )?(?:inspected|repaired|replaced|required|necessary))\b", suffix):
        return True
    if NEGATED_PREFIX.search(prefix) or HYPOTHETICAL_PREFIX.search(prefix):
        return True
    if HYPOTHETICAL_CAUSATION.search(prefix+body):
        return True
    if HYPOTHETICAL_INTERNAL.search(body):
        return True
    # For modes that can express a failure as non-operation, only that intended
    # non-operation is exempt; e.g. "brakes did not fail" remains excluded.
    neg = NEGATED_INTERNAL.search(body)
    if neg:
        if mode == "airbag_non_deployment" and re.search(r"(?:not |never )deploy|not inflate", neg.group(0)):
            return False
        if mode == "restraint_failure" and re.search(r"not lock", neg.group(0)):
            return False
        return True
    if re.match(r"\s+(?:did not occur|never occurred|was not (?:present|observed)|were not (?:present|observed)|was ruled out|were ruled out|was (?:a )?possibility)\b", suffix):
        return True
    return False

def redact_excerpt(text):
    text = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[EMAIL]", text, flags=re.I)
    text = re.sub(r"(?<!\w)[A-HJ-NPR-Z0-9]{17}(?!\w)", "[VIN]", text, flags=re.I)
    text = re.sub(r"(?<!\d)(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}(?!\d)", "[PHONE]", text)
    return text

def classify_text(text, variant_index=0):
    """Return weak multi-label symptom matches and exact local evidence.

    Takes description text only; no component codes, outcome flags, recalls,
    dates, manufacturer/model or future information affect these matches.
    """
    if text is None or not str(text).strip():
        return [], []
    lowered = str(text).lower().replace("’", "'")
    evidence = []
    modes = []
    for definition_, rules in COMPILED:
        if not any(token in lowered for token in definition_["triggers"]):
            continue
        mode = definition_["mode"]
        found = None
        for rule_id, pattern in rules:
            for match in pattern.finditer(lowered):
                if not reject_match(lowered, match, mode):
                    found = {"mode": mode, "variant_index": variant_index,
                             "rule_id": rule_id,
                             "excerpt": redact_excerpt(str(text)[max(0,match.start()-25):min(len(str(text)),match.end()+25)].strip()),
                             "match_text": redact_excerpt(str(text)[match.start():match.end()])}
                    break
            if found:
                break
        if found:
            modes.append(mode)
            evidence.append(found)
    return modes, evidence

UNIT_CASES = [
    ("The engine stalled without warning.", ["engine_stall"], []),
    ("No engine stalls were reported.", [], ["engine_stall"]),
    ("The engine did not stall.", [], ["engine_stall"]),
    ("There was no fire or smoke.", [], ["fire_smoke"]),
    ("There was no evidence of fire coming from the engine.", [], ["fire_smoke"]),
    ("The vehicle caught fire without warning.", ["fire_smoke"], []),
    ("The vehicle did not catch fire.", [], ["fire_smoke"]),
    ("The vehicle never caught fire.", [], ["fire_smoke"]),
    ("The vehicle may catch fire.", [], ["fire_smoke"]),
    ("A leaking fuel line could cause a fire.", ["fluid_leak"], ["fire_smoke"]),
    ("There was no warning before the engine stalled.", ["engine_stall"], []),
    ("The airbag did not deploy during the crash.", ["airbag_non_deployment"], []),
    ("Airbags never deployed upon impact.", ["airbag_non_deployment"], []),
    ("Airbags deployed during the crash.", [], ["airbag_non_deployment", "unintended_airbag_deployment"]),
    ("The airbag deployed unexpectedly while parked.", ["unintended_airbag_deployment"], []),
    ("The airbag did not deploy unexpectedly.", [], ["airbag_non_deployment", "unintended_airbag_deployment"]),
    ("The engine would not start.", ["failure_to_start"], []),
    ("No start condition was observed.", ["failure_to_start"], []),
    ("The brakes failed and the pedal went to the floor.", ["loss_of_braking"], []),
    ("The brakes did not fail.", [], ["loss_of_braking"]),
    ("The engine had no oil leaks.", [], ["fluid_leak"]),
    ("The oil was leaking from the engine.", ["fluid_leak"], []),
    ("The engine was overheating.", ["overheating"], []),
    ("The engine was not overheating.", [], ["overheating"]),
    ("The engine could overheat.", [], ["overheating"]),
    ("POWER TRAIN; SERVICE BRAKES; ENGINE; AIR BAGS", [], MODE_NAMES),
    ("The power steering failed.", ["steering_loss"], []),
    ("The vehicle lost engine power.", ["reduced_engine_power"], []),
    ("The vehicle lost power steering.", ["steering_loss"], ["reduced_engine_power"]),
    ("The transmission slipped between gears.", ["transmission_shift_failure"], []),
    ("The rear tire blew out.", ["tire_failure"], []),
    ("The left wheel fell off.", ["wheel_detachment"], []),
    ("The ball joint broke.", ["suspension_failure"], []),
    ("The seat belt failed to lock.", ["restraint_failure"], []),
    ("The windshield wipers stopped working.", ["visibility_failure"], []),
    ("The headlights went out.", ["lighting_failure"], []),
    ("The hood flew open.", ["door_latch_failure"], []),
    ("The engine was misfiring.", ["rough_running"], []),
    ("The steering wheel shook violently.", ["abnormal_vibration"], []),
    ("The electrical system went dead.", ["electrical_power_loss"], []),
    ("The vehicle suddenly accelerated on its own.", ["unintended_acceleration"], []),
    ("The brakes locked up on a dry road.", ["unintended_braking"], []),
    ("No brakes while driving.", ["loss_of_braking"], []),
    ("The owner denied engine stalling.", [], ["engine_stall"]),
    ("There is a risk of engine stalling.", [], ["engine_stall"]),
    ("The engine stalled, but there was no fire.", ["engine_stall"], ["fire_smoke"]),
    ("Possible engine stalling.", [], ["engine_stall"]),
    ("The alternator failed, causing excessive voltage.", [], ["electrical_power_loss"]),
    ("The steering wheel fell off.", ["steering_loss"], ["wheel_detachment"]),
    ("The airbag deployed without warning during a collision.", [], ["unintended_airbag_deployment"]),
    ("It could come into contact with the tire, causing a severe blowout.", [], ["tire_failure"]),
    ("No brakes failed.", [], ["loss_of_braking"]),
    ("The contact denied that the engine stalled.", [], ["engine_stall"]),
    (None, [], MODE_NAMES),
]

def run_unit_cases():
    results = []
    for text, required, excluded in UNIT_CASES:
        actual, _ = classify_text(text)
        passed = set(required).issubset(actual) and not set(excluded).intersection(actual)
        results.append({"text": text, "required_modes": required, "excluded_modes": excluded,
                        "actual_modes": actual, "passed": passed})
    return results

def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--limit", type=int, default=None, help="Optional smoke-run limit; omit for the full population.")
    parser.add_argument("--unit-only", action="store_true")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    units = run_unit_cases()
    write_json(out/"negation_unit_cases.json", units)
    failures = [case for case in units if not case["passed"]]
    if failures:
        print(json.dumps(failures, indent=2), flush=True)
        raise SystemExit(f"{len(failures)} rule unit checks failed")
    if args.unit_only:
        print(f"Passed {len(units)} synthetic rule tests; not a measured accuracy assessment.")
        return
    import pyarrow as pa
    import pyarrow.parquet as pq

    started = time.time()
    source = args.source_dir/"vehicle_complaints.parquet"
    texts_source = args.source_dir/"complaint_texts.parquet"
    source_file = pq.ParquetFile(source)
    expected_rows = source_file.metadata.num_rows if args.limit is None else min(args.limit, source_file.metadata.num_rows)
    conflict_ids = set()
    for batch in source_file.iter_batches(batch_size=100000, columns=["complaint_id", "has_text_conflict"]):
        data = batch.to_pydict()
        conflict_ids.update(cid for cid, flag in zip(data["complaint_id"], data["has_text_conflict"]) if flag)
    print(f"Reading unique variants for {len(conflict_ids):,} conflict complaints", flush=True)
    conflicts = defaultdict(set)
    for batch in pq.ParquetFile(texts_source).iter_batches(batch_size=20000, columns=["complaint_id", "text_clean"]):
        data = batch.to_pydict()
        for cid, txt in zip(data["complaint_id"], data["text_clean"]):
            if cid in conflict_ids and txt and txt.strip():
                conflicts[cid].add(txt)
    # Stable sort makes evidence variant indexes reproducible across row groups.
    conflicts = {cid: sorted(variants) for cid, variants in conflicts.items()}
    print(f"Loaded {sum(map(len, conflicts.values())):,} distinct usable conflict variants", flush=True)

    evidence_type = pa.list_(pa.struct([
        pa.field("mode", pa.string()), pa.field("variant_index", pa.int16()),
        pa.field("rule_id", pa.string()), pa.field("excerpt", pa.string()),
        pa.field("match_text", pa.string()),
    ]))
    schema = pa.schema([
        pa.field("complaint_id", pa.string(), nullable=False),
        pa.field("failure_modes", pa.list_(pa.string()), nullable=False),
        pa.field("primary_failure_mode", pa.string()),
        pa.field("evidence", evidence_type, nullable=False),
        pa.field("has_text_conflict", pa.bool_(), nullable=False),
        pa.field("classification_status", pa.string(), nullable=False),
        pa.field("mode_count", pa.int16(), nullable=False),
        pa.field("text_variant_count_classified", pa.int16(), nullable=False),
    ] + [pa.field("fm_"+mode, pa.uint8(), nullable=False) for mode in MODE_NAMES], metadata={
        b"classification_version": VERSION.encode(),
        b"label_semantics": b"weak rule-based pseudo-labels; no expert validation; no forced class",
        b"primary_mode_semantics": b"populated only when exactly one mode; null otherwise",
    })
    status_counts = Counter()
    mode_counts = Counter()
    count_distribution = Counter()
    conflict_agreement = Counter()
    audit = {"per_mode": defaultdict(list), "no_forced_class": [], "conflict_examples": [], "negation_examples": []}
    processed = variants_seen = conflicts_seen = conflict_missing = conflict_count_mismatch = 0
    classified_conflict_without_union_difference = 0
    max_modes = 0
    path = out/"failure_mode_assignments.parquet"
    writer = pq.ParquetWriter(path, schema, compression="zstd", compression_level=3)
    try:
        for batch in source_file.iter_batches(batch_size=args.batch_size, columns=["complaint_id", "text_clean", "has_text_conflict", "clean_text_variant_count"]):
            rows = []
            for src in batch.to_pylist():
                if args.limit is not None and processed >= args.limit:
                    break
                cid = src["complaint_id"]
                conflict = bool(src["has_text_conflict"])
                if conflict:
                    variants = conflicts.get(cid, [])
                    conflicts_seen += 1
                    if not variants:
                        conflict_missing += 1
                    if len(variants) != (src["clean_text_variant_count"] or 0):
                        conflict_count_mismatch += 1
                else:
                    variants = [src["text_clean"]] if src["text_clean"] and src["text_clean"].strip() else []
                matches = set()
                evidence = []
                variant_mode_sets = []
                for variant_index, text in enumerate(variants):
                    these_modes, these_evidence = classify_text(text, variant_index)
                    matches.update(these_modes)
                    evidence.extend(these_evidence)
                    variant_mode_sets.append(tuple(these_modes))
                if conflict and variant_mode_sets:
                    conflict_agreement["identical_mode_sets" if len(set(variant_mode_sets)) == 1 else "different_mode_sets"] += 1
                modes = [mode for mode in MODE_NAMES if mode in matches]
                if not variants:
                    status = "text_conflict_no_usable_variant" if conflict else "no_usable_text"
                elif conflict:
                    status = "text_conflict_classified" if modes else "text_conflict_no_forced_class"
                else:
                    status = "classified" if modes else "no_forced_class"
                n = len(modes)
                row = {"complaint_id": cid, "failure_modes": modes,
                       "primary_failure_mode": modes[0] if n == 1 else None,
                       "evidence": evidence, "has_text_conflict": conflict,
                       "classification_status": status, "mode_count": n,
                       "text_variant_count_classified": len(variants)}
                row.update({"fm_"+mode: int(mode in matches) for mode in MODE_NAMES})
                rows.append(row)
                status_counts[status] += 1
                mode_counts.update(modes)
                count_distribution[n] += 1
                max_modes = max(max_modes, n)
                variants_seen += len(variants)
                for mode in modes:
                    if len(audit["per_mode"][mode]) < 3:
                        audit["per_mode"][mode].append({"complaint_id": cid, "has_text_conflict": conflict,
                            "all_matched_modes": modes, "evidence": [e for e in evidence if e["mode"] == mode][:2]})
                if variants and not modes and len(audit["no_forced_class"]) < 12:
                    audit["no_forced_class"].append({"complaint_id": cid, "has_text_conflict": conflict,
                        "excerpt": redact_excerpt(variants[0][:300])})
                if conflict and len(audit["conflict_examples"]) < 8:
                    audit["conflict_examples"].append({"complaint_id": cid, "variant_count": len(variants),
                        "variant_mode_sets": variant_mode_sets, "combined_modes": modes,
                        "variant_excerpts": [redact_excerpt(v[:220]) for v in variants[:4]]})
                if variants and len(audit["negation_examples"]) < 12:
                    for txt in variants:
                        if re.search(r"\b(?:no fire|no smoke|did not deploy|no warning|not stall)", txt, re.I):
                            m = re.search(r"\b(?:no fire|no smoke|did not deploy|no warning|not stall)", txt, re.I)
                            audit["negation_examples"].append({"complaint_id": cid, "all_matched_modes": modes,
                                "excerpt": redact_excerpt(txt[max(0,m.start()-90):m.end()+100])})
                            break
                processed += 1
            if rows:
                writer.write_table(pa.Table.from_pylist(rows, schema=schema))
            if processed and (processed % 50000 == 0 or processed == expected_rows):
                elapsed = time.time()-started
                print(f"{processed:,}/{expected_rows:,} complaints | {elapsed:.1f}s | {processed/elapsed:.0f} records/s", flush=True)
            if args.limit is not None and processed >= args.limit:
                break
    finally:
        writer.close()

    # Verify written data and source population without modifying either source.
    result = pq.ParquetFile(path)
    checked_rows = checked_multi_primary = checked_binary = checked_mode_counts = 0
    observed_ids = set()
    for batch in result.iter_batches(batch_size=20000):
        data = batch.to_pydict()
        for i, cid in enumerate(data["complaint_id"]):
            if cid in observed_ids:
                raise AssertionError(f"Duplicate output complaint_id: {cid}")
            observed_ids.add(cid)
            n = len(data["failure_modes"][i])
            assert data["mode_count"][i] == n
            assert data["primary_failure_mode"][i] == (data["failure_modes"][i][0] if n == 1 else None)
            assert sum(data["fm_"+mode][i] for mode in MODE_NAMES) == n
            for mode in MODE_NAMES:
                assert data["fm_"+mode][i] in (0, 1)
                assert data["fm_"+mode][i] == int(mode in data["failure_modes"][i])
            checked_rows += 1
    assert checked_rows == expected_rows
    del observed_ids
    write_json(out/"taxonomy.json", {"version": VERSION, "kind": "fixed_explainable_multilabel_symptom_rules",
        "label_status": "weak_rule_based_pseudo_labels_not_expert_truth", "mode_count": len(MODE_NAMES),
        "modes": TAXONOMY, "input_contract": "Description text only. No recall labels, components or outcome flags.",
        "negation_policy": "Exclude recognized negation/risk-only patterns; preserve non-operation failures (e.g. airbag did not deploy). No warning does not negate a failure.",
        "conflict_policy": "Classify every distinct usable clean-text variant, retain flag, union modes, keep per-variant evidence. Variant disagreement is not resolved into truth.",
        "primary_policy": "Exactly one matched mode => that mode; zero or multiple => null. No ranking asserted.",
        "unknown_policy": "No usable text or no qualifying symptom => explicit status and zero numeric mode columns.",
        "evidence_policy": "At most one accepted match per mode per distinct text variant; excerpts redact recognizable email/phone/VIN patterns."})
    write_json(out/"audit_examples.json", {"purpose": "Small deterministic actual-data examples for human inspection; NOT a labeled validation set or random sample.",
        "selection": "First three occurrences per mode, first 12 unmatched, first eight conflicts, and first 12 selected negation phrases in source order.",
        "source": str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source), **audit})
    report = {"version": VERSION, "source": str(source), "conflict_variants_source": str(texts_source),
        "source_files_modified": False, "recall_text_or_labels_used": False,
        "rows": processed, "source_rows": source_file.metadata.num_rows, "is_full_population": args.limit is None,
        "distinct_usable_text_variants_classified": variants_seen,
        "mode_columns": ["fm_"+mode for mode in MODE_NAMES], "mode_count": len(MODE_NAMES),
        "classification_status_counts": dict(status_counts), "mode_counts": dict(mode_counts),
        "mode_count_distribution": {str(k):v for k,v in sorted(count_distribution.items())},
        "text_conflict_rows": conflicts_seen, "conflict_rows_without_usable_variant": conflict_missing,
        "conflict_variant_count_disagrees_with_source": conflict_count_mismatch,
        "conflict_mode_agreement": dict(conflict_agreement),
        "label_status": "weak_rule_based_pseudo_labels_not_expert_truth", "accuracy": None,
        "accuracy_note": "No measured accuracy, precision or recall: examples were not independently expert-labeled. Synthetic unit checks validate specified rule behaviors only.",
        "unit_checks_passed": len(units), "unit_checks_total": len(units),
        "integrity_checks": {"unique_complaint_ids": checked_rows, "rows_equal_expected": checked_rows == expected_rows,
            "numeric_mode_indicators_binary": True, "mode_counts_equal_indicator_sums": True,
            "primary_only_when_exactly_one_mode": True},
        "limitations": ["Conservative English regex rules miss paraphrases, typos, multilingual descriptions, and implicit symptoms.",
            "Local negation/hypothetical rules are incomplete; complex narrative scope can produce false positives or false negatives.",
            "Historical, repaired, quoted or manufacturer-risk statements may still match; no causal or temporal truth is inferred.",
            "Descriptions can mention other vehicles or multiple incidents; subject attribution is not reliably resolved.",
            "A mode is a symptom mentioned in text, not a diagnosis, defect finding, recall outcome, or expert label.",
            "Zero indicators mean no accepted rule evidence, not verified absence of a failure.",
            "Conflict union retains all variants and can combine incompatible accounts. Use conflict flags/sensitivity analyses."],
        "runtime_seconds": round(time.time()-started, 3), "output_file": str(path),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(out/"report.json", report)
    lines = ["# Complaint failure/symptom rule audit", "", "These are weak rule-based pseudo-labels, not expert truth. No measured accuracy is available.", "",
             f"Classified {processed:,} complaint IDs using {len(MODE_NAMES)} fixed symptom modes.", "",
             "Source data is read-only; recall text, recall outcomes, component labels and outcome flags are not classification inputs.", "",
             "A primary mode is populated only for one-mode records. Unmatched descriptions remain `no_forced_class`. Conflicting narratives retain separate evidence and combined indicators.", "",
             "## Coverage", "", "| Mode | Complaint IDs with rule evidence |", "|---|---:|"]
    for mode in MODE_NAMES:
        lines.append(f"| {mode} | {mode_counts[mode]:,} |")
    lines += ["", "## Actual-data examples", "", "Examples are deterministic and selected for inspection, not a representative validation set. Full compact evidence is in `audit_examples.json`.", ""]
    for mode in MODE_NAMES:
        example = audit["per_mode"].get(mode, [])
        if example:
            e = example[0]
            lines += [f"- **{mode}** — `{e['complaint_id']}`: {e['evidence'][0]['excerpt']}"]
    lines += ["", "## Negation behavior", "", f"{len(units)} synthetic checks passed, including `no fire`, `airbag did not deploy`, `no warning`, hypothetical failures, component-only text, and each symptom class. This is a rule-contract check, not model accuracy.", "",
              "## Practical limits", "", *["- "+item for item in report["limitations"]], ""]
    (out/"audit_examples.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"rows": processed, "seconds": report["runtime_seconds"], "status_counts": dict(status_counts)}, indent=2), flush=True)

if __name__ == "__main__":
    main()
