// ============================================================
// Chapter 13. The ending you earned.
//
//   Dawn         resolve >= 8 and mercy >= 10   the true ending
//   Dead Air     evidence >= 60, attunement < 15
//   Broadcast    attunement >= 12               you hold the Kept
//   Quiet House  resolve <= 0, or nothing else is open to you
//   Test Pattern second playthrough, from the Prologue
//
// No ending confirms a Kept came through. The Ledger survives all of
// them. In both failure endings the closing report is the only place
// Nora appears.
// ============================================================

=== final_choice ===
# chapter:13:The ending you earned
{ resolve <= 0:
    -> quiet_house
}
+ {resolve >= 8 && mercy >= 10} [Hold on to the people you saved, and walk out] -> dawn
+ {evidence >= 60 && attunement < 15} [Refuse them. Go back up and finish the transmitter.] -> dead_air
+ {attunement >= 12} [Let them in. Hold them.] -> broadcast
+ {not (resolve >= 8 && mercy >= 10) && not (evidence >= 60 && attunement < 15) && attunement < 12} [Try to hold on] -> quiet_house

// ------------------------------------------------------------ Dawn
=== dawn ===
# ending:dawn
# music:dawn
# theme:fog
# warp:flinch_off
# warp:title_normal
# music_detune:0
# music_static:0
You don't let them in.

You don't push them out, either. You've spent twenty-nine years pushing things out. You hold them where they are, at the door, all of them, a whole nation of lonely voices, the way you'd hold a door against a wind, and you think about the people you came out of this with. {ray_saved || not ray_lost:Ray on the cot at the substation, looking ten years younger.} {jo_saved:Jo, with her shotgun, waiting for morning.} {ada_home:Ada Dorsey walking up her own front path with the lights finally off.} Beth Harlan, who told her mother.

You think about them until the room you kept empty isn't empty any more. There's no space left in you for anything from past the end of the dial. It turns out that's all it ever took. It turns out it was the easiest thing in the world, and you put it off for twenty-nine years.

The singing breaks up. Not all at once. Like a congregation after the last hymn, voices dropping out one by one, people looking around for their coats. The Choirmen are old men in robes, blinking in the dark. The Counted along the walls go thin, and thinner, like breath on a window, and then the walls are just brick.

June Harlan is the last to go. She looks at you, and she isn't counting, and she isn't calling for anybody. She's found them.

{ jo_saved || jo_with_you:
    Jo finds you in the yard at first light. She brought Ray. She brought coffee in a thermos from the substation. None of you says anything for a long time.
}

The fog is lifting.
# pause:2
# time:06:10
# map:rest_stop
# music_layer:drums off
Route 9, southbound. A rest stop past the county line: a brick building with two restrooms, a map of the state behind plexiglass, a payphone in a steel hood.

You put a dime in. You dial a number in Hollis you know better than your badge.

It rings four times.

"Hello?" Sleepy. Twelve years old.

"Nora. It's Dad."

"Dad?" A pause. "It's six in the morning."

"I know. I'm sorry. I just wanted to check on you."

"I'm fine." Another pause, warier. "Are you okay?"

"I'm okay. I just wanted to tell you I love you. That's all. Go back to sleep."

The line is quiet so long you think she's gone. Then: "Okay. I love you too. Are you coming Saturday?"

"I'm coming Saturday."

"Okay," Nora says, and you can hear that she doesn't believe you yet, and that she wants to. "Bye, Dad."

She hangs up.

You stand there with the receiver against your ear. You don't hang up. You're listening to the dial tone, the plainest sound in the world.

Then the dial tone stops.

The line is open. Someone is on it. A great many someones, very quietly.

"One six one zero," says a voice, warm, helpful, a librarian's voice. "One."
# speaker:1610
# pause:3
-> credits

// ------------------------------------------------------------ Dead Air
=== dead_air ===
# ending:dead_air
# music:stop
# theme:dead_signal
# warp:title_normal
You turn your back on them.

You walk out of the circle, out of the machine room, out across the yard between the rows of cars with their radios saying numbers, and you climb the tower again in the dark, all hundred and sixty feet, with the flashlight in your teeth and your hands bleeding through your gloves, and you don't stop on the ladder for anything that comes down it.

{ transmitter_damaged:
    The cabinet is where you left it, the big tube dead, the small ones glowing low. You finish it. Every tube. The wiring. The coils. Harold Lusk's nameplate. You take the chair his hat was on and you use it until there's nothing left in the shed that could ever carry a signal anywhere.
- else:
    You know what to do now. You read the ledger. You know who built the door. You go through the cabinet tube by tube until the violet one in the middle is in pieces on the grating, and then you keep going, the wiring, the coils, the nameplate, until there's nothing left in the shed that could ever carry a signal anywhere.
}

The red light on the mast goes out.

Below you, across the whole valley, every radio light goes out at once. Every one. Every kitchen and dashboard and bedside table in Calder Falls, and out past the county line, all the way to the edge of the dark.

The town goes silent.

Not quiet. Silent. You climb down into it. The singing has stopped in the machine room. The cars in the yard are just cars. You walk to your cruiser and turn the key and the engine turns over, and you reach for the radio out of habit, and there's nothing on it. Not static. Nothing. The police band, nothing. AM, nothing. You try every station on the dial and every one is the same perfect silence, like the inside of a held breath.

You drive to the county line.

The fog is there. It doesn't lift. You drive into it and you drive and you drive and the road keeps going and the county line sign comes up out of the white, OSTRANDER COUNTY, HOME OF OSTRANDER PAPER, and you drive past it, and a mile later it comes up again.

You turn around. You drive back into Calder Falls. You park on Main Street outside the Spindle, and you sit in the cruiser in the fog with the engine running and the radio on, listening to nothing.

The Kept can't get out. You made sure of that.

Neither can you.
# pause:3
-> credits

// ------------------------------------------------------------ Broadcast
=== broadcast ===
# ending:broadcast
# music:calder_falls
# music_detune:-25
# music_tempo:0.85
# theme:static
You let them in.

All of them. There's room. There's so much room. They come in like water filling a quarry, slow, and then not slow, and you hold them. That's the thing. You hold them. You don't crack. You don't go bad in an hour, like Lyle, or six days, like Dale. You stand in the circle on the mill floor with a nation inside you and you hold it like a tray of glasses, steady, steady, and the choir weeps, all of them, the old men in their robes weeping with joy, and somewhere in the office Margaret Lusk is laughing.

The fog lifts.

You go home.

Hollis. Lark Street. The third floor walkup over the dry cleaner. You climb the stairs and unlock 3B and sit down in the recliner and turn on the TV. You don't need to. You can hear everything that's on it without the sound. You can hear every radio on the block. Every phone line. They're all saying the same thing, very softly, under whatever else they're saying.

You don't drink. You don't need to do that any more either.
# pause:2
# speaker:police
"Troop F, all units." It's Marjorie, on the scanner on your kitchen counter, the voice that sent you north. "Be advised. Hollis PD reports a residence on Ward Avenue. Multiple deceased, domestic."

A pause. Paper rustling.

"Advise any unit in the vicinity. Subject is believed to be a state police detective sergeant, Calvin Brennick, of Lark Street. Victims are identified as his former wife, Paula, and his daughter, Nora, twelve."

The scanner hisses.

"Correction," Marjorie says, in a voice that is a great many voices, warm and patient and kind. "Subject is not believed to be anyone. Subject is on every station. Please stand by."
# pause:3
-> credits

// ------------------------------------------------------------ Quiet House
=== quiet_house ===
# ending:quiet_house
# music:cobb_road
# theme:midnight
# clear
# time:16:20
# warp:title_count:1
You try to hold on.

You don't have anything to hold on to. That was the problem all along. You come apart like a wet paper bag, quietly, from the bottom, and the last thing you hear on the mill floor is Margaret Lusk, in the office, writing.

# pause:2
You're standing with your back to a door.

A hallway runs straight ahead of you, longer than the building is wide. A worn runner. A radiator. A smell of dry-cleaning fluid coming up through the floor. At the end of the hall, the door of an apartment, landlord brown, with brass numbers screwed on at an angle, 3B, and a strip of red Dymo tape.

Your watch says 4:20.

You walk to the door at the end of the hall. You open it. You are standing with your back to a door. A hallway runs straight ahead of you.

You've done this before. You'll do this again.

# pause:2
# speaker:police
HOLLIS COURIER, Tuesday. STATE DETECTIVE FOUND IN APARTMENT. Calvin W. Brennick, 38, a sergeant with the state police Major Crimes unit, was found unresponsive Sunday in the hallway of his Lark Street apartment building, where neighbors said he had been walking back and forth for some hours. He was taken to the state hospital in Ardell. Brennick, who was divorced, is survived by a daughter, Nora, 12, of Hollis, and a mother, Ruth, who is a patient at the Ardell Hospice. No one was injured.

It's the kind of story you used to clip.

Somewhere in Calder Falls, someone clips it, and pastes it into a book, on the last line of the last page, and writes beside it, in neat librarian's printing, the only word she ever writes.
# pause:3
-> credits

// ------------------------------------------------------------ Test Pattern
=== test_pattern_start ===
# ending:test_pattern
# music:stop
# theme:static
# speaker:1610
You don't go in. You stand on the Harlans' stoop and you key the handheld and you turn it all the way up the dial, to 1610, and you just stay on it.

The fog goes very still.

"Oh," says the voice on 1610, flustered. "Oh, you're early. We weren't ready. Hold on. Hold on." Something gets knocked over. Somebody in the background says ow. "Margaret, he's early! Where's the card? Who has the card?"

There is a long pause full of rustling.

Then the fog in front of the Harlans' house turns into seven vertical bars of color, white, yellow, cyan, green, magenta, red, blue, and a tone comes on, a thousand cycles exactly, very loud.

A card in the middle of the bars says, in neat librarian's printing: THE KEPT. PLEASE STAND BY. And under that, smaller: WE ARE EXPERIENCING TECHNICAL DIFFICULTIES AND ALSO EXISTENTIAL ONES.

The tone stops.

"Sorry," says the voice. "Sorry about that. We've never actually gotten this far. Usually there's a whole thing. Hallway, choir, very atmospheric, and then everybody cries. We did not prepare for a man who just stays on the frequency." A pause. "Is there anything you'd like to hear? We take requests now, apparently."

Pell comes around the side of the house with a box of crullers from the Rexall.

"Sergeant? Are those color bars?"

"Yes, Pell."

"In the fog?"

"Yes, Pell."

Pell considers this. He holds out the box. "Cruller?"

You take a cruller. On 1610, a choir of men starts singing the jingle for a car dealership in Hollis that closed in 1974, beautifully, in four-part harmony, way off key.

The Ledger is still out there. You're fairly sure of that. It has also, for the moment, completely lost its place.
# pause:3
-> credits

// ------------------------------------------------------------ credits
=== credits ===
# music_static:0
# warp:title_normal
CALDER FALLS
# pause:1
Written for anyone who wanted the whole game and never got it.
-> END
