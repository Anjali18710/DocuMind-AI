"""
Text of the illustrative SOPs in data/raw/ (used by generate_sample_sops.py).

These are sample documents written for the DocuMind AI demo, modelled on
typical integrated-steel-plant practice. They are NOT official SAIL documents.
"""

SOPS = [
    {
        "file": "LD_CONVERTER_OXYGEN_BLOWING_SOP.pdf",
        "sop_no": "BSP-SMS-012", "title": "Oxygen Blowing Operation in LD Converter",
        "department": "Steel Melting Shop", "revision": "02", "date": "05-Jun-2024",
        "body": """1. PURPOSE
To define the safe procedure for oxygen blowing in the LD (Linz-Donawitz) converters of Steel Melting Shop-II.
2. SCOPE
Applicable to LD Converters A, B and C. To be followed by converter operators, blowing pulpit operators and shift in-charges.
3. PREREQUISITES
- Lance cooling water flow minimum 180 m³/h and outlet temperature below 50°C
- Oxygen header pressure between 14 and 16 kg/cm²
- LD gas recovery system (IDCS) in auto mode and gas holder level below 80%
- Converter mouth and hood area cleared of all personnel
- Scrap and hot metal charged as per heat chart; slag-forming fluxes ready in bunkers
4. PERSONAL PROTECTIVE EQUIPMENT (PPE)
- Aluminised heat-resistant jacket and trousers
- Face shield with IR filter (shade 5)
- Safety helmet with neck protector
- Portable CO monitor (personal) for anyone on the converter platform
5. BLOWING PROCEDURE
Step 1 — Lower the lance to 2.5 m above bath level and start oxygen at 50% flow for ignition.
Step 2 — Confirm ignition within 60 seconds from the flame at the converter mouth. If there is no ignition within 60 seconds, raise the lance and stop oxygen.
Step 3 — Increase oxygen flow to 100% (approx. 600 Nm³/min) and bring the lance to 1.8 m working height.
Step 4 — Add lime and dolomite in two batches as per the flux chart during the first 4 minutes.
Step 5 — Watch for slopping. On heavy slopping, raise the lance by 0.3 m and reduce oxygen flow to 80%.
Step 6 — Stop blowing at the end point given by sub-lance or after approx. 16 minutes; raise the lance to parking position.
6. EMERGENCY — LANCE WATER LEAK
- Stop oxygen immediately and raise the lance to parking position
- Do NOT tilt the converter until water on the bath surface has fully evaporated (minimum 20 minutes)
- Water contact with liquid steel can cause a steam explosion
- Inform Shift In-charge (Ext. 3120) and Emergency Control Room (Ext. 100)
7. RECORDS
Record blow time, oxygen consumed and any abnormality in the Heat Log Book (form SMS-HL-02).
""",
    },
    {
        "file": "HOT_METAL_LADLE_HANDLING_SOP.pdf",
        "sop_no": "BSP-SMS-015", "title": "Hot Metal Ladle Handling and Transfer",
        "department": "Steel Melting Shop", "revision": "01", "date": "18-Mar-2024",
        "body": """1. PURPOSE
To ensure safe handling, lifting and transfer of hot metal ladles between the mixer, desulphurisation unit and LD converters.
2. SCOPE
Applies to all ladle cranes, crane operators, riggers and floor personnel in the charging bay.
3. LADLE CONDITION CHECKS (BEFORE EVERY USE)
- Refractory lining visually inspected; no red spots or bulging on the shell
- Trunnions and lifting hooks checked for cracks; last NDT not older than 6 months
- Ladle must be pre-heated to minimum 900°C if it has been idle for more than 2 hours
- Ladle must be completely dry; a wet or damp ladle must NEVER be filled
4. LIFTING AND TRANSFER
- Only a certified ladle crane (125 t capacity) may be used
- Maximum fill level: 300 mm below the ladle rim
- No person shall stand or pass under a suspended ladle
- Maintain an exclusion zone of 10 metres around the ladle path during transfer
- Travel speed must not exceed 30 m/min while carrying a full ladle
- Signal person with whistle and flag must guide every move
5. PPE
- Aluminised apron, heat-resistant gloves and face shield for anyone within 10 metres
- Safety boots with metatarsal guard
6. EMERGENCY — LADLE BREAKTHROUGH OR SPILL
Step 1 — Sound the bay siren and move everyone out of the bay immediately.
Step 2 — Do NOT use water on molten metal.
Step 3 — Crane operator to place the ladle in the nearest emergency pit if safe to do so.
Step 4 — Call Emergency Control Room: Ext. 100 and Fire Station: Ext. 101.
Step 5 — Allow spilled metal to solidify before any clean-up; use dry sand only.
""",
    },
    {
        "file": "CONTINUOUS_CASTER_BREAKOUT_SOP.pdf",
        "sop_no": "BSP-CC-003", "title": "Breakout Response at Slab Caster",
        "department": "Continuous Casting", "revision": "03", "date": "22-Aug-2024",
        "body": """1. PURPOSE
To define immediate actions in case of a breakout (liquid steel escaping through the solidified shell) at the slab casters.
2. SCOPE
Applies to Slab Caster Nos. 1 and 2, including casting floor, segment area and run-out table personnel.
3. EARLY WARNING SIGNS
- Breakout Prediction System (BOPS) alarm on the HMI
- Sudden rise in mould thermocouple temperature (more than 15°C in 10 seconds)
- Abnormal mould level fluctuation above ±5 mm
- Sparks or flames observed below the mould
4. IMMEDIATE ACTIONS ON BOPS ALARM
Step 1 — Reduce casting speed to 0.4 m/min automatically or manually.
Step 2 — Hold reduced speed for at least 30 seconds and watch thermocouple trends.
Step 3 — If the alarm clears, increase speed gradually by 0.1 m/min every minute.
5. ACTIONS ON CONFIRMED BREAKOUT
Step 1 — Press the EMERGENCY STOP on the casting floor; the tundish slide gate closes automatically.
Step 2 — Close the ladle shroud and swing the ladle turret to the safe position.
Step 3 — Evacuate the segment area and run-out table; nobody may stay below the casting floor.
Step 4 — Keep secondary cooling water ON to protect segments unless instructed otherwise.
Step 5 — Inform Shift In-charge (Ext. 3310), Emergency Control Room (Ext. 100) and Maintenance (Ext. 3325).
6. PPE FOR RECOVERY WORK
- Aluminised suit, face shield, heat-resistant gloves and safety boots
- Recovery work only under a valid Hot Work Permit (see BSP-SAF-014)
7. REPORTING
Breakouts must be reported in the Caster Incident Register within 2 hours.
""",
    },
    {
        "file": "HOT_STRIP_MILL_ROLL_CHANGE_SOP.pdf",
        "sop_no": "BSP-HSM-021", "title": "Work Roll Change in Finishing Mill Stands",
        "department": "Hot Strip Mill", "revision": "02", "date": "12-Apr-2024",
        "body": """1. PURPOSE
To ensure safe and quick changing of work rolls in finishing stands F1 to F7 of the Hot Strip Mill.
2. SCOPE
Applies to roll shop crew, mill operators, electrical and mechanical maintenance staff.
3. PREREQUISITES
- Mill stopped and "Roll Change Mode" selected on the pulpit HMI
- Electrical isolation of main drive and screw-down as per LOTO SOP BSP-EL-005
- Descaling water pumps isolated and pressure at 0 bar confirmed on gauge
- New roll set pre-checked in the roll shop, chocks fitted, roll diameter recorded
4. PPE
- Safety helmet, safety goggles, cut-resistant gloves, safety boots
- Ear protection (noise in the stand area exceeds 90 dB)
5. ROLL CHANGE PROCEDURE
Step 1 — Open the stand to maximum gap and lower the work-roll balance.
Step 2 — Connect the roll change car; confirm the latch indicator is green.
Step 3 — Pull the old roll set out; keep a distance of at least 3 metres from the moving car.
Step 4 — Push the new roll set in and engage the chock locks.
Step 5 — Restore hydraulics and run a zero-level calibration before rolling.
6. HAZARDS
- Crushing between chocks and the stand housing
- Hot surfaces: rolls may be above 60°C for 2 hours after rolling stops
- High-pressure water (descaling header up to 180 bar)
7. HANDOVER
The roll change supervisor removes personal locks only after all crew members confirm they are clear of the stand.
""",
    },
    {
        "file": "CONFINED_SPACE_ENTRY_SOP.pdf",
        "sop_no": "BSP-SAF-009", "title": "Confined Space Entry",
        "department": "Safety and Environment", "revision": "04", "date": "03-Jan-2024",
        "body": """1. PURPOSE
To prevent injury or death from toxic gases, oxygen deficiency, engulfment or entrapment when entering confined spaces.
2. SCOPE
Applies to all confined spaces including gas mains, dust catchers, bunkers, tanks, pits, sewers, stoves and ducts. Applies to employees and contractors.
3. PERMIT REQUIREMENT
Entry is allowed only with a valid Confined Space Entry Permit issued under the Permit-to-Work system (BSP-SAF-014). The permit is valid for one shift only.
4. ATMOSPHERIC TESTING (BEFORE ENTRY AND EVERY 2 HOURS)
- Oxygen: between 19.5% and 23.5%
- Carbon monoxide (CO): below 25 ppm
- Hydrogen sulphide (H2S): below 10 ppm
- Flammable gas: below 10% of the Lower Explosive Limit (LEL)
Test at the top, middle and bottom of the space with a calibrated multi-gas detector.
5. ISOLATION
- Positive isolation of all gas, steam, water and material lines by blinding or removing a spool piece
- Electrical and mechanical isolation with LOTO as per BSP-EL-005
- Purge with nitrogen and then air until readings are within limits
6. ENTRY RULES
- A trained attendant (hole watcher) must remain at the entry point at all times and must never enter
- Maximum 2 persons inside unless the permit states otherwise
- Continuous forced ventilation during the work
- Full body harness with lifeline for vertical entry
- 24 V or lower hand lamps only
7. EMERGENCY RESCUE
- Rescue only by persons wearing SCBA
- A rescue tripod and winch must be kept ready at the entry point for vertical spaces
- Call Emergency Control Room: Ext. 100
""",
    },
    {
        "file": "WORK_AT_HEIGHT_SOP.pdf",
        "sop_no": "BSP-SAF-011", "title": "Safe Work at Height",
        "department": "Safety and Environment", "revision": "02", "date": "14-May-2024",
        "body": """1. PURPOSE
To prevent falls of persons and objects when working at height.
2. DEFINITION
Work at height means any work at 1.8 metres or more above the ground or floor level, or near an unprotected edge or opening.
3. REQUIREMENTS
- Height Work Permit required for all work at 1.8 metres or more
- Only persons certified medically fit for height work (renewed every year) may work at height
- Full body harness with double lanyard and shock absorber; anchor above shoulder level
- 100% tie-off: at least one lanyard must be attached at all times
- Anchor point capacity minimum 22 kN (approx. 2,250 kg)
4. SCAFFOLDS AND LADDERS
- Scaffolds only erected by trained scaffolders and inspected before use; green tag = safe to use, red tag = do not use
- Toe boards of minimum 150 mm and double guard rails on all working platforms
- Ladders placed at 1:4 angle (1 m out for every 4 m up) and extended 1 metre above the landing
5. WEATHER RESTRICTIONS
- Stop outdoor height work when wind speed exceeds 40 km/h, during lightning, or heavy rain
6. FALLING OBJECTS
- Barricade the area below and post a watchman
- Tools must be tied with tool lanyards
7. RESCUE
A rescue plan must be available before work starts. A suspended worker must be rescued within 10 minutes to avoid suspension trauma. Emergency: Ext. 100.
""",
    },
    {
        "file": "PERMIT_TO_WORK_SOP.pdf",
        "sop_no": "BSP-SAF-014", "title": "Permit-to-Work System",
        "department": "Safety and Environment", "revision": "03", "date": "09-Feb-2024",
        "body": """1. PURPOSE
To control hazardous non-routine work through a written permit that confirms hazards are identified and controlled.
2. TYPES OF PERMIT
- Hot Work Permit — welding, gas cutting, grinding in hazardous areas
- Confined Space Entry Permit — see BSP-SAF-009
- Height Work Permit — see BSP-SAF-011
- Electrical Isolation Permit — see BSP-EL-005
- Gas Line Work Permit — work on BFG, COG or LDG lines
3. ROLES
- Permit Issuer: shift in-charge of the area (Executive level)
- Permit Receiver: supervisor of the team doing the work
- Safety Officer: countersigns permits for confined space and gas line work
4. PERMIT PROCEDURE
Step 1 — Receiver prepares the job safety analysis (JSA) and applies for the permit.
Step 2 — Issuer inspects the site, confirms isolations and gas tests, and signs.
Step 3 — Receiver briefs every team member in a toolbox talk; each member signs the permit.
Step 4 — Permit copy is displayed at the work site.
Step 5 — On completion, the receiver confirms the area is safe and the issuer closes the permit.
5. VALIDITY
- A permit is valid for one shift (maximum 8 hours) and must be renewed at shift change
- A permit becomes invalid immediately if any alarm sounds or conditions change
6. HOT WORK CONDITIONS
- Flammable gas below 1% of LEL within 15 metres
- Fire extinguisher and fire watcher present during work and for 30 minutes after
""",
    },
    {
        "file": "ELECTRICAL_LOTO_SOP.pdf",
        "sop_no": "BSP-EL-005", "title": "Electrical Isolation and Lockout-Tagout (LOTO)",
        "department": "Electrical Maintenance", "revision": "02", "date": "27-Jun-2024",
        "body": """1. PURPOSE
To protect personnel from unexpected energisation or start-up of equipment during maintenance.
2. SCOPE
Applies to all electrical and electro-mechanical equipment: motors, conveyors, cranes, drives, panels and HT switchgear.
3. LOTO PROCEDURE
Step 1 — Inform the operator and stop the equipment through the normal stop button.
Step 2 — Obtain an Electrical Isolation Permit from the Electrical Shift In-charge.
Step 3 — Isolate at the source: rack out the breaker (HT) or switch off and remove fuses (LT).
Step 4 — Apply a personal padlock and a "DANGER — DO NOT OPERATE" tag. Every worker applies his or her own lock.
Step 5 — Verify zero energy: try to start the equipment locally (test for start) and test for voltage with an approved tester.
Step 6 — Discharge stored energy: capacitors, springs, hydraulic accumulators and gravity loads.
4. RULES
- One person, one lock, one key. Never lend your key.
- Locks may be removed only by the person who applied them.
- For HT equipment (above 650 V), earthing must be applied after isolation.
5. REMOVING LOTO
- Confirm all tools removed and guards refitted
- Confirm all persons clear
- Remove personal locks, return the permit, and inform the operator before restart
6. ELECTRIC SHOCK — FIRST RESPONSE
- Switch off the supply before touching the victim; if not possible, use a dry wooden stick
- Start CPR if the victim is not breathing and call Medical Centre: Ext. 2400
""",
    },
    {
        "file": "CONVEYOR_MAINTENANCE_SOP.pdf",
        "sop_no": "BSP-RMHP-002", "title": "Safe Maintenance of Belt Conveyors",
        "department": "Raw Material Handling", "revision": "01", "date": "30-Jul-2024",
        "body": """1. PURPOSE
To prevent entanglement and crush injuries during cleaning and maintenance of belt conveyors in the Raw Material Handling Plant (RMHP).
2. HAZARDS
- Entanglement at head, tail and snub pulleys
- Nip points between belt and idlers
- Falling material from transfer points
- Coal and ore dust
3. GENERAL RULES
- Never clean, adjust or remove spillage from a running conveyor
- Never cross over or under a conveyor except at designated crossovers
- Pull-cord (emergency stop) switches must be tested every week; distance between pull-cord switches maximum 30 metres
- Guards must be refitted before restart
4. MAINTENANCE PROCEDURE
Step 1 — Stop the conveyor and apply LOTO at the MCC as per BSP-EL-005.
Step 2 — Operate the local pull-cord and the zero-speed switch check to confirm the belt cannot move.
Step 3 — Relieve belt tension at the gravity take-up by securing the counterweight.
Step 4 — Carry out the work; use belt clamps when cutting or splicing the belt.
Step 5 — Remove tools, refit guards, remove LOTO and give a pre-start warning siren of 30 seconds.
5. PPE
- Safety helmet, safety boots, goggles, dust mask (FFP2 or better)
- Close-fitting clothing; no loose sleeves near moving parts
""",
    },
    {
        "file": "OXYGEN_PIPELINE_SAFETY_SOP.pdf",
        "sop_no": "BSP-OXY-004", "title": "Safe Handling of Oxygen Pipelines and Cylinders",
        "department": "Oxygen Plant", "revision": "02", "date": "19-Sep-2024",
        "body": """1. PURPOSE
To prevent fires caused by oxygen enrichment and to ensure safe handling of oxygen pipelines and cylinders.
2. KEY HAZARD
Oxygen does not burn, but it makes everything else burn much faster. Clothing soaked in oxygen can catch fire from a small spark. Oxygen-enriched air is above 23.5% oxygen.
3. RULES FOR OXYGEN PIPELINES
- Oil and grease must NEVER come into contact with oxygen valves, fittings or regulators
- Use only oxygen-cleaned and degreased tools
- Open oxygen valves slowly; never open a valve fast
- Maximum velocity in carbon steel oxygen lines: 8 m/s
- Before hot work near an oxygen line, confirm oxygen in air is below 23.5%
4. OXYGEN CYLINDERS
- Store cylinders upright, chained, and at least 6 metres away from fuel gas cylinders (or separated by a fire wall)
- Cylinder colour code: black body with white shoulder
- Use a trolley to move cylinders; never roll or drag them
5. IF CLOTHING IS OXYGEN-ENRICHED
- Leave the area, do not smoke or go near any ignition source
- Air out clothing for at least 15 minutes before returning
6. EMERGENCY
On an oxygen leak or fire, isolate the supply valve if safe, evacuate, and call the Fire Station: Ext. 101 and Emergency Control Room: Ext. 100.
""",
    },
    {
        "file": "EOT_CRANE_OPERATION_SOP.pdf",
        "sop_no": "BSP-MM-006", "title": "Safe Operation of EOT Cranes",
        "department": "Mechanical Maintenance", "revision": "03", "date": "08-Oct-2024",
        "body": """1. PURPOSE
To ensure safe operation of Electric Overhead Travelling (EOT) cranes in all shops.
2. OPERATOR REQUIREMENTS
- Only authorised operators holding a valid crane operator licence (renewed every 3 years)
- Eyesight and medical fitness test every year
3. PRE-SHIFT CHECKS
- Test hoist, cross-travel and long-travel limit switches
- Test brakes of all motions with no load
- Check wire rope for broken wires, kinks or crushing; discard if 10 or more broken wires in one lay length
- Check hook safety latch and horn/siren
- Record checks in the Crane Log Book
4. OPERATING RULES
- Never exceed the Safe Working Load (SWL) marked on the crane
- Lift the load 150 mm first and check the brakes before full lift
- Sound the horn before every movement
- Never carry loads over people
- Follow signals from only one designated signal person, except the STOP signal which must be obeyed from anyone
5. WHEN TO STOP OPERATION
- Wind speed above 50 km/h for outdoor cranes
- Any abnormal noise, brake slip or limit-switch failure
6. EMERGENCY
On power failure with a suspended load, stay in the cabin, warn people below with the horn, and inform the Shift In-charge. Do not attempt to lower the load manually unless trained.
""",
    },
    {
        "file": "FIRE_EMERGENCY_RESPONSE_SOP.pdf",
        "sop_no": "BSP-FS-001", "title": "Fire Emergency Response",
        "department": "Fire Services", "revision": "05", "date": "11-Jan-2024",
        "body": """1. PURPOSE
To define actions for all personnel on discovering a fire anywhere in the plant.
2. ON DISCOVERING A FIRE
Step 1 — Shout "FIRE, FIRE" and break the glass of the nearest manual call point.
Step 2 — Call the Fire Station on Ext. 101 and give: location, what is burning, and whether anyone is trapped.
Step 3 — Attempt to fight the fire only if it is small, you are trained, and you have a clear escape route behind you.
Step 4 — If the fire cannot be controlled in 30 seconds, leave and close doors behind you.
3. CHOOSING THE EXTINGUISHER
- Class A (wood, paper, cloth): water or foam
- Class B (oil, grease, solvents): foam, CO2 or dry chemical powder (DCP)
- Electrical fires: CO2 or DCP only — never water
- Class D (metal fires, e.g. magnesium): special dry powder or dry sand only
- Molten metal: never use water — use dry sand
4. USING AN EXTINGUISHER — P.A.S.S.
Pull the pin, Aim at the base of the fire, Squeeze the handle, Sweep side to side. Stand 2 to 3 metres away.
5. EVACUATION
- Follow green exit signs to the designated assembly point of your department
- Do not use lifts
- Supervisors take a head count within 10 minutes and report missing persons to the Fire Officer
6. FIRE STATION CONTACTS
- Fire Station (main): Ext. 101
- Emergency Control Room: Ext. 100
""",
    },
    {
        "file": "SINTER_PLANT_DUST_CONTROL_SOP.pdf",
        "sop_no": "BSP-SP-008", "title": "Dust Control and Respiratory Protection in Sinter Plant",
        "department": "Sinter Plant", "revision": "01", "date": "25-Apr-2024",
        "body": """1. PURPOSE
To control exposure of personnel to respirable dust and to ensure proper use of respiratory protection in the Sinter Plant.
2. EXPOSURE LIMITS
- Respirable dust in the work area must be below 3 mg/m³ (8-hour average)
- Areas above this limit are marked "Respirator Zone" with yellow signboards
3. ENGINEERING CONTROLS
- Electrostatic precipitator (ESP) must be in service whenever the sinter machine is running
- ESP outlet emission limit: 50 mg/Nm³; if exceeded for 30 minutes, inform the Environment Cell (Ext. 2650)
- Dedusting fans at transfer points must be checked every shift
- Water sprinklers on raw material conveyors to be kept ON in dry weather
4. RESPIRATORY PROTECTION
- Minimum FFP2 disposable respirator in Respirator Zones; FFP3 or half-mask with P3 filter for cleaning of ESP hoppers
- Fit check before each use; beards prevent a proper seal
- Replace disposable respirators every shift or when breathing becomes difficult
5. HOUSEKEEPING
- Use vacuum cleaning or wet cleaning only; dry sweeping with brooms and compressed-air blowing are prohibited
6. HEALTH SURVEILLANCE
All Sinter Plant personnel undergo lung function testing (spirometry) once a year at the Occupational Health Centre.
""",
    },
    {
        "file": "HEAT_STRESS_FIRST_AID_SOP.pdf",
        "sop_no": "BSP-OHS-003", "title": "Prevention and First Aid for Heat Stress and Burns",
        "department": "Occupational Health Services", "revision": "02", "date": "02-Apr-2024",
        "body": """1. PURPOSE
To prevent heat-related illness among personnel working near furnaces, converters and casting floors, and to give first aid for heat illness and burns.
2. PREVENTION
- Drink 250 ml of water every 20 minutes during hot work, even if not thirsty
- ORS (oral rehydration salts) is available at all shop-floor rest rooms
- Work-rest cycle in extreme heat zones: 45 minutes work followed by 15 minutes rest in a cool room
- New workers must be acclimatised over 5 to 7 days
3. SIGNS OF HEAT EXHAUSTION
Heavy sweating, weakness, dizziness, headache, nausea, cold and clammy skin.
First aid: move to a cool place, loosen clothing, give ORS or water in small sips, rest for at least 30 minutes.
4. SIGNS OF HEAT STROKE (MEDICAL EMERGENCY)
Hot, dry skin, confusion, fainting, body temperature above 40°C.
First aid:
Step 1 — Call Medical Centre: Ext. 2400 immediately.
Step 2 — Move the person to shade and cool the body with water and fanning; place ice packs at the neck, armpits and groin.
Step 3 — Do NOT give anything to drink if the person is confused or unconscious.
5. FIRST AID FOR THERMAL BURNS
- Cool the burn under clean running water for at least 20 minutes
- Remove rings and watches before swelling starts
- Do NOT apply ice, toothpaste, oil or any cream
- Do NOT burst blisters
- Cover loosely with a clean non-fluffy dressing and send to the Medical Centre
""",
    },
    {
        "file": "PLC_INTERLOCK_BYPASS_SOP.pdf",
        "sop_no": "BSP-CA-010", "title": "Management of PLC/DCS Logic Changes and Interlock Bypass",
        "department": "Control and Automation", "revision": "01", "date": "16-Jul-2024",
        "body": """1. PURPOSE
To ensure that changes to PLC/DCS programs and any bypass (forcing) of safety interlocks are authorised, recorded and removed in time.
2. SCOPE
Applies to all PLC, DCS and SCADA systems maintained by the Control and Automation (C&A) Department, including level-2 systems.
3. LOGIC CHANGE PROCEDURE
Step 1 — Raise a Logic Change Request (form CA-LCR-01) describing the change and the reason.
Step 2 — Get approval from the Area Head of C&A and the Operations Head of the concerned shop.
Step 3 — Take a full backup of the existing program and store it on the C&A backup server with date and version.
Step 4 — Test the change in simulation mode where available.
Step 5 — Download during a planned stoppage, verify, and update the change register.
4. INTERLOCK BYPASS (FORCING)
- Safety interlocks (e.g. gas pressure low trip, lance water flow low trip, crane over-travel) may be bypassed only with a written Interlock Bypass Permit
- Maximum bypass duration: 8 hours (one shift); extension needs fresh approval
- A red "INTERLOCK BYPASSED" tag must be placed on the HMI screen and on the field device
- An alternative safety measure (e.g. manual watch) must be in place for the whole duration
- All active bypasses must be reviewed at every shift handover
5. PASSWORDS AND ACCESS
- Engineering station passwords are changed every 90 days
- USB drives may be used only after virus scanning on the C&A clean station
6. RECORDS
All changes and bypasses are recorded in the C&A Change Register and kept for 3 years.
""",
    },
]

# Delivered as an image-only PDF to demonstrate OCR on scanned documents.
SCANNED_SOP = {
    "file": "GAS_DETECTOR_CALIBRATION_SOP_SCANNED.pdf",
    "sop_no": "BSP-GS-006", "title": "Portable Gas Detector Bump Test and Calibration",
    "department": "Safety and Environment", "revision": "01", "date": "04-Mar-2024",
    "body": """1. PURPOSE
To make sure portable gas detectors give correct readings before they are used.
2. BUMP TEST
- A bump test must be done before every shift or every use
- Expose the detector to the test gas for 30 seconds
- The detector must alarm for CO, H2S, O2 and LEL sensors
- If any sensor fails the bump test, do NOT use the detector; send it for calibration
3. CALIBRATION
- Full calibration every 30 days at the Gas Safety Laboratory
- Calibration gas cylinders must be within expiry date
- Calibration label on the detector must show the due date
4. ALARM SETTINGS
- CO low alarm: 20 ppm, CO high alarm: 50 ppm
- O2 low alarm: 19.5 %, O2 high alarm: 23.5 %
- LEL alarm: 10 %
5. CONTACT
Gas Safety Laboratory: Ext. 2315
""",
}

# A newer revision of the gas-leak SOP, NOT loaded at start-up.
# Upload it from the Admin page to see automatic revision replacement.
REVISION_DEMO = {
    "file": "GAS_LEAK_EMERGENCY_SOP_Rev04.pdf",
    "sop_no": "BSP-GS-004", "title": "Emergency Response Procedure for Gas Leak",
    "department": "Safety and Environment", "revision": "04", "date": "15-Sep-2024",
    "body": """1. PURPOSE
To define the immediate response actions for all personnel upon detection of a gas leak at Bokaro Steel Plant, covering Blast Furnace Gas (BFG), Coke Oven Gas (COG), and Linz-Donawitz Gas (LDG).
2. SCOPE
Applicable to all areas where process gases are present. Mandatory for all plant personnel, contractors, and visitors.
3. GAS HAZARD CLASSIFICATION
- Blast Furnace Gas (BFG): CO content 20-28%. Highly toxic. Odourless.
- Coke Oven Gas (COG): Contains H2, CH4, CO. Flammable. Toxic.
- LD Gas (LDG): CO content 60-70%. Extremely toxic. Odourless.
CRITICAL: BFG and LDG are odourless. Never rely on smell for detection. Always carry a personal CO monitor.
4. DETECTION THRESHOLDS (REVISED)
- CO alarm (warning): 20 ppm
- CO alarm (evacuate): 35 ppm
- Explosive limit for COG: 6% in air (Lower Explosive Limit)
5. IMMEDIATE RESPONSE PROCEDURE
Step 1 — On Detection of Gas Leak
- Do NOT operate any electrical switches or use mobile phones in the affected area
- Raise the alarm using the nearest manual call point
- Call Emergency Control Room: Extension 100
Step 2 — Evacuation
- Evacuate all non-essential personnel immediately, moving upwind
- Minimum safe distance: 150 metres from the leak point (revised from 100 metres)
- Assemble at the department assembly point for head count
Step 3 — Isolate the Source (Trained Personnel Only)
- Only Gas Safety Officers wearing SCBA may attempt isolation
Step 4 — Notify
- Emergency Control Room: Extension 100
- Gas Safety Department: Extension 2310
6. RE-ENTRY PROTOCOL
- Re-entry only after written clearance from the Gas Safety Officer
- CO level must be below 20 ppm at all entry points
7. REVISION NOTE
Revision 04 lowers the evacuation threshold from 50 ppm to 35 ppm and increases the minimum safe distance from 100 to 150 metres.
""",
}
