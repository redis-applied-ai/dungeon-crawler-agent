"Clockwork Descent" by "Andrew Brookins"

Use scoring.
Include Exit Lister by Gavin Lambert.

When play begins:
	now the score is 0;
	now the maximum score is 60;
	now the left hand status line is
		"[the player's surroundings] / [turn count] / [score]";
	now the right hand status line is "";

[Level 1: Aerial Platform - Your Starting Location]

Aerial Platform is a room. "You stand on a wind-swept sky dock atop a flying clockwork airship platform attached to the tower, having just escaped from your prison cell high above. Gears whirr, propellers spin, and steam vents hiss around you. A dirigible is moored to a spire to the east. A cargo crane stands nearby, currently misaligned, blocking a large elevator hatch in the floor. A control panel with an empty slot sits near the crane. A narrow metal gantry extends toward the tower's edge, creaking ominously. A small clockwork automaton named Cogsworth clings to the gantry with a damaged leg that clearly needs repair. You can hear the distant sound of alarm bells from above - you must descend quickly to escape."

The propellers are scenery in Aerial Platform. "Large brass propellers mounted on the platform's sides, spinning steadily to help maintain the airship's stability. Their constant rotation creates a steady thrum that mixes with the wind."
Understand "propeller" or "brass propellers" or "platform propellers" or "spinning propellers" as the propellers.

The platform steam vents are scenery in Aerial Platform. "Small vents in the platform's decking that release excess steam from the tower's systems below. They hiss periodically, creating small clouds of white vapor that are quickly dispersed by the wind."
Understand "steam vents" or "vents" or "platform vents" or "steam openings" or "deck vents" as the platform steam vents.

The dirigible is scenery in Aerial Platform. "A sleek brass and mahogany airship tied to a mooring post. Its balloon is made of treated canvas, taut with lifting gas."
Understand "airship" or "balloon" or "gas bag" or "envelope" as the dirigible.

A device can be aligned or misaligned. A device has a text called alignment description.
The crane is a device in Aerial Platform. The crane is misaligned. The alignment description of the crane is "misaligned".
The description of the crane is "A heavy cargo crane, currently misaligned and blocking the elevator hatch. Its control panel sits nearby with an empty lever slot."
Understand "cargo crane" or "heavy crane" as the crane.
The control panel is scenery in Aerial Platform. "A brass-plated panel with an empty slot shaped for a lever. Above it is a diagram showing gear alignment positions: circle, triangle, square. The slot looks like it would fit the bronze lever perfectly."
Understand "panel" or "brass panel" or "lever slot" or "slot" or "diagram" as the control panel.

Workshop is a room. "An expansive mechanical workshop fills this level of the tower. Churning gears, belt-driven machines, and boiling pipes surround you in every direction. The air is dimmer here, oil-stained and heavy with the scent of machine grease - a stark contrast to the airy platform above. Steam hisses from valves, and the floor vibrates with the motion of a colossal central gear assembly. Conveyor belts carry parts across the room. Doorways lead to a storage area to the east, a control room to the north, and a machine bay to the west. You're one level closer to freedom, but you can still hear the faint echoes of pursuit from above."

The belt-driven machines are scenery in Workshop. "Various mechanical devices powered by an intricate system of leather belts and pulleys. They hum and whir as they process components, their rhythm creating a steady industrial symphony."
Understand "machines" or "belt machines" or "belt-driven machines" or "mechanical devices" or "devices" or "pulleys" or "belts" as the belt-driven machines.

The boiling pipes are scenery in Workshop. "A network of copper and steel pipes carrying superheated steam throughout the workshop. They occasionally emit jets of steam with sharp hissing sounds, and their surfaces are too hot to touch."
Understand "pipes" or "pipe" or "copper pipes" or "steel pipes" or "steam pipes" or "network" as the boiling pipes.

The central gear assembly is scenery in Workshop. "A massive mechanical centerpiece that dominates the workshop floor. Enormous interlocking gears turn with precise timing, their motion creating vibrations that can be felt through the floor. It appears to be the primary power source for the entire workshop level."
Understand "gears" or "gear" or "assembly" or "central assembly" or "massive gears" or "colossal assembly" or "centerpiece" or "power source" as the central gear assembly.

The conveyor belts are scenery in Workshop. "Moving belt systems that transport components and materials between different areas of the workshop. They carry various mechanical parts, tools, and raw materials in an endless cycle."
Understand "belts" or "belt" or "conveyor" or "belt systems" or "moving belts" or "transport belts" as the conveyor belts.

The elevator hatch is a door. It is down of Aerial Platform and up of Workshop. The elevator hatch is closed and locked. Understand "hatch" or "elevator hatch" or "floor hatch" or "lift hatch" or "platform hatch" as the elevator hatch.

The gantry is a device in Aerial Platform. The gantry is scenery.
The gantry can be intact or collapsed.
The gantry is intact.
Understand "metal gantry" or "narrow gantry" or "walkway" or "platform" or "bridge" as the gantry.

A workbench is scenery in Aerial Platform. "A sturdy steel bench marked with tool dents. A toolbox rests upon it."
Understand "bench" or "steel bench" or "work bench" or "table" as the workbench.
A toolbox is a container in Aerial Platform. It is closed and openable. "A battered metal toolbox, likely holding useful tools." Inside the toolbox are a bronze lever and a heavy wrench.
Understand "tool box" or "metal toolbox" or "battered toolbox" or "battered metal toolbox" or "box" as the toolbox.

After opening the toolbox:
	say "Inside the toolbox, you find a bronze lever and a heavy wrench. The lever looks like it would fit into a control mechanism, while the wrench appears suitable for mechanical repairs."

The bronze lever is a thing.
Understand "lever" or "bronze" or "handle" or "control lever" as the bronze lever.
The description is "A heavy bronze lever shaped perfectly to fit the control panel's slot. The control panel is near the crane." The bronze lever is portable.
The heavy wrench is a thing.
Understand "wrench" or "tool" or "spanner" or "repair tool" as the heavy wrench.
The description is "A robust wrench for tightening nuts and bolts. It looks like it could help repair mechanical devices." The heavy wrench is portable.

A supply crate is a container in Aerial Platform. It is closed and openable. "A reinforced wooden crate stamped with the airship's insignia." Inside the supply crate is the brass spyglass.
Understand "crate" or "wooden crate" or "reinforced crate" or "reinforced wooden crate" or "box" or "container" as the supply crate.
The brass spyglass is a thing in the supply crate.
Understand "spyglass" or "glass" or "telescope" or "scope" or "brass telescope" or "optical device" as the brass spyglass.
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

Instead of putting the bronze lever on the control panel: try inserting the bronze lever into the control panel.

Instead of inserting the bronze lever into the control panel when the crane is aligned:
	say "The lever is already in place and the crane hums contentedly.".

Instead of inserting something into the control panel:
	say "That doesn't fit the lever slot.".

Instead of going down when the gantry is intact and the elevator hatch is closed:
	now the gantry is collapsed;
	decrease the score by 10;
	move the player to Workshop;
	end the story saying "The metal groans under your weight! The gantry buckles and you plunge through a trapdoor in the floor! Your hasty escape attempt has backfired, but at least you're one level closer to freedom.".


Cogsworth is a person in Aerial Platform. "A small clockwork automaton tinkerer clings to the gantry, its right leg hinge visibly loose and causing it to limp badly. The automaton looks like it could be repaired with the right tool." Cogsworth can be repaired or broken. Cogsworth is broken.
Understand "automaton" or "tinkerer" or "clockwork automaton" or "small automaton" or "clockwork tinkerer" or "robot" or "mechanical man" or "clockwork" as Cogsworth.
The description of Cogsworth is "A helpful-looking clockwork automaton that appears to be a tinkerer or engineer. Its right leg hinge is visibly damaged and loose, causing it to move with difficulty. A wrench would probably fix that problem easily. Despite its condition, it has the look of someone who might know useful information about this place."

The lift-code is a number that varies. The lift-code is 0.

Instead of speaking to Cogsworth when Cogsworth is broken:
	say "The automaton makes grinding noises and gestures weakly at its damaged leg. It seems to be trying to communicate but can't function properly with its broken hinge. If you could repair it, it might be able to help you."

After giving the heavy wrench to Cogsworth when Cogsworth is broken:
	now Cogsworth is repaired;
	now lift-code is 472;
	now the player is lift-code-aware;
	increase the score by 5;
	say "You hand the wrench to Cogsworth. He tightens his leg hinge with a few clicks, stands upright, and says, 'Thank you! I'm much better now. As a token of gratitude, here's something useful: the code for the workshop lift is 472.' [bracket]+5[close bracket]".


After giving the heavy wrench to Cogsworth when Cogsworth is repaired:
	say "Cogsworth pats his leg gratefully but doesn't need further help.".

A clockwork raven is a kind of animal.
A clockwork raven called the Raven is in Aerial Platform. The description of the Raven is "A metallic raven with glowing red eyes circles above, watching you."
Understand "raven" or "bird" or "metallic bird" or "clockwork bird" or "mechanical raven" as the Raven.

The Steam Valve is a device.
The Steam Valve is in Aerial Platform.
The Steam Valve can be switched on or switched off.
The Steam Valve is switched off.
The description of the Steam Valve is "A brass valve controlling a steam vent. The metallic raven seems to be keeping its distance from the vent area."
Understand "valve" or "brass valve" or "steam control" or "vent control" as the Steam Valve.

A steam vent is scenery.
The steam vent is in Aerial Platform.
The steam vent can be active or inactive.
The steam vent is inactive.
The description of the steam vent is "A vent that can release a burst of steam when powered."
Understand "vent" or "steam opening" or "nozzle" or "steam nozzle" as the steam vent.

Instead of switching on the Steam Valve:
	now the steam vent is active;
	say "Steam hisses from the vent!".


After switching on the Steam Valve when the steam vent is active and the Raven is in the location:
	remove the Raven from play;
	increase the score by 5;
	now a small gear is in the location;
	say "The raven screeches and flies away under the blast of steam, dropping a small brass gear. [bracket]+5[close bracket]".

A small gear is a thing. The description is "A tiny brass gear once held by the raven." The small gear is portable.
Understand "gear" or "tiny gear" or "brass gear" or "small brass gear" or "cog" as the small gear.

After taking the small gear:
	increase the score by 1;
	say "You pick up the small gear. [bracket]+1[close bracket]".

Instead of going down when the elevator hatch is open and the elevator hatch is unlocked:
	move the player to Workshop;
	say "You descend into the workshop, gears clanking behind you. One level closer to freedom.".

Instead of entering the elevator hatch when the elevator hatch is open: try going down.
	
[Level 2: Workshop - Changed from single room to multiple rooms]

The Storage Area is east of Workshop. "This cluttered space houses spare parts, tools, and maintenance supplies. Metal shelves line the walls, packed with components and engineering materials. A heavy tool chest sits against the far wall. [if the steam pipe is leaking]The Chief Engineer, Marigold, is here suffering from the dangerous steam leak.[otherwise]The Chief Engineer, Marigold, is here working peacefully now that the steam problem is resolved.[end if] The main workshop lies to the west."

The metal shelves are scenery in Storage Area. "Sturdy steel shelving units line the walls, packed with an assortment of mechanical components, spare parts, and engineering materials. Every shelf appears to be completely full."
Understand "shelves" or "shelf" or "steel shelves" or "shelving" or "steel shelving" or "shelving units" as the metal shelves.

The components are scenery in Storage Area. "Various mechanical parts, gears, springs, bolts, and other components needed for maintaining the workshop's machinery. They're organized in bins and containers throughout the storage area."
Understand "parts" or "spare parts" or "mechanical parts" or "gears" or "springs" or "bolts" or "bins" or "containers" as the components.

The engineering materials are scenery in Storage Area. "Raw materials used in the workshop's operations: sheets of metal, lengths of copper pipe, brass fittings, and various other industrial supplies."
Understand "materials" or "raw materials" or "metal" or "sheets" or "metal sheets" or "copper pipe" or "brass fittings" or "fittings" or "supplies" or "industrial supplies" as the engineering materials.

The Control Room is north of Workshop. "The workshop's nerve center is filled with monitoring equipment and control panels. Pressure gauges, brass dials, and lever arrays cover the walls. A large service elevator platform occupies the center of the room, its control panel gleaming with polished brass fixtures. The main workshop is to the south."

The pressure gauges are scenery in Control Room. "Various gauges showing steam pressure, temperature, and flow rates throughout the workshop systems. Most readings appear to be within normal operational parameters."
Understand "gauges" or "gauge" or "pressure gauge" or "steam gauge" or "temperature gauge" or "monitoring equipment" as the pressure gauges.

The brass dials are scenery in Control Room. "Polished brass control dials for fine-tuning the workshop's mechanical systems. They gleam in the light from the overhead fixtures."
Understand "dials" or "dial" or "brass dial" or "control dial" or "brass dials" or "polished dials" as the brass dials.

The lever arrays are scenery in Control Room. "Rows of levers for controlling various workshop functions, though most appear to be for routine operations. They're arranged in neat, methodical rows along the wall panels."
Understand "levers" or "lever" or "arrays" or "lever array" or "control levers" or "wall levers" as the lever arrays.

The Machine Bay is west of Workshop. "The constant din of operating machinery fills this high-ceilinged chamber. Massive gear assemblies turn overhead, while automated belt mechanisms transport components across the room. Steam regularly vents from pipes along the walls. A small floor hatch bolted to the floor appears to be an emergency exit. The main workshop lies to the east."

The massive gear assemblies are scenery in Machine Bay. "Enormous mechanical gear systems mounted on the ceiling, their interlocking teeth meshing with precise timing. They turn with tremendous force, providing power distribution throughout the machine bay."
Understand "gears" or "gear" or "assemblies" or "assembly" or "massive gears" or "gear systems" or "mechanical gears" or "overhead gears" or "ceiling gears" as the massive gear assemblies.

The automated belt mechanisms are scenery in Machine Bay. "Complex conveyor and belt systems that automatically transport components across the room. They operate with mechanical precision, moving parts from one station to another without human intervention."
Understand "belts" or "belt" or "mechanisms" or "belt mechanisms" or "automated belts" or "conveyor systems" or "transport systems" as the automated belt mechanisms.

The wall steam vents are scenery in Machine Bay. "Regular openings in the wall pipes that release excess steam pressure. They emit periodic jets of hot steam with sharp hissing sounds, creating a hazardous environment near the walls."
Understand "vents" or "vent" or "steam vents" or "wall vents" or "steam openings" or "pressure vents" as the wall steam vents.

[Workshop machinery and objects redistributed across rooms]

The service elevator is a device in the Control Room.
The service elevator can be locked or unlocked. The service elevator is locked.
Understand "lift" or "platform" or "elevator" or "service lift" or "workshop lift" or "industrial elevator" or "machinery lift" as the service elevator.
The description of the service elevator is "A large industrial elevator platform designed to transport heavy machinery between levels. Its control panel has a numeric keypad for entering a code."

The elevator control panel is scenery in the Control Room. "A control panel with a numeric keypad and a large button marked 'DESCEND'. The keypad appears to require a 3-digit code."
Understand "control panel" or "panel" or "keypad" or "numeric keypad" or "elevator panel" or "number pad" or "controls" as the elevator control panel.

The elevator button is part of the elevator control panel.
Understand "button" or "descend button" or "large button" or "elevator button" or "control button" as the elevator button.

A person can be lift-code-aware or lift-code-unaware. A person is usually lift-code-unaware.

Instead of pushing the elevator button:
	if the service elevator is locked:
		say "The button refuses to activate. The control panel flashes red - it seems to require a code.";
	otherwise:
		say "As you press the button, the elevator platform begins to descend with a mechanical groan. It carries you past the forge level to a hidden exit at the tower's base. You emerge into daylight, finally free from both your prison and the clockwork labyrinth. Behind you, the tower's alarms continue to sound, but you are beyond their reach now.";
		end the story finally saying "You have successfully escaped! Your ingenuity and determination have carried you from the prison cell at the tower's peak down to freedom at its base. The clockwork tower's mechanical challenges could not hold you."

Understand "enter [text] on keypad" or "enter [text]" or "type [text]" or "input [text]" or "set dial to [text]" or "punch in [text]" or "key in [text]" or "press [text]" as entering code.
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
Understand "pipe" or "pipes" or "copper pipe" or "steam pipe" or "broken pipe" or "cracked pipe" as the steam pipe.

The steam cloud is a thing. "Scalding steam fills parts of the room, making it dangerous to move around freely."
The description is "A billowing cloud of hot steam that could cause serious burns if you walk through it."
Understand "steam" or "cloud" or "hot steam" or "scalding steam" or "vapor" as the steam cloud.

A spare gasket is a thing in the Storage Area. "A rubber gasket sits on a nearby shelf, appearing to be the right size for pipe repairs."
The description is "A thick rubber gasket designed to seal high-pressure pipe connections."
Understand "gasket" or "rubber gasket" or "seal" or "pipe seal" or "rubber seal" as the spare gasket.

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

Instead of putting the spare gasket on the steam pipe: try fixing the steam pipe.

Understand "use [something] on [something]" or "apply [something] to [something]" or "put [something] on [something]" or "attach [something] to [something]" or "install [something] on [something]" as putting it on.

Instead of putting the spare gasket on the steam pipe: try fixing the steam pipe.

Understand "patch [something] with [something]" or "seal [something] with [something]" or "fix [something] with [something]" or "repair [something] with [something]" or "mend [something] with [something]" or "plug [something] with [something]" as repairing it with.
Repairing it with is an action applying to two things.

Check repairing it with:
	if the noun is not the steam pipe:
		say "That doesn't need repairing with anything." instead;
	if the second noun is the heavy wrench:
		say "A wrench won't help seal a pipe leak. You need something to plug the crack - perhaps a gasket or seal of some kind." instead;
	if the second noun is not the spare gasket:
		say "That won't help repair the pipe." instead.

Carry out repairing it with:
	try fixing the steam pipe.


Understand "fix [something]" or "repair [something]" or "seal [something]" or "patch [something]" or "mend [something]" as fixing.
Fixing is an action applying to one thing.

Check fixing:
	if the noun is not the steam pipe:
		say "That doesn't need fixing." instead.

Carry out fixing:
	say "You need something to fix this with.".

The copper gear key is a thing in the Machine Bay. "A distinctive copper gear with odd teeth lies partially hidden beneath a belt mechanism."
The description is "An unusual copper gear with teeth arranged in an intricate pattern. It appears to be designed as a key rather than a functional gear."
Understand "copper gear" or "gear key" or "key" or "copper key" or "unusual gear" or "distinctive gear" as the copper gear key.

Instead of taking the copper gear key:
	now the player carries the copper gear key;
	increase the score by 5;
	say "You take the copper gear key. It feels like it might fit into a specialized lock somewhere. [bracket]+5 points[close bracket]".

A tool chest is a container in the Storage Area. It is closed and openable. "A heavy tool chest sits against the far wall."
The description is "A large, industrial-strength chest for storing workshop tools."
Understand "chest" or "heavy chest" or "tool box" or "industrial chest" or "storage chest" as the tool chest.

Marigold is a woman in the Storage Area. "A woman in grease-stained overalls crouches [if the steam pipe is leaking]behind the tool chest, coughing violently from the scalding steam filling the area. She looks like she's in distress and would be very grateful if someone could stop the steam leak[otherwise]by the tool chest, examining some components with a relieved expression[end if]."
The description is "A tough-looking woman with practical overalls and calloused hands. A patch on her jacket identifies her as 'Marigold, Chief Engineer'. [if the steam pipe is leaking]She's clearly suffering from the steam and keeps glancing toward the Workshop where the broken pipe is located. She looks like someone who would reward whoever fixes that dangerous steam leak.[otherwise]She seems much more comfortable now that the steam problem has been resolved. As the Chief Engineer, she probably knows useful information about this facility.[end if]".
Understand "woman" or "engineer" or "chief engineer" or "worker" or "mechanic" as Marigold.

After fixing the steam pipe when Marigold is in the Storage Area and the steam pipe is in Workshop:
	say "Word seems to travel fast. Marigold stands up straight in the Storage Area, her coughing subsiding. 'Thank you for that! I was afraid the whole level would fill with steam. That pipe's been troublesome for weeks. I owe you one - ask me for help if you need anything.'";
	now Marigold carries the pocket watch.

The pocket watch is a thing.
The description is "A polished brass pocket watch with intricate clockwork visible through a glass panel. Looking carefully, you notice the numbers '472' engraved inside the cover."
Understand "watch" or "brass watch" or "pocket watch" or "timepiece" or "clock" as the pocket watch.

After examining the pocket watch:
	now the player is lift-code-aware;
	say "You notice the numbers '472' delicately engraved inside the cover. That looks like it could be important."

Instead of speaking to Marigold when the steam pipe is leaking:
	say "Marigold coughs violently and can barely speak through the scalding steam. 'Can't... *cough*... work like this!' she gasps, pointing toward the Workshop. 'That steam pipe... *cough*... needs fixing badly! Someone with the right supplies could patch it up!' She looks at you hopefully."

Instead of asking Marigold about "help" when Marigold carries the pocket watch:
	now the player carries the pocket watch;
	increase the score by 5;
	say "'Here, take this as thanks for your help,' Marigold says, handing you a pocket watch. 'And a bit of advice - in the forge below, mind the pattern: short-long-long-short. It's the sequence to calibrate the smelter.' [bracket]+5 points[close bracket]".

Instead of asking Marigold about "watch": try asking Marigold about "help".
Instead of asking Marigold about "reward": try asking Marigold about "help".
Instead of asking Marigold about "thanks": try asking Marigold about "help".

A gearling is a kind of animal. "A fist-sized mechanical creature scuttles across the floor, its gear-shaped legs clicking on the metal." Understand "gear spider" or "mechanical pest" or "gear creature" or "creature" or "spider" or "mechanical spider" or "pest" or "bug" or "mechanical bug" as a gearling.
The description of a gearling is "A small mechanical pest resembling a spider made of gears and springs. Its tiny metal mandibles look sharp enough to cut through wire."

A gearling called a skittering gearling is in Workshop.
A gearling called a clicking gearling is in the Machine Bay.
A gearling called a whirring gearling is in the Machine Bay.

The machine oil is a thing in the tool chest. "A can of machine oil sits on a shelf."
The description is "A metal can filled with slick lubricating oil for machinery."
Understand "oil" or "can" or "oil can" or "lubricant" or "machine lubricant" or "grease" as the machine oil.

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

Instead of throwing the machine oil at a gearling: try pouring the machine oil on the noun.

Understand "pour [something] on [something]" as pouring it on. Pouring it on is an action applying to two things.

Check pouring it on:
	if the noun is not the machine oil:
		say "You can't pour that." instead.

Carry out pouring it on:
	say "You pour [the noun] on [the second noun], but nothing useful happens.".

The scrap metal is a thing. "Some scrap metal pieces lie on the floor."
The description is "Various small metal pieces, gears, and springs from the defeated gearlings."
Understand "scrap" or "metal" or "pieces" or "metal pieces" or "scraps" or "debris" or "parts" as the scrap metal.

Instead of taking the scrap metal:
	now the player carries the scrap metal;
	increase the score by 1;
	say "You collect the scrap metal. It might be useful for something. [bracket]+1 point[close bracket]".

The emergency hatch is a door. It is down from the Machine Bay. The emergency hatch is locked.
Understand "hatch" or "floor hatch" or "emergency exit" or "bolted hatch" or "exit" or "door" or "metal hatch" as the emergency hatch.
The description is "A small metal hatch bolted to the floor, likely an emergency exit. It appears to be locked from this side."

The crowbar is a thing in Workshop. "A sturdy crowbar leans against one of the workbenches."
The description is "A solid steel crowbar, perfect for prying things open."
Understand "bar" or "pry bar" or "crowbar" or "steel bar" or "lever" or "tool" as the crowbar.

Instead of taking the crowbar:
	now the player carries the crowbar;
	increase the score by 1;
	say "You take the crowbar. [bracket]+1 point[close bracket]".

Instead of opening the emergency hatch when the emergency hatch is locked:
	say "The emergency hatch is bolted shut from this side. You'll need some kind of prying tool to force it open."

Instead of opening the emergency hatch when the emergency hatch is unlocked:
	say "The emergency hatch is already open. You can go down through it to escape."

Instead of unlocking the emergency hatch with the crowbar:
	now the emergency hatch is unlocked;
	increase the score by 3;
	say "You wedge the crowbar into the seam of the hatch and heave with all your strength. With a screech of metal, the bolts give way and the hatch swings open. [bracket]+3 points[close bracket]".


Instead of going down through the emergency hatch when the emergency hatch is unlocked:
	say "You carefully lower yourself through the hatch and begin descending the narrow spiral staircase. It leads to a hidden emergency exit at the tower's base. You emerge into daylight, finally free from both your prison and the clockwork labyrinth. Behind you, the tower's alarms continue to sound, but you are beyond their reach now.";
	end the story finally saying "You have successfully escaped! Your ingenuity and determination have carried you from the prison cell at the tower's peak down to freedom at its base. The clockwork tower's mechanical challenges could not hold you."

[Level 3: Gear Forge]

Main Forge is a room. "You've entered the fiery heart of the tower's manufacturing operations at its base level. This vast chamber glows with intense orange light from molten metal baths and a massive furnace dominating the center. The heat is oppressive, making sweat bead on your skin instantly. Enormous gears line the walls, awaiting installation elsewhere in the tower, while conveyor belts transport raw materials to various workstations. The continuous clanking of an automated hammer punctuates the roar of the furnace. Steam rises through grates in the floor from the foundational systems below. Doorways lead to a control room to the north, a materials storage area to the east, and a cooling chamber to the west. Freedom lies just beyond these chambers - you can almost taste it."

The molten metal baths are scenery in Main Forge. "Glowing pools of liquid metal that cast dancing orange light throughout the chamber. They bubble and hiss with intense heat, too dangerous to approach without proper protection."
Understand "baths" or "metal baths" or "molten baths" or "pools" or "liquid metal" or "glowing pools" as the molten metal baths.

The enormous gears are scenery in Main Forge. "Massive mechanical gears of various sizes line the walls, awaiting installation elsewhere in the tower. They're perfectly crafted, their teeth precisely machined and their surfaces gleaming despite the forge's heat."
Understand "gears" or "gear" or "enormous gears" or "massive gears" or "wall gears" or "mechanical gears" as the enormous gears.

The forge conveyor belts are scenery in Main Forge. "Heavy-duty conveyor systems that transport raw materials to various workstations throughout the forge. They move continuously, carrying ingots, tools, and components with mechanical precision."
Understand "conveyor belts" or "belts" or "conveyor" or "transport belts" or "conveyor systems" as the forge conveyor belts.

The workstations are scenery in Main Forge. "Various specialized work areas throughout the forge, each equipped with different tools and apparatus for specific metalworking tasks. They're arranged for efficient workflow around the central furnace."
Understand "workstation" or "work areas" or "work stations" or "stations" or "apparatus" as the workstations.

The floor grates are scenery in Main Forge. "Metal grating in the floor that allows steam from the foundational systems below to rise into the main forge area. They glow with heat from the systems beneath."
Understand "grates" or "grate" or "floor grates" or "metal grating" or "grating" or "floor grating" as the floor grates.

Forge Control Room is north of Main Forge. "This room overlooks the main forge floor through a large heat-resistant glass window. The walls are lined with gauges, dials, and levers controlling various aspects of the forging process. A large smelter control panel dominates the center of the room, featuring four sequential levers arranged in a row. A chalkboard hangs on the wall near the panel. The intense heat of the main forge is somewhat mitigated here, though the air remains uncomfortably warm. The main forge area lies to the south."

The heat-resistant glass window is scenery in Forge Control Room. "A large window made of specially treated glass that can withstand the intense heat of the main forge. Through it, you can see the glowing furnace and the busy activity of the forge floor below."
Understand "window" or "glass window" or "large window" or "heat-resistant window" or "glass" as the heat-resistant glass window.

The forge gauges are scenery in Forge Control Room. "Various monitoring instruments displaying temperature, pressure, and other critical measurements for the forging process. They provide real-time data about the forge's operational status."
Understand "gauges" or "gauge" or "monitoring instruments" or "instruments" or "temperature gauges" or "pressure gauges" as the forge gauges.

The forge dials are scenery in Forge Control Room. "Precision control dials for adjusting various aspects of the forging process. They allow fine-tuning of temperature, pressure, and timing for different metalworking operations."
Understand "dials" or "dial" or "control dials" or "precision dials" or "adjustment dials" as the forge dials.

The control levers are scenery in Forge Control Room. "Wall-mounted levers for controlling various forge functions. They're separate from the smelter control panel and handle routine operational tasks."
Understand "levers" or "lever" or "wall levers" or "operational levers" or "forge levers" as the control levers.

Materials Storage is east of Main Forge. "Raw materials for the forge's operation are stored in this high-ceilinged chamber. Bins of metal ingots, crates of coal, and barrels of various industrial chemicals line the walls. A massive magnetic crane system runs along ceiling tracks, designed to move heavy materials to and from the main forge. A control box for the crane hangs from a chain nearby. Warning signs about magnetic hazards are posted prominently. The main forge lies to the west."

The bins of metal ingots are scenery in Materials Storage. "Large storage bins containing metal ingots of various alloys - steel, brass, copper, and iron. They're sorted by type and stacked efficiently for easy access by the magnetic crane."
Understand "bins" or "ingots" or "metal ingots" or "metal bins" or "storage bins" or "steel ingots" or "brass ingots" or "copper ingots" or "iron ingots" as the bins of metal ingots.

The crates of coal are scenery in Materials Storage. "Wooden crates filled with coal for fueling the forge's furnaces. The coal is of high quality, selected specifically for metalworking applications."
Understand "crates" or "coal" or "crates of coal" or "coal crates" or "wooden crates" or "fuel" as the crates of coal.

The barrels of chemicals are scenery in Materials Storage. "Industrial barrels containing various chemicals used in the forging process - flux compounds, cleaning agents, and other specialized materials. Warning labels indicate their hazardous nature."
Understand "barrels" or "chemicals" or "chemical barrels" or "industrial barrels" or "flux compounds" or "cleaning agents" or "hazardous materials" as the barrels of chemicals.

The ceiling tracks are scenery in Materials Storage. "Heavy-duty rail systems mounted on the ceiling that allow the magnetic crane to move throughout the storage area. They're built to support tremendous weight."
Understand "tracks" or "ceiling tracks" or "rail systems" or "rails" or "crane tracks" or "overhead tracks" as the ceiling tracks.

Cooling Chamber is west of Main Forge. "This room serves as both a cooling area for newly forged items and a holding cell. The temperature here is noticeably lower than the main forge, with large fans circulating air. Racks of cooling molds line one wall, while a series of water troughs stand ready for quenching hot metal. In the corner, behind sturdy iron bars, is what appears to be a large cage. The main forge area is to the east."

The large fans are scenery in Cooling Chamber. "Industrial-sized fans mounted on the walls and ceiling, designed to circulate air and help cool newly forged items. They turn steadily, creating a much more comfortable environment than the main forge."
Understand "fans" or "fan" or "large fans" or "industrial fans" or "cooling fans" or "air circulation" as the large fans.

The water troughs are scenery in Cooling Chamber. "A series of long, rectangular water containers positioned for quenching hot metal. They're filled with clean water and positioned strategically for easy access from the main forge."
Understand "troughs" or "trough" or "water troughs" or "water containers" or "quenching troughs" or "containers" or "water" as the water troughs.

The cooling racks are scenery in Cooling Chamber. "Metal racks designed to hold cooling molds and newly forged items. They're arranged to provide optimal air circulation for the cooling process."
Understand "racks" or "rack" or "cooling racks" or "metal racks" or "mold racks" as the cooling racks.

[Main Forge Scenery and Objects]

The massive furnace is scenery in Main Forge. "A roaring industrial furnace, its open mouth glowing white-hot with molten metal inside. The heat radiating from it is almost unbearable. A series of molds sit nearby, and a heavy gear-shaped door is set into the floor near the base of the furnace."
Understand "furnace" or "industrial furnace" or "forge" or "fire" or "kiln" or "oven" as the massive furnace.

The automated hammer is scenery in Main Forge. "A gigantic steam-powered hammer that rhythmically pounds red-hot metal. Its continuous clanking follows a distinct pattern: one short strike, followed by two long strikes, then another short strike."
Understand "hammer" or "automated hammer" or "steam hammer" or "mechanical hammer" or "giant hammer" or "power hammer" as the automated hammer.

After examining the automated hammer:
	if the player is smelter-pattern-unaware:
		now the player is smelter-pattern-aware;
		say "You notice the hammer strikes follow a distinct pattern: short-long-long-short. This seems deliberate rather than random.";

The gear door is a door. It is down from Main Forge. The gear door is scenery. The gear door is closed and locked.
Understand "gear-shaped door" or "floor door" or "hatch" or "gear hatch" or "circular hatch" or "gear door" or "floor hatch" or "round door" as the gear door.
The description is "A circular hatch set into the floor, designed like an enormous gear. It appears to be a doorway down to lower levels. The locking mechanism has a gear-shaped slot where a key component seems to be missing."

The smelting pit is scenery in Main Forge. "A deep pit filled with bubbling molten metal. Excess material drains through a large pipe at the bottom, presumably to be recycled. It's far too hot to approach without protection."
Understand "pit" or "smelting pit" or "molten pit" or "metal pit" or "forge pit" or "crucible" as the smelting pit.

The smelting pit can be heated or cooled. The smelting pit is heated.

The water valve is a device in Main Forge. The water valve can be switched on or switched off. The water valve is switched off.
Understand "valve" or "water valve" or "emergency valve" or "cooling valve" or "flood valve" as the water valve.
The description is "An emergency water valve designed to flood the smelting pit with cooling water in case of an emergency."

Instead of switching on the water valve:
	if the smelting pit is heated:
		now the smelting pit is cooled;
		now the water valve is switched on;
		say "You turn the valve. Water gushes into the smelting pit, causing clouds of steam to billow up as the molten metal rapidly cools and solidifies.";
	otherwise:
		say "The water valve is already active and the smelting pit has been cooled.";

Instead of opening the water valve: try switching on the water valve.

[Steam Golem]

The Steam Golem is an animal in Main Forge. "A monstrous construct of iron and hydraulics lumbers around the forge, superheated steam escaping from its joints. Its metal body glows red-hot."
The description is "A fearsome creation of metal and steam, standing about eight feet tall. Its body is constructed of iron plates riveted together, with glowing red-hot elements visible through the gaps. Steam continuously vents from its joints as it moves with surprising speed and agility for something so massive."
Understand "golem" or "construct" or "automaton" or "robot" or "machine" or "iron golem" or "steam construct" or "metal construct" as the Steam Golem.

The Steam Golem can be operational or neutralized. The Steam Golem is operational.

Instead of attacking the Steam Golem:
	say "Your attack has no effect on the super-heated metal body of the golem. It turns toward you menacingly, steam hissing from its joints."

After switching on the water valve when the Steam Golem is in the location and the Steam Golem is operational:
	now the Steam Golem is neutralized;
	increase the score by 7;
	say "As water floods the smelting pit, some of it splashes onto the Steam Golem. With a hissing screech, the creature seizes up as its heated components rapidly cool and contract. It freezes in place, becoming immobile. [bracket]+7 points[close bracket]";

[Forge Control Room Items]

The smelter control panel is scenery in Forge Control Room. "A complex control station with four sequential levers arranged in a row. Each lever can be pulled for either a short or long duration to calibrate the smelting process."
Understand "control panel" or "panel" or "smelter panel" or "control station" or "controls" as the smelter control panel.

The four levers are part of the smelter control panel. Understand "levers" or "sequential levers" or "row of levers" or "four levers" or "control levers" or "lever row" as the four levers.

The chalkboard is scenery in Forge Control Room. "A slate board covered with chalk dust. Someone has drawn four symbols that look like Morse code: a dot, followed by two dashes, and then another dot (· — — ·)."
Understand "chalk board" or "board" or "slate" or "chalkboard" or "blackboard" or "slate board" or "symbols" or "pattern" as the chalkboard.

After examining the chalkboard:
	if the player is smelter-pattern-unaware:
		now the player is smelter-pattern-aware;
		say "The pattern on the board - dot, dash, dash, dot - reminds you of a sequence: short-long-long-short.";

A person can be smelter-pattern-aware or smelter-pattern-unaware. A person is usually smelter-pattern-unaware.

A device can be calibrated or uncalibrated. A device has a text called calibration description.
The smelter is a device in Forge Control Room. The smelter is uncalibrated. The calibration description of the smelter is "uncalibrated".

Understand "calibrate smelter" or "set smelter" or "use levers" or "pull levers in pattern" or "pull levers short long long short" or "operate smelter" or "activate smelter" or "adjust smelter" as calibrating the smelter.
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

Understand "pull [text]" or "operate [text]" or "use [text]" or "activate [text]" or "set [text]" as pulling levers with pattern. Pulling levers with pattern is an action applying to one topic.

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
Understand "crane" or "magnetic" or "magnetic crane" or "industrial crane" or "electromagnet" or "magnet" as the magnetic crane.
The description is "A massive industrial crane with a powerful electromagnet at its end, designed to move heavy metal objects throughout the forge. It's currently [if the magnetic crane is powered]powered on, its electromagnetic field active[otherwise]powered off and safe to approach[end if]."

The crane control box is scenery in Materials Storage. "A control box hanging from a chain with buttons to operate the overhead magnetic crane. There's a large red emergency stop button prominently displayed."
Understand "control box" or "box" or "controls" or "crane controls" or "control panel" as the crane control box.

The red button is part of the crane control box. "A large red emergency button labeled 'STOP'."
Understand "stop button" or "emergency button" or "emergency stop" or "red button" or "button" or "stop" as the red button.

Instead of pushing the red button:
	if the magnetic crane is powered:
		now the magnetic crane is unpowered;
		increase the score by 2;
		say "You slam your hand down on the emergency stop button. With a loud clunk, the magnetic crane powers down, its electromagnetic field dissipating. [bracket]+2 points[close bracket]";
	otherwise:
		say "The crane is already powered down.";


The magnetic warning sign is scenery in Materials Storage. "WARNING: POWERFUL MAGNETIC FIELD IN OPERATION. NO METAL OBJECTS OR TOOLS BEYOND THIS POINT WHEN CRANE IS ACTIVE. PACEMAKER USERS KEEP CLEAR."
Understand "warning" or "sign" or "magnetic sign" or "warning sign" or "danger sign" or "notice" as the magnetic warning sign.

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
Understand "cage" or "bars" or "cell" or "iron cage" or "iron bars" or "prison" as the iron cage.

Tock is a person in the iron cage. "A clockwork automaton sits inside the iron cage, its bronze body dented and scratched. It watches you with glowing crystal eyes."
The description is "A humanoid automaton about five feet tall, constructed of bronze gears and copper plating. Its crystal eyes glow with an inner light, suggesting sentience. Through a damaged panel in its chest, you can see that one of its central gears is cracked and barely functioning."
Understand "automaton" or "clockwork automaton" or "clockwork" or "bronze golem" or "robot" or "mechanical man" or "prisoner" as Tock.

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
Understand "door" or "cage door" or "iron door" or "cell door" or "bars" as the cage door.

The mold shelf is scenery in Cooling Chamber. "A shelf containing various molds for casting metal parts. Most are for small components, but one large gear mold stands out."
Understand "shelf" or "molds" or "mold shelf" or "casting shelf" or "rack" as the mold shelf.

The gear mold is scenery in Cooling Chamber. "A heavy iron mold shaped for casting a large gear. It appears to match the shape needed for the gear door in the main forge area."
Understand "mold" or "large mold" or "large gear mold" or "gear mold" or "iron mold" or "casting mold" as the gear mold.

A container can be empty or full. A container is usually full.
The blank mold is a container in Cooling Chamber. The blank mold is full. "A blank gear mold sits on the cooling rack[if the blank mold is empty], ready to be filled with molten metal from the calibrated smelter[end if]."
The description is "A heavy iron mold designed to cast a large gear. [if the blank mold is empty]It's currently empty and ready to use[otherwise]It currently contains an older, unusable casting[end if]."
Understand "blank" or "gear mold" or "blank mold" or "mold" or "casting mold" or "empty mold" as the blank mold.

Instead of taking the blank mold:
	now the player carries the blank mold;
	say "You take the blank gear mold. It's quite heavy.";

The steel gear is a thing. "A newly-cast steel gear lies cooling on the rack."
The description is "A perfectly formed steel gear, still warm from casting. Its teeth pattern appears to match the locking mechanism of the gear door."
Understand "gear" or "steel gear" or "cast gear" or "metal gear" or "new gear" or "forged gear" as the steel gear.

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

Instead of putting the blank mold on the massive furnace: try inserting the blank mold into the massive furnace.

Understand "cast gear" or "make gear" or "forge gear" or "create gear" or "form gear" or "mold gear" as casting the gear. Casting the gear is an action applying to nothing.

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
Understand "shard" or "stone" or "crystal" or "philosofer's stone" or "stone shard" or "crystalline shard" or "glowing shard" or "flux stone" as the philosopher's stone shard.

After taking the philosopher's stone shard:
	increase the score by 5;
	say "You carefully pocket the glowing shard of the Philosopher's Stone. It pulses warmly in your possession. [bracket]+5 points[close bracket]";

Instead of giving the philosopher's stone shard to Tock:
	now Tock is neutral;
	say "As you show the glowing shard to Tock, its hostile posture relaxes. The automaton's eyes change from red to a calm blue. 'The flux stone. You are not one of the Master's minions then,' it says in a voice like meshing gears.";

Instead of showing the philosopher's stone shard to Tock: try giving the philosopher's stone shard to Tock.

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
	say "You descend through the gear-shaped door, following a spiral staircase that leads to a hidden exit at the tower's base. After what feels like an eternity of climbing down, you emerge into daylight and fresh air, finally free from both your prison and the clockwork labyrinth. Behind you, the tower's alarms continue to sound, but you are beyond their reach now.";
	end the story finally saying "You have successfully escaped! Your ingenuity and determination have carried you from the prison cell at the tower's peak down to freedom at its base. The clockwork tower's mechanical challenges could not hold you."

The emergency exit is scenery in Main Forge. "A maintenance access point at the bottom of the smelting pit."
Understand "maintenance access" or "access point" or "ladder" or "maintenance ladder" or "pipe" or "drainage pipe" as the emergency exit.

The emergency exit can be available or unavailable. The emergency exit is unavailable.

Instead of examining the smelting pit when the smelting pit is cooled:
	say "With the molten metal cooled and solidified, you can now see a maintenance ladder leading down through the drainage pipe at the bottom of the pit. It appears to be an alternate route downward.";
	now the emergency exit is available.

Understand "climb down ladder" or "descend ladder" or "climb ladder" or "use ladder" or "down ladder" or "down maintenance ladder" or "down through pit" or "use drainage pipe" or "enter drainage pipe" or "use emergency exit" as descending the pit. Descending the pit is an action applying to nothing.

Check descending the pit:
	if the player is not in Main Forge:
		say "There's no ladder here." instead;
	if the smelting pit is heated:
		say "The smelting pit is filled with dangerous molten metal. You can't climb down through it." instead;
	if the emergency exit is unavailable:
		say "You don't see any way to climb down." instead.

Carry out descending the pit:
	say "You carefully climb down the maintenance ladder through the cooled smelting pit. The drainage pipe leads to a hidden emergency exit. After crawling through the narrow tunnel, you emerge into daylight at the tower's base, finally free from both your prison and the clockwork labyrinth. Behind you, the tower's alarms continue to sound, but you are beyond their reach now.";
	end the story finally saying "You have successfully escaped! Your ingenuity and determination have carried you from the prison cell at the tower's peak down to freedom at its base. The clockwork tower's mechanical challenges could not hold you."
