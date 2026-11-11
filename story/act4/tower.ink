// ============================================================
// Chapter 11. Act IV: the water tower. Harold Lusk's transmitter,
// still on the air thirty years after the mill bought its last tube.
// ============================================================

VAR climbed = false

=== act4_start ===
# chapter:11:The water tower
# theme:dead_signal
# music:water_tower
# map:mill
# map:water_tower
# time:23:40
# hint:The transmitter is at the top. Decide whether Jo comes with you.
Ostrander Paper sits in the bend of the river like a dead animal too big to move. The sawtooth roof of the machine room, the brick sheds, the dark stacks. Every window in the machine room is lit. The yard is full of cars, parked neat in rows, Buicks and pickups and a hearse from one of the two funeral homes, as if the whole town came to a wedding.

The water tower stands over all of it on its four black legs. The red light on top is blinking. Every six seconds.

Jo pulls up at the foot of the tower and turns the engine off and sits with her hands on the wheel.
{ jo_hums >= 4:
    She's humming. She doesn't stop when the engine stops. She doesn't stop when you say her name.
- else:
    "Okay," she says. "Okay. What's the plan?"
}
-> tower_base

=== tower_base ===
+ {jo_with_you} [Send Jo back to the substation to sit with Ray and wait for morning] -> send_jo
+ {jo_with_you} [Bring Jo up the tower with you] -> bring_jo
+ {not jo_with_you} [Climb] -> climb
+ {cigarettes > 0} [Smoke a cigarette at the foot of the ladder] -> smoke -> tower_base

= send_jo
"Go back to the substation, Jo. Lock the door. Sit with Ray. Don't turn anything on."

"Cal." She looks at the tower, and the lit windows of the machine room, and back at you. "Cal, I'm a cop. You don't get to send me home."

"Your father went to sleep, Jo. Four years he held it, and then he went to sleep, and Margaret Lusk says it runs in families. They want you. If you go in there, they'll have you."

Jo's jaw works. She doesn't argue. She can hear herself humming, now. You can see her hear it.

"Morning," she says. "You come and get me in the morning."

"I will."

She starts the Gran Fury. She doesn't look back. You watch her taillights go up the mill road and into the fog until they're two red points, and then one, and then none.
~ jo_saved = true
~ jo_with_you = false
~ mercy += 3
~ hurt(1)
-> climb

= bring_jo
"Come on," you say. "I'm not doing this alone."

"Good," Jo says, and gets out, and checks her shotgun, and starts humming again on the first rung of the ladder.
~ resolve -= 1
-> climb

=== climb ===
# dark:on
# battery:low
# shadow:don't look down
# music_layer:drums off
The ladder goes straight up one leg of the tower in a steel cage, rung after rung, cold enough to hurt through your gloves. The flashlight is in your teeth. The beam swings with every rung, over the rivets, the rust, the fog.

At a hundred feet the fog thins. At a hundred and twenty you come up out of it, and the whole valley is under you, a white sea, and the sky over it is black and absolutely clear and full of stars, and you can hear the transmitter now. Not with your ears. In your fillings.

There's someone on the ladder above you.

A Choirman, robe and stole, coming down. His face is snow. He fills the cage. There's no way past him. # timed:6:1
+ [Hold still and let him pass]
    You press yourself against the rungs and hold still and don't breathe.
    He passes through you. It's like walking through the cold aisle at the IGA. When he's gone, you're shaking so hard you almost lose the flashlight, and somewhere far below you hear him reach the bottom and walk away across the gravel, singing.
    ~ hurt(2)
    ~ resolve += 1
+ [Look at his face]
    You look up into his face as he comes.
    In the snow, for one second, it comes in clear. An old man. Glasses. You know him. He's the pharmacist from the roster, the one who sold your mother aspirin in 1956. He's crying.
    Then he's through you, and gone.
    ~ hurt(3)
    ~ attunement += 1
+ {rounds > 0} [Shoot]
    You fire straight up the cage. The round goes through him and rings off the steel somewhere above, and he keeps coming. Of course he does.
    ~ rounds -= 1
    ~ hurt(3)
- -> catwalk

=== catwalk ===
# dark:off
# battery:ok
# music_layer:drums on
~ climbed = true
The ladder ends at the catwalk that rings the tank, a grating with a pipe railing. OSTRANDER PAPER in letters taller than you are, on the curve of the tank beside you, the paint peeling in long strips.

On the far side of the tank there's a shed. Steel, the size of a phone booth, bolted to the catwalk. The red light is on a mast on its roof. The door is open, and inside there is light: the orange glow of vacuum tubes.

{ jo_with_you:
    Jo comes up off the ladder behind you and stands at the rail, looking out at the stars. She isn't humming now. She's singing, very softly. She has a lovely voice.
}
-> shed

=== shed ===
# hint:{read_history:You know who built this. Harold Lusk's transmitter. The library gazette showed the cabinet.|The transmitter in the shed. Look at it closely before you do anything to it.}
+ [Look at the transmitter] -> transmitter
+ [Look out over the town] -> look_out
+ {transmitter} [Break the transmitter] -> break_it
+ [RADIO:1610: Listen to it, this close] -> tower_1610 -> shed
+ [Climb down to the mill] -> act4_down

= transmitter
The cabinet is the one in the 1956 Gazette photograph, gray steel, rivets, a nameplate: OSTRANDER PAPER CO. YARD RADIO. DESIGNED H. LUSK. Behind a window in the front, a row of glass tubes, glowing orange, and one big tube in the middle the size of a quart jar, glowing violet.

There's no power cable. The plug end of a heavy cord hangs off the back of the cabinet, cut clean through, the copper green with thirty years of weather.

It's on anyway.

There's a wooden chair in the corner of the shed. A man's hat on it, a fedora, gray with dust, a pair of headphones with cloth-covered wire on top of the hat. Somebody sat here and listened. Somebody died here, in July of 1956, of his heart, the Gazette said.
# evidence:ev_transmitter_shed;object;The transmitter shed;Harold Lusk's 1956 cabinet. Power cord cut and rotted. Tubes lit anyway. His hat and headphones on the chair.
~ evidence += 1
~ hurt(1)
-> shed

= look_out
From up here you can see all of Calder Falls under the fog, and you can see it because of the lights. Every house has one. A little point of orange or green in a window, a kitchen, a bedroom, a dashboard. Every radio in town, on, tuned to the top of the dial. Hundreds of them. The whole town lit up like a switchboard.

And beyond the town, faint, out past the county line, more of them. Down Route 9. Toward Hollis. Toward Ardell.

They're reaching further. Every family they empty, it reaches further.
~ hurt(2)
~ attunement += 1
-> shed

= break_it
{ read_history:
    You know what you're looking at. Harold Lusk's photograph is in your head: his hand on the cabinet, the big tube in the middle. The final amplifier. Everything else in there is just getting the signal ready for that.
    You put the Kel-Lite through the window and into the violet tube.
    It bursts with a sound like a lightbulb dropped in a church. The violet goes out. The orange tubes flicker, and dim, and stay dim.
    Below you, across the whole valley, the little radio lights go out. Not all of them. Most of them. Like a field of fireflies when a car door slams.
    ~ transmitter_damaged = true
    ~ evidence += 3
    ~ attunement -= 2
- else:
    You don't know what any of it does. You smash the glass and beat the tubes with the flashlight until the flashlight's lens breaks, and you're hitting them with the dented barrel in the dark.
    Some go out. Most don't. The big violet one in the middle takes three hits and doesn't even crack. It glows at you, patient.
    Below you, across the valley, a few of the little radio lights go out. A few.
    ~ evidence += 1
}
~ hurt(2)
-> shed

=== tower_1610 ===
# speaker:1610
# music_static:0.6
{ transmitter_damaged:
    "You hurt us," the voice says. It doesn't sound angry. It sounds like a child who's been slapped for the first time. "We only wanted to come home."
    ~ mercy += 1
- else:
    "This is where we come in, Cally. Harold built the door and then he wouldn't open it, and it killed him, the stubborn old thing. Margaret opened it. Margaret always opens the door." A pause. "If you break it, the town goes quiet. All of it. Forever. Is that what you want? Quiet?"
}
# music_static:0
~ attunement += 1
->->

=== act4_down ===
# music:mill_floor
You climb down into the fog.

At the bottom the gravel is wet and the mill is enormous and lit and full of singing, and the cars in the yard all have their radios on, all of them, every car, very low, saying numbers.

The office is in the brick building at the head of the yard. You have the key Margaret Lusk gave you, on its red ribbon.
{ jo_with_you:
    Jo comes down the last rungs behind you. She's still singing. She walks past you toward the machine room door before you can stop her, not fast, the way you walk up the aisle at church.
    "Jo!"
    She doesn't turn around.
}
-> mill_floor_start
