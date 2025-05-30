"Clockwork Descent" by "Andrew Brookins"

Use scoring.
Include Exit Lister by Gavin Lambert.

When play begins:
	now the score is 0;
	now the maximum score is 60;
	now the left hand status line is
		"[the player's surroundings] / [turn count] / [score]";
	now the right hand status line is "".

[Level 0: Tower Entrance]

Tower Entrance is a room. "You stand at the base of a massive clockwork tower, its brass and copper walls stretching impossibly high above you. Enormous gears slowly turn along its exterior, driving countless mechanisms. A series of iron rungs forms a ladder that ascends to what appears to be an aerial platform high above. Wind whistles around you, carrying the scent of oil and steam. A weathered sign nearby reads 'Caution: Clockwork mechanisms in operation. Authorized personnel only.'"

The iron ladder is scenery in Tower Entrance. "A sturdy set of iron rungs bolted directly into the tower's exterior wall, leading upward to the platform."
Understand "rungs" or "iron rungs" as the iron ladder.

Instead of climbing the iron ladder:
	increase the score by 2;
	move the player to Aerial Platform;
	say "You climb the iron rungs, carefully navigating your way up the tower's exterior. After what feels like an eternity of climbing, you finally reach the top. [bracket]+2 points[close bracket]".

The warning sign is scenery in Tower Entrance. "The weathered metal sign reads: 'CAUTION: Clockwork mechanisms in operation. Authorized personnel only.'"
Understand "sign" or "weathered sign" or "metal sign" or "caution" as the warning sign.


[Level 1: Aerial Platform]

Aerial Platform is a room. "You stand on a wind-swept sky dock atop a flying clockwork airship platform attached to the tower. Gears whirr, propellers spin, and steam vents hiss around you. A dirigible is moored to a spire to the east. A cargo crane stands nearby, currently misaligned, blocking a large elevator hatch in the floor. A narrow metal gantry extends toward the tower's edge, creaking ominously."

The dirigible is scenery in Aerial Platform. "A sleek brass and mahogany airship tied to a mooring post. Its balloon is made of treated canvas, taut with lifting gas."

A device can be aligned or misaligned. A device has a text called alignment description.
The crane is a device in Aerial Platform. The crane is misaligned. The alignment description of the crane is "misaligned".
The control panel is scenery in Aerial Platform. "A brass-plated panel with an empty slot shaped for a lever. Above it is a diagram showing gear alignment positions: circle, triangle, square."

Workshop is a room. "An expansive mechanical workshop fills this level of the tower. Churning gears, belt-driven machines, and boiling pipes surround you in every direction. The air is dimmer here, oil-stained and heavy with the scent of machine grease - a stark contrast to the airy platform above. Steam hisses from valves, and the floor vibrates with the motion of a colossal central gear assembly. Conveyor belts carry parts across the room. Doorways lead to a storage area to the east, a control room to the north, and a machine bay to the west."

The elevator hatch is a door. It is down of Aerial Platform and up of Workshop. The elevator hatch is closed and locked. Understand "hatch" or "elevator hatch" or "floor hatch" as the elevator hatch.

The gantry is a device in Aerial Platform. The gantry is scenery.
The gantry can be intact or collapsed.
The gantry is intact.

A workbench is scenery in Aerial Platform. "A sturdy steel bench marked with tool dents. A toolbox rests upon it."
A toolbox is a container on the workbench. It is closed and openable. "A battered metal toolbox, likely holding useful tools." Inside the toolbox are a bronze lever and a heavy wrench.

The bronze lever is a thing.
Understand "lever" as the bronze lever.
The description is "A heavy bronze lever shaped perfectly to fit the control panel's slot." The bronze lever is portable.
The heavy wrench is a thing.
Understand "wrench" as the heavy wrench.
The description is "A robust wrench for tightening nuts and bolts." The heavy wrench is portable.

A supply crate is a container in Aerial Platform. It is closed and openable. "A reinforced wooden crate stamped with the airship's insignia." Inside the supply crate is the brass spyglass.
The brass spyglass is a thing in the supply crate.
Understand "spyglass" or "glass" as the brass spyglass.
The description is "A finely crafted clockwork spyglass of polished brass." The brass spyglass is portable.

After taking the bronze lever:
	increase the score by 1;
	say "You take the bronze lever. [bracket]+1 point[close bracket]".

After taking the heavy wrench:
	increase the score by 1;
	say "You take the heavy wrench. [bracket]+1 point[close bracket]".

After taking the brass spyglass:
	increase the score by 3;
	say "You pocket the brass spyglass. [bracket]+3 points[close bracket]".

Instead of inserting the bronze lever into the control panel when the crane is misaligned:
	now the crane is aligned;
	increase the score by 5;
	now the elevator hatch is unlocked;
	now the elevator hatch is open;
	say "You slot the bronze lever into the control panel. Gears grind as the crane rotates into alignment, and steam hisses as the hatch unlocks and swings open. [bracket]+5[close bracket]".

Instead of inserting the bronze lever into the control panel when the crane is aligned:
	say "The lever is already in place and the crane hums contentedly.".

Instead of inserting something into the control panel:
	say "That doesn't fit the lever slot.".

Instead of going down when the gantry is intact and the elevator hatch is closed:
	now the gantry is collapsed;
	decrease the score by 10;
	move the player to Workshop;
	end the story saying "The metal groans under your weight! The gantry buckles and you plunge through a trapdoor in the floor!".

Cogsworth is a person in Aerial Platform. "A small clockwork automaton tinkerer clings to the gantry, its right leg hinge loose." Cogsworth can be repaired or broken. Cogsworth is broken.

The lift-code is a number that varies. The lift-code is 0.

After giving the heavy wrench to Cogsworth when Cogsworth is broken:
	now Cogsworth is repaired;
	now lift-code is 472;
	now the player is lift-code-aware;
	increase the score by 5;
	say "You hand the wrench to Cogsworth. He tightens his leg hinge with a few clicks, stands upright, and says, 'The code for the workshop lift is 472.' [bracket]+5[close bracket]".

After giving the heavy wrench to Cogsworth when Cogsworth is repaired:
	say "Cogsworth pats his leg gratefully but doesn't need further help.".

A clockwork raven is a kind of animal.
A clockwork raven called the Raven is in Aerial Platform. The description of the Raven is "A metallic raven with glowing red eyes circles above, watching you.".

The Steam Valve is a device.
The Steam Valve is in Aerial Platform.
The Steam Valve can be switched on or switched off.
The Steam Valve is switched off.
The description of the Steam Valve is "A brass valve controlling a steam vent.".

A steam vent is scenery.
The steam vent is in Aerial Platform.
The steam vent can be active or inactive.
The steam vent is inactive.
The description of the steam vent is "A vent that can release a burst of steam when powered.";

Instead of switching on the Steam Valve:
	now the steam vent is active;
	say "Steam hisses from the vent!".

After switching on the Steam Valve when the steam vent is active and the Raven is in the location:
	remove the Raven from play;
	increase the score by 5;
	now a small gear is in the location;
	say "The raven screeches and flies away under the blast of steam, dropping a small brass gear. [bracket]+5[close bracket]".

A small gear is a thing. The description is "A tiny brass gear once held by the raven." The small gear is portable.

After taking the small gear:
	increase the score by 1;
	say "You pick up the small gear. [bracket]+1[close bracket]".

Instead of going down when the elevator hatch is open and the elevator hatch is unlocked:
	move the player to Workshop;
	say "You descend into the workshop, gears clanking behind you.".
	
[Level 2: Workshop - Changed from single room to multiple rooms]

The Storage Area is east of Workshop. "This cluttered space houses spare parts, tools, and maintenance supplies. Metal shelves line the walls, packed with components and engineering materials. A heavy tool chest sits against the far wall. The main workshop lies to the west."

The Control Room is north of Workshop. "The workshop's nerve center is filled with monitoring equipment and control panels. Pressure gauges, brass dials, and lever arrays cover the walls. A large service elevator platform occupies the center of the room, its control panel gleaming with polished brass fixtures. The main workshop is to the south."

The Machine Bay is west of Workshop. "The constant din of operating machinery fills this high-ceilinged chamber. Massive gear assemblies turn overhead, while automated belt mechanisms transport components across the room. Steam regularly vents from pipes along the walls. A small floor hatch bolted to the floor appears to be an emergency exit. The main workshop lies to the east."

[Workshop machinery and objects redistributed across rooms]

The service elevator is a device in the Control Room.
The service elevator can be locked or unlocked. The service elevator is locked.
Understand "lift" or "platform" or "elevator" or "service lift" or "workshop lift" as the service elevator.
The description of the service elevator is "A large industrial elevator platform designed to transport heavy machinery between levels. Its control panel has a numeric keypad for entering a code."

The elevator control panel is scenery in the Control Room. "A control panel with a numeric keypad and a large button marked 'DESCEND'. The keypad appears to require a 3-digit code."
Understand "control panel" or "panel" or "keypad" or "numeric keypad" as the elevator control panel.

The elevator button is part of the elevator control panel.
Understand "button" or "descend button" as the elevator button.

A person can be lift-code-aware or lift-code-unaware. A person is usually lift-code-unaware.

Instead of pushing the elevator button:
	if the service elevator is locked:
		say "The button refuses to activate. The control panel flashes red - it seems to require a code.";
	otherwise:
		say "As you press the button, the elevator platform begins to descend with a mechanical groan.";
		end the story finally saying "You descend further into the tower's depths. Level 2 complete!"

Understand "enter [text] on keypad" or "enter [text]" or "type [text]" or "input [text]" or "set dial to [text]" as entering code.
Entering code is an action applying to one topic.

Check entering code:
	if the player is not in the Control Room:
		say "There's no keypad here to enter a code." instead.

Carry out entering code:
	if the topic understood matches "472":
		if the service elevator is locked:
			now the service elevator is unlocked;
			increase the score by 10;
			say "You enter 472 on the keypad. With a loud clunk, the elevator powers on and its panel glows green! [bracket]+10 points[close bracket]";
		otherwise:
			say "The elevator is already activated.";
	else:
		say "The keypad flashes red. That code doesn't seem to work.";
		if a random chance of 1 in 2 succeeds:
			say "Suddenly, a gauge spins into the red zone as you input the wrong code...";
			activate-steam-trap.

To activate-steam-trap:
	if the steam pipe is not leaking:
		now the steam pipe is leaking;
		say "A pipe bursts in the Workshop, releasing a scalding jet of steam into the room! You need to find a way to stop it before it fills the entire workshop level!";
		move the steam cloud to Workshop.

The steam pipe is a device in Workshop. The steam pipe can be functioning or leaking. The steam pipe is functioning.
The description of the steam pipe is "A thick copper pipe running along the wall, carrying superheated steam from lower levels. [if the steam pipe is leaking]It has a large crack spewing scalding steam into the room![otherwise]It looks solid, if under considerable pressure.[end if]".
Understand "pipe" or "pipes" or "copper pipe" as the steam pipe.

The steam cloud is a thing. "Scalding steam fills parts of the room, making it dangerous to move around freely."
The description is "A billowing cloud of hot steam that could cause serious burns if you walk through it."

A spare gasket is a thing in the Storage Area. "A rubber gasket sits on a nearby shelf, appearing to be the right size for pipe repairs."
The description is "A thick rubber gasket designed to seal high-pressure pipe connections."
Understand "gasket" or "rubber gasket" as the spare gasket.

Instead of taking the spare gasket:
	now the player carries the spare gasket;
	increase the score by 2;
	say "You take the spare gasket. [bracket]+2 points[close bracket]".

Instead of fixing the steam pipe:
	if the player carries the spare gasket:
		now the steam pipe is functioning;
		remove the steam cloud from play;
		increase the score by 5;
		say "You carefully apply the spare gasket to the broken pipe. After a tense moment, the seal holds and the steam stops spewing out. [bracket]+5 points[close bracket]";
	otherwise:
		say "You need something to seal the broken pipe.".

Understand "fix [something]" or "repair [something]" or "seal [something]" as fixing.
Fixing is an action applying to one thing.

Check fixing:
	if the noun is not the steam pipe:
		say "That doesn't need fixing." instead.

Carry out fixing:
	say "You need something to fix this with.".

The copper gear key is a thing in the Machine Bay. "A distinctive copper gear with odd teeth lies partially hidden beneath a belt mechanism."
The description is "An unusual copper gear with teeth arranged in an intricate pattern. It appears to be designed as a key rather than a functional gear."
Understand "copper gear" or "gear key" or "key" as the copper gear key.

Instead of taking the copper gear key:
	now the player carries the copper gear key;
	increase the score by 5;
	say "You take the copper gear key. It feels like it might fit into a specialized lock somewhere. [bracket]+5 points[close bracket]".

A tool chest is a container in the Storage Area. It is closed and openable. "A heavy tool chest sits against the far wall."
The description is "A large, industrial-strength chest for storing workshop tools."

Marigold is a woman in the Storage Area. "A woman in grease-stained overalls crouches [if the steam pipe is leaking]behind the tool chest, coughing[otherwise]by the tool chest, examining some components[end if]."
The description is "A tough-looking woman with practical overalls and calloused hands. A patch on her jacket identifies her as 'Marigold, Chief Engineer'."

After fixing the steam pipe when Marigold is in the Storage Area and the steam pipe is in Workshop:
	say "Word seems to travel fast. Marigold stands up straight in the Storage Area, her coughing subsiding. 'Thank you for that! I was afraid the whole level would fill with steam. That pipe's been troublesome for weeks.'";
	now Marigold carries the pocket watch.

The pocket watch is a thing.
The description is "A polished brass pocket watch with intricate clockwork visible through a glass panel. Looking carefully, you notice the numbers '472' engraved inside the cover."
Understand "watch" or "brass watch" as the pocket watch.

After examining the pocket watch:
	now the player is lift-code-aware;
	say "You notice the numbers '472' delicately engraved inside the cover. That looks like it could be important."

Instead of asking Marigold about "help" when Marigold carries the pocket watch:
	now the player carries the pocket watch;
	increase the score by 5;
	say "'Here, take this as thanks for your help,' Marigold says, handing you a pocket watch. 'And a bit of advice - in the forge below, mind the pattern: short-long-long-short. It's the sequence to calibrate the smelter.' [bracket]+5 points[close bracket]".

A gearling is a kind of animal. "A fist-sized mechanical creature scuttles across the floor, its gear-shaped legs clicking on the metal." Understand "gear spider" or "mechanical pest" or "gear creature" as a gearling.
The description of a gearling is "A small mechanical pest resembling a spider made of gears and springs. Its tiny metal mandibles look sharp enough to cut through wire."

A gearling called a skittering gearling is in Workshop.
A gearling called a clicking gearling is in the Machine Bay.
A gearling called a whirring gearling is in the Machine Bay.

The machine oil is a thing in the tool chest. "A can of machine oil sits on a shelf."
The description is "A metal can filled with slick lubricating oil for machinery."
Understand "oil" or "can" or "oil can" as the machine oil.

Instead of taking the machine oil:
	now the player carries the machine oil;
	increase the score by 1;
	say "You take the can of machine oil. [bracket]+1 point[close bracket]".

Instead of attacking a gearling:
	say "The gearling is too quick and skitters away from your attack.".

Instead of pouring the machine oil on a gearling:
	remove the noun from play;
	say "You pour oil onto the gearling. It slips and slides uncontrollably before tumbling into a crack in the floor, disappearing from sight.";
	increase the score by 2;
	say "[bracket]+2 points[close bracket]";
	if the number of gearlings in the location is 0:
		if all gearlings are not in the location and the scrap metal is not in a room:
			say "With the last of the gearlings in this area gone, you've made progress against the infestation.";
		otherwise if all gearlings are not in a room:
			say "With the last of the gearlings gone, you notice they've dropped some scrap metal.";
			now the scrap metal is in the Machine Bay;
		otherwise:
			say "One gearling down, but there seem to be more elsewhere in the workshop.";

Understand "pour [something] on [something]" as pouring it on. Pouring it on is an action applying to two things.

Check pouring it on:
	if the noun is not the machine oil:
		say "You can't pour that." instead.

Carry out pouring it on:
	say "You pour [the noun] on [the second noun], but nothing useful happens.".

The scrap metal is a thing. "Some scrap metal pieces lie on the floor."
The description is "Various small metal pieces, gears, and springs from the defeated gearlings."
Understand "scrap" or "metal" as the scrap metal.

Instead of taking the scrap metal:
	now the player carries the scrap metal;
	increase the score by 1;
	say "You collect the scrap metal. It might be useful for something. [bracket]+1 point[close bracket]".

The emergency hatch is a door. It is down from the Machine Bay. The emergency hatch is locked.
Understand "hatch" or "floor hatch" or "emergency exit" or "bolted hatch" as the emergency hatch.
The description is "A small metal hatch bolted to the floor, likely an emergency exit. It appears to be locked from this side."

The crowbar is a thing in Workshop. "A sturdy crowbar leans against one of the workbenches."
The description is "A solid steel crowbar, perfect for prying things open."
Understand "bar" or "pry bar" as the crowbar.

Instead of taking the crowbar:
	now the player carries the crowbar;
	increase the score by 1;
	say "You take the crowbar. [bracket]+1 point[close bracket]".

Instead of unlocking the emergency hatch with the crowbar:
	now the emergency hatch is unlocked;
	increase the score by 3;
	say "You wedge the crowbar into the seam of the hatch and heave with all your strength. With a screech of metal, the bolts give way and the hatch swings open. [bracket]+3 points[close bracket]".

Instead of going down through the emergency hatch when the emergency hatch is unlocked:
	say "You carefully lower yourself through the hatch and begin descending the narrow spiral staircase into darkness below.";
	end the story finally saying "You take the emergency route deeper into the tower. Level 2 complete!"

[Level 3: Gear Forge]

Main Forge is a room. "You've entered the fiery heart of the tower's manufacturing operations. This vast chamber glows with intense orange light from molten metal baths and a massive furnace dominating the center. The heat is oppressive, making sweat bead on your skin instantly. Enormous gears line the walls, awaiting installation elsewhere in the tower, while conveyor belts transport raw materials to various workstations. The continuous clanking of an automated hammer punctuates the roar of the furnace. Steam rises through grates in the floor, suggesting you're nearing the boiler levels. Doorways lead to a control room to the north, a materials storage area to the east, and a cooling chamber to the west."

Forge Control Room is north of Main Forge. "This room overlooks the main forge floor through a large heat-resistant glass window. The walls are lined with gauges, dials, and levers controlling various aspects of the forging process. A large smelter control panel dominates the center of the room, featuring four sequential levers arranged in a row. A chalkboard hangs on the wall near the panel. The intense heat of the main forge is somewhat mitigated here, though the air remains uncomfortably warm. The main forge area lies to the south."

Materials Storage is east of Main Forge. "Raw materials for the forge's operation are stored in this high-ceilinged chamber. Bins of metal ingots, crates of coal, and barrels of various industrial chemicals line the walls. A massive magnetic crane system runs along ceiling tracks, designed to move heavy materials to and from the main forge. A control box for the crane hangs from a chain nearby. Warning signs about magnetic hazards are posted prominently. The main forge lies to the west."

Cooling Chamber is west of Main Forge. "This room serves as both a cooling area for newly forged items and a holding cell. The temperature here is noticeably lower than the main forge, with large fans circulating air. Racks of cooling molds line one wall, while a series of water troughs stand ready for quenching hot metal. In the corner, behind sturdy iron bars, is what appears to be a large cage. The main forge area is to the east."

[Main Forge Scenery and Objects]

The massive furnace is scenery in Main Forge. "A roaring industrial furnace, its open mouth glowing white-hot with molten metal inside. The heat radiating from it is almost unbearable. A series of molds sit nearby, and a heavy gear-shaped door is set into the floor near the base of the furnace."
Understand "furnace" as the massive furnace.

The automated hammer is scenery in Main Forge. "A gigantic steam-powered hammer that rhythmically pounds red-hot metal. Its continuous clanking follows a distinct pattern: one short strike, followed by two long strikes, then another short strike."
Understand "hammer" as the automated hammer.

After examining the automated hammer:
	if the player is smelter-pattern-unaware:
		now the player is smelter-pattern-aware;
		say "You notice the hammer strikes follow a distinct pattern: short-long-long-short. This seems deliberate rather than random.";

The gear door is a door. It is down from Main Forge. The gear door is scenery. The gear door is closed and locked.
Understand "gear-shaped door" or "floor door" or "hatch" or "gear hatch" as the gear door.
The description is "A circular hatch set into the floor, designed like an enormous gear. It appears to be a doorway down to lower levels. The locking mechanism has a gear-shaped slot where a key component seems to be missing."

The smelting pit is scenery in Main Forge. "A deep pit filled with bubbling molten metal. Excess material drains through a large pipe at the bottom, presumably to be recycled. It's far too hot to approach without protection."
Understand "pit" as the smelting pit.

The smelting pit can be molten or solidified. The smelting pit is molten.

The water valve is a device in Main Forge. The water valve can be switched on or switched off. The water valve is switched off.
Understand "valve" as the water valve.
The description is "An emergency water valve designed to flood the smelting pit with cooling water in case of an emergency."

Instead of switching on the water valve:
	if the smelting pit is molten:
		now the smelting pit is solidified;
		now the water valve is switched on;
		say "You turn the valve. Water gushes into the smelting pit, causing clouds of steam to billow up as the molten metal rapidly cools and solidifies.";
	otherwise:
		say "The water valve is already active and the smelting pit has been cooled.";

[Steam Golem]

The Steam Golem is an animal in Main Forge. "A monstrous construct of iron and hydraulics lumbers around the forge, superheated steam escaping from its joints. Its metal body glows red-hot."
The description is "A fearsome creation of metal and steam, standing about eight feet tall. Its body is constructed of iron plates riveted together, with glowing red-hot elements visible through the gaps. Steam continuously vents from its joints as it moves with surprising speed and agility for something so massive."

The Steam Golem can be operational or neutralized. The Steam Golem is operational.

Instead of attacking the Steam Golem:
	say "Your attack has no effect on the super-heated metal body of the golem. It turns toward you menacingly, steam hissing from its joints."

After switching on the water valve when the Steam Golem is in the location and the Steam Golem is operational:
	now the Steam Golem is neutralized;
	increase the score by 7;
	say "As water floods the smelting pit, some of it splashes onto the Steam Golem. With a hissing screech, the creature seizes up as its heated components rapidly cool and contract. It freezes in place, becoming immobile. [bracket]+7 points[close bracket]";

[Forge Control Room Items]

The smelter control panel is scenery in Forge Control Room. "A complex control station with four sequential levers arranged in a row. Each lever can be pulled for either a short or long duration to calibrate the smelting process."
Understand "control panel" or "panel" as the smelter control panel.

The four levers are part of the smelter control panel. Understand "levers" or "sequential levers" or "row of levers" as the four levers.

The chalkboard is scenery in Forge Control Room. "A slate board covered with chalk dust. Someone has drawn four symbols that look like Morse code: a dot, followed by two dashes, and then another dot (· — — ·)."
Understand "chalk board" or "board" or "slate" as the chalkboard.

After examining the chalkboard:
	if the player is smelter-pattern-unaware:
		now the player is smelter-pattern-aware;
		say "The pattern on the board - dot, dash, dash, dot - reminds you of a sequence: short-long-long-short.";

A person can be smelter-pattern-aware or smelter-pattern-unaware. A person is usually smelter-pattern-unaware.

A device can be calibrated or uncalibrated. A device has a text called calibration description.
The smelter is a device in Forge Control Room. The smelter is uncalibrated. The calibration description of the smelter is "uncalibrated".

Understand "calibrate smelter" or "set smelter" or "use levers" or "pull levers in pattern" or "pull levers short long long short" as calibrating the smelter.
Calibrating the smelter is an action applying to nothing.

Check calibrating the smelter:
	if the player is not in Forge Control Room:
		say "The smelter controls aren't here." instead.

Carry out calibrating the smelter:
	if the smelter is uncalibrated:
		now the smelter is calibrated;
		increase the score by 10;
		now the blank mold is empty;
		say "You pull the levers in the sequence: short pull, long pull, long pull, short pull. The smelter hums as it calibrates to the correct temperature. Molten metal flows into the waiting mold in the main forge. [bracket]+10 points[close bracket]";
	otherwise:
		say "The smelter is already perfectly calibrated.";

Understand "pull [text]" as pulling levers with pattern. Pulling levers with pattern is an action applying to one topic.

Check pulling levers with pattern:
	if the player is not in Forge Control Room:
		say "There are no levers to pull here." instead.

Carry out pulling levers with pattern:
	if the topic understood matches "short long long short":
		if the smelter is uncalibrated:
			now the smelter is calibrated;
			increase the score by 10;
			now the blank mold is empty;
			say "You pull the levers in the sequence: short pull, long pull, long pull, short pull. The smelter hums as it calibrates to the correct temperature. Molten metal flows into the waiting mold in the main forge. [bracket]+10 points[close bracket]";
		otherwise:
			say "The smelter is already perfectly calibrated.";
	else:
		say "You pull the levers in that pattern, but the smelter temperature fluctuates wildly. That doesn't seem to be the correct sequence.";

[Materials Storage Items]

The magnetic crane is a device in Materials Storage. The magnetic crane can be powered or unpowered. The magnetic crane is powered.
Understand "crane" or "magnetic" as the magnetic crane.
The description is "A massive industrial crane with a powerful electromagnet at its end, designed to move heavy metal objects throughout the forge. It's currently [if the magnetic crane is powered]powered on, its electromagnetic field active[otherwise]powered off and safe to approach[end if]."

The crane control box is scenery in Materials Storage. "A control box hanging from a chain with buttons to operate the overhead magnetic crane. There's a large red emergency stop button prominently displayed."
Understand "control box" or "box" as the crane control box.

The red button is part of the crane control box. "A large red emergency button labeled 'STOP'."
Understand "stop button" or "emergency button" or "emergency stop" as the red button.

Instead of pushing the red button:
	if the magnetic crane is powered:
		now the magnetic crane is unpowered;
		increase the score by 2;
		say "You slam your hand down on the emergency stop button. With a loud clunk, the magnetic crane powers down, its electromagnetic field dissipating. [bracket]+2 points[close bracket]";
	otherwise:
		say "The crane is already powered down.";

The magnetic warning sign is scenery in Materials Storage. "WARNING: POWERFUL MAGNETIC FIELD IN OPERATION. NO METAL OBJECTS OR TOOLS BEYOND THIS POINT WHEN CRANE IS ACTIVE. PACEMAKER USERS KEEP CLEAR."
Understand "warning" or "sign" or "magnetic sign" as the magnetic warning sign.

After going to Materials Storage when the magnetic crane is powered:
	if the player carries the crowbar or the player carries the bronze lever or the player carries the steel gear or the player carries the small gear or the player carries the copper gear key:
		say "As you enter the room, the powerful magnetic crane activates! Your metal items are suddenly yanked upward!";
		if the player carries the crowbar:
			now the crowbar is in Materials Storage;
		if the player carries the bronze lever:
			now the bronze lever is in Materials Storage;
		if the player carries the steel gear:
			now the steel gear is in Materials Storage;
		if the player carries the small gear:
			now the small gear is in Materials Storage;
		if the player carries the copper gear key:
			now the copper gear key is in Materials Storage;
		say "You'll need to deactivate the crane to retrieve your items safely.";

[Cooling Chamber and Tock]

The iron cage is scenery in Cooling Chamber. "A sturdy cage built of iron bars, large enough to hold a person-sized automaton. [if Tock is in the iron cage]Inside is a clockwork figure, watching you with glowing crystal eyes[otherwise]It's now empty, the door hanging open[end if]."
Understand "cage" or "bars" or "cell" as the iron cage.

Tock is a person in the iron cage. "A clockwork automaton sits inside the iron cage, its bronze body dented and scratched. It watches you with glowing crystal eyes."
The description is "A humanoid automaton about five feet tall, constructed of bronze gears and copper plating. Its crystal eyes glow with an inner light, suggesting sentience. Through a damaged panel in its chest, you can see that one of its central gears is cracked and barely functioning."
Understand "automaton" or "clockwork automaton" or "clockwork" or "bronze golem" as Tock.

Tock can be hostile, neutral, or friendly. Tock is hostile.

Instead of attacking Tock:
	if Tock is hostile:
		say "The automaton raises its arms defensively and makes threatening grinding noises.";
	otherwise:
		say "The automaton doesn't seem to pose any threat to you now. No need for violence.";

Understand "talk to [someone]" or "speak to [someone]" or "speak with [someone]" or "converse with [someone]" as speaking to. Speaking to is an action applying to one thing.

Check speaking to:
	if the noun is not a person:
		say "You can't have a conversation with that." instead.

Carry out speaking to:
	say "You attempt to start a conversation, but get no meaningful response."

Instead of speaking to Tock:
	if Tock is hostile:
		say "The automaton makes aggressive grinding noises and backs away from the bars.";
	otherwise if Tock is neutral:
		say "'I am Tock, former assistant to the Master Engineer,' the automaton says in a voice like meshing gears. 'I was imprisoned for objecting to his dangerous experiments. The boiler maze reacts to cold water - remember this if you proceed deeper.'";
	otherwise:
		say "'Thank you for repairing me, friend,' Tock says. 'I will remember your kindness. Remember: the boiler maze below reacts to cold water. That is the key to navigating safely.'";

Instead of freeing Tock:
	if Tock is hostile:
		say "The automaton seems dangerous in its current state. It might attack you if freed.";
	otherwise:
		if the cage door is locked:
			say "You need to unlock the cage door first.";
		otherwise:
			remove Tock from play;
			increase the score by 5;
			say "You open the cage door and Tock steps out, its mechanisms whirring. 'Thank you, friend. I shall find my own way from here, but remember: the boiler maze reacts to cold water. That is your key to the next level.' With that, Tock slips away through a maintenance passage. [bracket]+5 points[close bracket]";

Understand "free [something]" or "release [something]" or "let out [something]" as freeing. Freeing is an action applying to one thing.

Check freeing:
	if the noun is not Tock:
		say "You can't free that." instead.

The cage door is part of the iron cage. The cage door can be locked or unlocked. The cage door is locked.
Understand "door" as the cage door.

The mold shelf is scenery in Cooling Chamber. "A shelf containing various molds for casting metal parts. Most are for small components, but one large gear mold stands out."
Understand "shelf" or "molds" as the mold shelf.

The gear mold is scenery in Cooling Chamber. "A heavy iron mold shaped for casting a large gear. It appears to match the shape needed for the gear door in the main forge area."
Understand "mold" or "large mold" or "large gear mold" as the gear mold.

A container can be empty or full. A container is usually full.
The blank mold is a container in Cooling Chamber. The blank mold is full. "A blank gear mold sits on the cooling rack[if the blank mold is empty], ready to be filled with molten metal from the calibrated smelter[end if]."
The description is "A heavy iron mold designed to cast a large gear. [if the blank mold is empty]It's currently empty and ready to use[otherwise]It currently contains an older, unusable casting[end if]."
Understand "blank" or "gear mold" as the blank mold.

Instead of taking the blank mold:
	now the player carries the blank mold;
	say "You take the blank gear mold. It's quite heavy.";

The steel gear is a thing. "A newly-cast steel gear lies cooling on the rack."
The description is "A perfectly formed steel gear, still warm from casting. Its teeth pattern appears to match the locking mechanism of the gear door."
Understand "gear" as the steel gear.

After inserting the blank mold into the massive furnace:
	if the smelter is calibrated and the blank mold is empty:
		remove the blank mold from play;
		now the steel gear is in Main Forge;
		increase the score by 5;
		say "You place the empty mold into the designated spot by the furnace. With the smelter properly calibrated, molten metal flows into the mold in precisely the right amount. After cooling for a moment, a perfectly formed steel gear emerges. [bracket]+5 points[close bracket]";
	otherwise if the smelter is not calibrated:
		say "You place the mold by the furnace, but without the smelter being properly calibrated, nothing happens.";
	otherwise:
		say "The mold needs to be empty before you can use it for a new casting.";

Understand "cast gear" or "make gear" or "forge gear" as casting the gear. Casting the gear is an action applying to nothing.

Check casting the gear:
	if the player is not in Main Forge:
		say "You need to be in the main forge area to cast anything." instead;
	if the player does not carry the blank mold and the blank mold is not in Main Forge:
		say "You need a proper mold to cast a gear." instead;
	if the smelter is not calibrated:
		say "The smelter needs to be calibrated before you can cast anything properly." instead;
	if the blank mold is not empty:
		say "You need an empty mold to cast a new gear." instead.

Carry out casting the gear:
	remove the blank mold from play;
	now the steel gear is in Main Forge;
	increase the score by 5;
	say "With the smelter properly calibrated, you position the empty mold. Molten metal flows into it in precisely the right amount. After cooling for a moment, a perfectly formed steel gear emerges. [bracket]+5 points[close bracket]";

After taking the steel gear:
	increase the score by 3;
	say "You take the steel gear. It feels solid and precisely crafted. [bracket]+3 points[close bracket]";

The philosopher's stone shard is a thing in Materials Storage. "A strange crystalline shard glows with an otherworldly light among the raw materials."
The description is "A fragment of what appears to be the legendary Philosopher's Stone. It glows with an inner light and feels unusually warm to the touch. According to myth, it can transmute base metals into gold and might have other alchemical properties."
Understand "shard" or "stone" or "crystal" or "philosofer's stone" or "stone shard" as the philosopher's stone shard.

After taking the philosopher's stone shard:
	increase the score by 5;
	say "You carefully pocket the glowing shard of the Philosopher's Stone. It pulses warmly in your possession. [bracket]+5 points[close bracket]";

Instead of giving the philosopher's stone shard to Tock:
	now Tock is neutral;
	say "As you show the glowing shard to Tock, its hostile posture relaxes. The automaton's eyes change from red to a calm blue. 'The flux stone. You are not one of the Master's minions then,' it says in a voice like meshing gears.";

Instead of unlocking the cage door with the crowbar:
	now the cage door is unlocked;
	increase the score by 3;
	say "You wedge the crowbar between the bars and apply leverage to the lock. With a satisfying crack, the mechanism breaks and the cage door swings open. [bracket]+3 points[close bracket]";

The steel gear can be repaired or broken. The steel gear is repaired.

Instead of giving the steel gear to Tock:
	if Tock is hostile:
		say "The automaton backs away suspiciously, refusing to accept anything from you.";
	otherwise:
		now Tock is friendly;
		increase the score by 5;
		say "You hand the steel gear to Tock through the bars. The automaton carefully opens its damaged chest panel and replaces its cracked central gear with your perfectly cast one. Its movements immediately become smoother and more precise. 'My gratitude, human. I am Tock, and I am in your debt. Listen carefully: the boiler maze below reacts to cold water. Remember this to survive what lies ahead.' [bracket]+5 points[close bracket]";

Instead of unlocking the gear door with the steel gear:
	now the gear door is unlocked;
	now the gear door is open;
	increase the score by 7;
	say "You carefully place the steel gear into the empty slot on the door's locking mechanism. It fits perfectly! As you turn it, the massive door's complex locking system disengages with a series of satisfying clicks. The gear-shaped door swings open, revealing a passage downward. [bracket]+7 points[close bracket]";

Instead of unlocking the gear door with the copper gear key:
	now the gear door is unlocked; 
	now the gear door is open;
	increase the score by 3;
	say "You insert the copper gear key into the gear door's mechanism. It's not a perfect fit, but with some jiggling, you manage to engage the lock. The gear door creaks open, though the copper gear has been damaged in the process. [bracket]+3 points[close bracket]";
	remove the copper gear key from play;

Instead of going down through the gear door when the gear door is open:
	say "You descend through the gear-shaped door, following a spiral staircase deeper into the tower's heart.";
	end the story finally saying "You've navigated the Gear Forge and continue your descent. Level 3 complete!"

Boiler Tunnel is a room. "This cramped, steaming tunnel connects to the levels below. It's too dark to explore properly from here."

The emergency exit is scenery in Main Forge. "A maintenance access point at the bottom of the smelting pit."
Understand "maintenance access" or "access point" or "ladder" or "maintenance ladder" or "pipe" or "drainage pipe" as the emergency exit.

The emergency exit can be available or unavailable. The emergency exit is unavailable.

Instead of examining the smelting pit when the smelting pit is solidified:
	say "With the molten metal cooled and solidified, you can now see a maintenance ladder leading down through the drainage pipe at the bottom of the pit. It appears to be an alternate route downward.";
	now the emergency exit is available.

Understand "climb down ladder" or "descend ladder" or "climb ladder" or "use ladder" or "down ladder" or "down maintenance ladder" or "down through pit" or "use drainage pipe" or "enter drainage pipe" or "use emergency exit" as descending the pit. Descending the pit is an action applying to nothing.

Check descending the pit:
	if the player is not in Main Forge:
		say "There's no ladder here." instead;
	if the smelting pit is molten:
		say "The smelting pit is filled with dangerous molten metal. You can't climb down through it." instead;
	if the emergency exit is unavailable:
		say "You don't see any way to climb down." instead.

Carry out descending the pit:
	say "You carefully climb down the maintenance ladder through the cooled smelting pit, entering the drainage system that leads to the boiler level below.";
	end the story finally saying "You've found an alternate route through the Gear Forge. Level 3 complete!"
