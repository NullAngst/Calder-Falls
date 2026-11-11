// ============================================================
// Chapter 1. Prologue: Dispatch
// The call, the drive, the briefing, the tape. Teaches the verbs:
// reading, choosing, the police band, the AM dial, the camera, the
// notebook, Nerve, smoking, the hint button.
// ============================================================

=== prologue ===
# chapter:1:Dispatch
# theme:midnight
# music:calder_falls
# time:14:52
# item:radio
# item:notebook
# item:pistol
# item:keys
# hint:Read, then pick what he does with the buttons below. The radio tab on the right has a police band knob too.
Sunday, the twelfth of October, 1986. Route 9, northbound, somewhere past the last exit with a gas station on it.

The cruiser smells like burnt coffee and the pine tree hanging from the mirror, which stopped smelling like pine in August. The wipers go every six seconds. You don't need them. You like the sound.

You are Detective Sergeant Cal Brennick, state police, Major Crimes, and you are three hours from home on a Sunday because you wanted to be.

The radio under the dash has been quiet for forty minutes. Then it isn't.

"Troop F to any Major Crimes unit north of Hollis. Respond Calder Falls, Ostrander County. Twenty-two Cobb Road. County is requesting. Multiple deceased, domestic. Repeat, multiple deceased."

You knew it would be Calder Falls before she said the name. You have known it since the first time you heard about a Calder Falls father, which was 1962, in a newspaper your mother left face down on the kitchen table so you wouldn't see it. You saw it.

-> handset

= handset
# hint:Pick up the handset, or key the police band knob on the Radio tab. Either one answers the call.
The handset hangs on its hook by the shifter, coiled cord gone stiff with cold.
+ [Pick up the handset and take the call] -> take_call
+ [POLICE: Key the police band and take the call] -> take_call
+ [Let somebody closer take it]
    You let your hand sit on the wheel.
    Ten seconds. Twenty. Nobody else answers. Nobody is closer. You checked the duty board twice before you left this morning, which you will not be telling anyone.
    ~ resolve -= 1
    -> handset

= take_call
"Troop F, this is Brennick, Major Crimes, unit four-one-one. I'm on 9 north of Hollis. I'll take Calder Falls."

A pause. The dispatcher is Marjorie, who has worked weekends since Nixon and knows every voice on the band.

"Four-one-one, copy. You're a long way north, Cal."

"I was driving anyway."

"Copy that." Another pause, longer. "Lieutenant Okafor's already rolling from the barracks. She'll meet you at the scene. County officer on site is a Pell, Thomas. Ostrander County PD."

"Copy. Four-one-one out."

You hang the handset back on its hook. Your hand stays on it a second longer than it needs to.
-> drive

=== drive ===
# time:15:31
# music_layer:drums off
# hint:The Radio tab has an AM dial. Drag the needle. Something might be on a frequency.
The fog starts at the county line like somebody drew it there.

One mile you can see the tree line on both sides of the road, the leaves gone to rust and lemon, the sky the color of a nickel. The next mile the trees are rumors. The headlights push into the white and the white pushes back.

The sign says OSTRANDER COUNTY in reflective letters, and under it, in letters somebody painted by hand on a board and bolted on, HOME OF OSTRANDER PAPER. Somebody else has come along since with black spray paint and changed HOME to TOMB.

You haven't seen this road since you were nine years old and lying across the back seat of a 1951 Plymouth, watching the telephone wires dip and rise past the window, and your mother saying keep your head down, Cally, keep your head down, until the wires stopped and there was only sky.

You keep your head up now. It's a habit you made on purpose.

-> drive_choices

= drive_choices
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> drive_choices
+ [Turn on the AM radio for company] -> am_radio
+ [RADIO:1610: Advisory station] -> advisory
+ [Drive. Just drive.] -> water_tower_sight

= am_radio
You click the dashboard radio on. WCAL out of Hollis is playing the back half of a Hall and Oates song through a wall of hiss. Then the hiss wins. You turn the dial. Farm report. Static. A preacher telling somebody named Dolores that it isn't too late. Static.

Right at the top of the dial, where the highway advisory stations sit, the ones that tell you about lane closures, there is a voice. Flat, even, like a recording of a man reading a list.

You can't make out the words from here. You'd have to tune it in.
~ attunement += 0
+ [RADIO:1610: Advisory station] -> advisory
+ [Turn the radio off] -> water_tower_sight
+ [Drive. Just drive.] -> water_tower_sight

= advisory
# speaker:1610
# music_static:0.35
"...advisory for Ostrander County. Route 9 northbound, fog, visibility under one hundred feet. Cobb Road, one lane, four occupants. Four occupants. Mill Street, closed. Traveler, reduce speed. Traveler, you are expected."
~ attunement += 1
# music_static:0
The station drops out and the dial gives you nothing but hiss.

You tell yourself highway advisory stations run on a loop and nobody updates them. You tell yourself Cobb Road was in the dispatch and you heard it ten minutes ago. You tell yourself a lot of things. You have been in this county for seven minutes.
~ hurt(1)
# note:Advisory station, top of the AM dial. Said "Cobb Road, four occupants." Said "you are expected." Check: who runs highway advisory for Ostrander County?
-> water_tower_sight

= water_tower_sight
# music_layer:drums on
The road crests a hill and for a moment the fog thins, and there is Calder Falls in the valley below you like something left in a sink.

The mill takes up the whole bend of the river: brick sheds, the long sawtooth roof of the machine room, two stacks that haven't smoked since spring of last year. Beside it, on four black legs, the water tower. OSTRANDER PAPER on the tank in letters taller than a man. On top of it, a single red light, blinking slow.

They shut the last paper line eighteen months ago. Half the town worked there. Your father worked there. Somebody still pays the electric bill on that light.

The fog closes over the town again, and the road goes down into it.
+ [Count the blinks]
    You count without meaning to. Blink. One, two, three, four, five, six. Blink. Every six seconds, same as your wipers.
    You turn the wipers off.
    ~ hurt(1)
    -> into_town
+ [Look at the road]
    -> into_town

= into_town
# time:15:58
# map:cobb_road
# music:the_hush
Main Street is a long gray throat of closed things. HALVORSEN HARDWARE, CLOSED, SEE YOU IN SPRING, in a window where the spring has come and gone. A bank with plywood over one pane. The Rexall. The VFW. A bar called the Spindle with a beer sign lit in the window and a Pontiac out front, which is the only proof you've seen so far that people live here.

You pass the end of Mill Street and don't look down it. You know what's down it. You know which house.

St. Adalbert's sits on the hill above the square, red brick and a steeple that disappears into the white about halfway up. There's a marquee by the steps, the kind with plastic letters you slide into tracks.

MEN'S CHOIR TUES & THURS 7PM
ALL WELCOME
HE KNOWS YOUR NUMBER

You read it twice. The second time it says the same thing, which is not as reassuring as it should be.
+ [Pull over and photograph the sign]
    -> camera_lesson
+ [Keep driving]
    -> cobb_road_end

= camera_lesson
You don't have the Polaroid out of the trunk yet. You make a note instead, in the spiral pad you keep in your coat. Your handwriting is worse than it was when you were twenty-five, and it was never good.
# note:St. Adalbert's marquee: MEN'S CHOIR TUES & THURS. "HE KNOWS YOUR NUMBER." Psalm reference? Ask.
# hint:Notes go into the Notebook tab. Photos and statements go on the Evidence tab.
~ evidence += 1
-> cobb_road_end

= cobb_road_end
Cobb Road runs off the county two-lane past the edge of town, where the houses stop pretending to be a neighborhood and start sitting by themselves on their own patches of brown lawn, each with a mailbox at the end of a long gravel drive.

Twenty-two is the last one before the road goes to dirt.

There are two county cruisers at the end of the drive, lights going, no sirens, and one unmarked state Ford you recognize because you've been driving the same one for three years. Lieutenant Okafor is leaning on its fender with her arms crossed, in a gray wool coat that makes her look like she's going to church.

You park behind her and kill the engine. The fog fills in the space where the headlights were.
-> okafor

=== okafor ===
# time:16:04
# music_layer:lead off
# hint:Talk to Okafor. What you tell her changes how she treats you later.
Dana Okafor is forty-four, came over from Newark PD in 1979, and is the only lieutenant in Troop F who has never once asked you how you're doing in the voice people use when they've heard about the divorce. You would take a bullet for her for that alone.

"Brennick." She doesn't uncross her arms. "You made good time."

"Roads were empty."

"Mm." She looks at you the way she looks at a suspect's alibi, which is to say like she's already found the hole in it and is waiting to see if you'll point to it yourself. "Marjorie says you were on Route 9 northbound before the call went out. On a Sunday. On your weekend with Nora."

"Nora's with her mother. It's Paula's weekend."

"It's your weekend," Okafor says. "I can read a duty board."

-> okafor_choice

= okafor_choice
+ [Tell her the truth: you were born here]
    -> okafor_truth
+ [Tell her part of it: you've been following Calder Falls cases]
    -> okafor_part
+ [Tell her nothing. Ask about the scene.]
    -> okafor_deflect

= okafor_truth
"I was born here," you say. "Nine Mill Street. My mother took me out of this town in 1957 and I've been reading about it ever since."

Okafor's arms come uncrossed. That's the most surprise you've ever seen out of her.

"Your file says Hollis."

"My file says where I went to school."

She looks at the fog, then at you, for long enough that you can hear the cruiser engines ticking as they cool.

"Okay," she says finally. "Okay. You tell me if this gets to you. I mean it, Cal. You tell me before it gets to you, not after."

"I will."

You both know you won't. She gives you the case anyway.
~ told_okafor_truth = true
~ resolve += 1
# note:Told Okafor about Mill Street. She took it better than I would have.
-> okafor_brief

= okafor_part
"There's a pattern up here," you say. "Fathers. Going back to the fifties. I've been clipping the cases for years. Nobody else is looking at them together."

"A pattern."

"Seven since 1957 that I can find. Eight now."

Okafor considers that. "That's a hobby, Cal. That's a strange hobby for a man to have about one county."

"Everybody's got something."

"Mm." It isn't belief. It isn't disbelief either. "Bring me the clippings when we're back. All of them."
~ evidence += 1
-> okafor_brief

= okafor_deflect
"What've we got?"

Okafor lets you get away with it, which is its own kind of answer. "We'll talk about your weekend later." She uncrosses her arms and takes a notebook out of her coat, and just like that she's a lieutenant again.
~ resolve -= 1
-> okafor_brief

= okafor_brief
# evidence:ev_okafor_brief;statement;Okafor's briefing;Harlan family, 22 Cobb Rd. Found by neighbor 12:40.
"Wesley Harlan, forty-one. Machine tender at Ostrander Paper for nineteen years until they shut the line in April of '85. Wife June, thirty-nine, cashier at the IGA. Two kids. Danny, ten. Beth, seven."

She reads it without looking at you, which is how she reads the bad ones.

"Neighbor, a Mrs. Cuddy, comes by after the eleven o'clock Mass with a coffee cake. Twelve-forty. Truck's in the drive with the engine running, radio on loud, Wes in the cab. She knocks on the truck window and he doesn't look at her. She goes to the house, the front door is open, she goes in. She's at the county hospital now. They gave her something."

"Wes?"

"Dead in the cab when Pell got here at one-ten. Service revolver from his army days on the seat. One round." She closes the notebook. "The radio was still on. Pell turned it off. I've already had words with Pell about touching things."

"The family?"

"Inside." She doesn't add anything to that. She doesn't need to. "ME's held up in Hollis till six with a pileup on 9. It's ours until then. I want you to walk it, Cal. Slowly. Like you do. Then you tell me what happened in there, because I've been in this job twenty-one years, and I walked through it once, and I couldn't tell you."

"What's wrong with it?"

Okafor looks at the house. It's a split-level, white aluminum siding, black shutters, a basketball hoop on the garage with no net. Every window has its blinds down. The front door is closed.

"I don't know," she says. "That's what's wrong with it. Go see Pell. He'll walk you to the door. I'm on the radio if you need me. Channel two. Key it and I'll hear you."
# item:camera
You pop the trunk and get the Polaroid out, the One Step with the rainbow stripe that the department bought in '79 and never replaced, and a fresh pack of film. Ten exposures. You put the camera strap over your head like a tourist.
# item:flashlight
And the flashlight, the long black Kel-Lite that doubles as a nightstick when it has to. You check it. It works.
# hint:You now have a camera and a flashlight. Look at the Evidence and Notebook tabs on the right any time.
-> pell

=== pell ===
# time:16:11
# music_layer:lead on
# map:cobb_road
# hint:Talk to Pell, photograph what matters, then go to the door.
Officer Thomas Pell is maybe twenty-three, with a mustache he's trying very hard to make happen. He's standing at the yellow tape where it crosses the walk, between a rosebush and the lamppost, with his thumbs hooked in his belt the way they teach you at the academy so nobody can see your hands shaking.

"Sergeant." He straightens up. "Lieutenant said you'd want to see the truck first."

The truck is a 1979 Ford F-150, brown and tan, rust coming up through the rocker panels. The driver's door is closed. There's a cloth over the windshield on the inside, which is something, at least. Pell has done that much right.
-> pell_choices

= pell_choices
+ [Ask Pell what he saw] -> pell_saw
+ [Photograph the truck] -> photo_truck
+ [Look at the radio in the truck] -> truck_radio
+ {pell_saw && photo_truck} [Ask about the choir] -> pell_choir
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> pell_choices
+ {pell_saw} [Go to the front door] -> front_door

= pell_saw
"Got here ten after one." Pell talks fast, like he's been rehearsing for somebody to ask. "Engine was running. Radio was going. I opened the door to check him and..." He nods at the truck instead of finishing. "Then I went in the house. I went in the house, Sergeant, and I came right back out, and I called it in, and I've been standing here since."

"You turned the radio off."

He flushes. "It was loud. It was just static, real loud. I couldn't think with it going. I know I shouldn't have touched it. The lieutenant already."

"What station?"

"I didn't look." He thinks about it. "Up high. All the way up the dial, I think. Way up where there's nothing."
# evidence:ev_pell_statement;statement;Pell's statement;On scene 1:10. Radio loud, static, dial "way up high."
~ evidence += 1
-> pell_choices

= photo_truck
You frame the truck in the viewfinder. The whole thing, cab to tailgate, the house behind it. The One Step whirs and pushes the picture out like a tongue.

You hold it by the edge and wait. The image comes up out of the brown slowly, the way they do: the truck, the house, the bare hoop over the garage.

There's something in the passenger window of the truck. A pale smear. Probably the cloth over the windshield catching the flash.

Probably.
# evidence:ev_photo_truck;photo;The truck, 16:13;Passenger window: glare?
~ evidence += 1
-> pell_choices

= truck_radio
You open the passenger door, not the driver's. The cab smells like Old Spice and cordite and something under both of them that you have smelled at enough scenes not to name.

You don't look left. You look at the dash.

The radio is a factory AM unit with two knobs and a sliding orange needle. The needle is all the way to the right, past the last printed number on the band, jammed hard against the stop. Somebody pushed it there and held it.

Taped to the dash beside it is a strip of masking tape with something written on it in blue ballpoint, in a hand that pressed down hard.

1610 - 4
# evidence:ev_truck_dial;object;Truck radio dial;Needle jammed past the top of the band. Tape on dash: "1610 - 4"
# note:Wes Harlan's truck radio: needle at the top of the dial. Tape on dash, 1610 - 4. Four people in that house. Four.
~ evidence += 1
~ hurt(1)
-> pell_choices

= pell_choir
"Pell. You from here?"

"Born and raised." He says it like an apology.

"St. Adalbert's has a men's choir. What do you know about it?"

Pell blinks. Whatever he was ready for, it wasn't that. "They're all right. They're old guys mostly. My uncle Lenny sang with them till his knees went. They do the funerals. They did a drive for laid-off families last Christmas, turkeys and stuff." He hesitates. "Mr. Harlan joined up last winter, I think. My mom said it was good for him. Getting out of the house."

"Your uncle Lenny still around?"

"He's in Florida," Pell says, then, after a moment, a little too quickly: "He moved to Florida."
# evidence:ev_pell_choir;statement;Pell on the choir;Wes Harlan joined the St. Adalbert's men's choir last winter.
# note:Wes Harlan joined St. Adalbert's men's choir winter of '85. Pell's uncle Lenny sang with them. "Moved to Florida."
~ evidence += 1
-> pell_choices

= front_door
# time:16:20
# music:cobb_road
Pell lifts the tape for you. You duck under it. He doesn't follow.

"Sergeant." You look back. He's got the expression of a man who's decided to say something and is regretting it in advance. "When I went in. The hallway. It's real long. Longer than it looks from out here. I don't know. I think I was scared."

"You did fine, Pell."

"Yes, sir."

The walk is concrete, cracked, with dandelions coming up in the cracks even this late in the year. Three steps up to the stoop. The storm door is aluminum with a scalloped edge and a big cursive H in the middle of the grille. The front door behind it is painted a red that was probably cheerful once.

You put your hand on the knob.
+ [Go in]
    -> go_in
+ [Call Okafor first]
    -> call_first
+ [POLICE: Call Okafor first]
    -> call_first
+ {second_run} [RADIO:1610: Stay on 1610 instead]
    -> test_pattern_start

= call_first
You key the handheld on your belt. "Lieutenant. Brennick. I'm going in."

"Copy, Cal." Her voice is small and clear in the speaker, and behind it you can hear the cruiser engines and the gravel and the whole ordinary afternoon. "I'm right here."

It helps more than you'd like it to.
~ steady(1)
-> go_in

= go_in
You open the door. Warm air comes out to meet you, the furnace running, the smell of a house that people live in: dish soap, a pot roast from Saturday, old carpet, kids.

You step inside and close the door behind you, because that is what you do at a scene, you control the doors.

It shuts with a click that is louder than it should be.

Outside, faintly, very faintly, you hear the cruisers. The gravel. Pell, saying something to somebody.

Then you don't.
# pause:2
-> act1_start
