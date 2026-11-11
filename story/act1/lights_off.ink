// ============================================================
// Chapter 3. Act I: Cobb Road, lights off. Loops 5 to 8.
// June starts to hunt the hallway. The text starts to lie.
// ============================================================

=== lights_off_intro ===
# chapter:3:Cobb Road, lights off
# clear
# time:16:20
# music:cobb_road
# music_layer:pad off
# hint:June hunts by sound. In the dark the hall text changes in the same way it did with the lights on: find the one difference.
You try the switch by the front door. Up, down, up. Nothing. You try the lamp on the hall table. The cord is plugged in. The bulb is fine; you can see the filament in the gray light. Nothing.

You key the handheld.
# speaker:police
"Cal. Copy." Okafor. "You've been in there about two minutes. Porch light just went off out here. Power company says there's no outage on Cobb."

"Lights are out in here too."

"You want to come out?"

You look down the hall. The kitchen faucet is still running, a thin steady sound like a radio between stations.

"No," you say. "Not yet."
# speaker:police
"Copy. Two minutes, Cal. Then I'm coming in after you."

She has said two minutes three times now. You decide not to count.
-> loop_top.loop_begin

// ------------------------------------------------------------ coats
=== coats_off ===
{ diff == coats:
    -> coats_on.coats_four ->
    -> robe_pocket
}
{ coats_off == 1:
    In the dark the coats are three tall shapes on the wall, and for a second, before your eyes sort them out, they are three people standing very still with their backs to you. Then they are coats. June's car coat. Danny's jacket. Beth's parka, which is the size of a pillowcase.
    You put your hand on Beth's. It's cold, cold all the way through, like it's been hanging outside.
    ~ hurt(1)
- else:
    The coats. Three of them. Beth's parka cold under your hand. Same as before.
}
->->

= robe_pocket
There's something stiff in the robe's pocket. You fish it out with two fingers. A folded sheet of mimeographed paper, purple ink, the kind every church office in America ran off on a hand-cranked machine until about five years ago.
MONDAY NIGHT FELLOWSHIP
St. Adalbert's Parish Hall, 7:30 PM
For the men of Calder Falls who have given their working lives to this town
COFFEE. FELLOWSHIP. PURPOSE.
"You were made for something larger."
All are welcome. All are counted.
Mrs. Margaret Lusk, Director of Music
Under that, in pencil, Wes has written FRIDAY RADIO. And under that, again, in a hand that's shaking: I CAN'T HOLD IT.
# evidence:ev_fellowship_program;statement;Fellowship flyer;Monday Night Fellowship, for laid-off mill men. "All are counted." Director: Mrs. Margaret Lusk. Wes wrote: "I can't hold it."
# note:Monday Fellowship for laid-off mill men, run by Mrs. Margaret Lusk, Director of Music. MARGARET L. from the phone card. Wes wrote I CAN'T HOLD IT. Hold what?
~ evidence += 1
~ hurt(1)
->->

// ------------------------------------------------------------ photo
=== photo_off ===
{ diff == photo:
    -> photo_on.photo_three ->
    ->->
}
{ photo_off == 1:
    You can't see much of the photo in the dark. Four pale ovals of faces against the brick. The shine on the frame.
    As you look, the pale oval on the far left, where Wes is, seems to turn very slightly toward the camera. Toward you.
    It's the light. There is no light.
    ~ hurt(1)
- else:
    The photo. Four pale faces. One of them turned a little toward you. Same as before, which is the worst part.
}
->->

// ------------------------------------------------------------ radio
=== radio_off ===
{ diff == hallradio:
    -> radio_glowing
}
{ radio_off == 1:
    The clock radio is a dark box. No numbers. The power's out, so of course it is.
    You put your hand on top of it. The plastic is warm. Warm like a radio that has been on for hours.
- else:
    The clock radio, dark, and warm under your palm. Same as before.
}
->->

= radio_glowing
The clock radio is on.
The power's out. The lamp beside it is dead. The radio's dial glows a soft orange anyway, and the little number cards have flipped to 16:10, and out of its one speaker comes a woman's voice.
# speaker:1610
"...and I know some of you feel useless. I know you feel like the mill took your hands. But you were not made to feed a machine. You were made for something larger. There is a room inside every one of you, and all we ask is that you make room."
A pause, the faint hiss of tape.
# speaker:1610
"Let's say it together, the way we practice. One six one zero."
And a roomful of men answer her, low and ragged and willing, like a congregation: "One six one zero."
# speaker:1610
"And now your own number. Just to yourselves. Count the ones at home."
Silence. The tape hisses. Somewhere in it, very faint, a man says "four." You know whose voice it is. You heard it on the phone.
# evidence:ev_fellowship_broadcast;statement;The clock radio, 16:10;A woman leading laid-off men: "make room." They answer "one six one zero." Wes says "four."
# note:Radio came on with the power OUT. Woman's voice, kind, teaching men to say 1610 and their household count. "Make room." This is a recording of the Fellowship. That is her. That is Margaret Lusk.
# warp:scrollback:a framed photo of the four of them=>a framed photo of the four of us
~ hurt(2)
~ attunement += 1
->->

// ------------------------------------------------------------ clock
=== clock_off ===
{ diff == clock:
    -> clock_on.clock_stopped ->
    ->->
}
{ clock_off == 1:
    You can't read the clock in the dark. You put your face close. 4:20. The second hand goes around, too loud.
    Under the ticking, if you hold your breath, there's another sound, a second clock somewhere behind the wall, ticking a hair behind this one, like an echo that has gotten lost.
- else:
    The clock. 4:20 if you squint. The echo behind the wall. Same as before.
}
->->

// ------------------------------------------------------------ phone
=== phone_off ===
{ diff == phone:
    -> phone_on.phone_off_hook ->
    ->->
}
{ phone_off == 1:
    The phone in its cradle. You lift the receiver. No dial tone. The line is dead the way lines are when the pole's down. You put it back.
    The card of numbers beside it is pale in the dark. MARGARET L. (CHOIR) is the only line you can still read.
- else:
    The phone. Dead line. MARGARET L. (CHOIR). Same as before.
}
->->

// ------------------------------------------------------------ living room
=== living_off ===
{ living_off == 1:
    The Zenith is still on in the living room, the only light in the house, gray and flickering. The ball game is gone. The screen is snow, and in the snow, if you look at it the way you look at clouds, there are shapes that might be people sitting very close together on a couch.
    Three plates on three trays. The milk in the glasses has gone yellow.
    You don't go in. You want to. You don't.
    ~ hurt(1)
- else:
    The living room. The snow on the Zenith. The shapes in it, sitting close. Same as before.
}
->->

// ------------------------------------------------------------ bathroom
=== bathroom_off ===
{ diff == bathroom:
    -> bathroom_open
}
{ bathroom_off == 1:
    The bathroom door, closed, locked. The drip behind it.
    You put your ear to the door, and the drip stops, all at once, the way a person stops talking when they hear you on the stairs.
    You step back.
    ~ hurt(1)
    ~ june_near = MIN(june_near + 1, 5)
- else:
    The bathroom door. Locked. Silent now. Same as before.
}
->->

= bathroom_open
The bathroom door is open an inch. Gray light comes through the crack, not from a window. From the water.
You push it open with the flashlight, not your hand.
The door frame is splintered on the inside, around the strike plate, the wood torn in long pale strips. Somebody kicked this door in from the hall. The little push-button lock on the knob is still pushed in. Locked from inside, and kicked in from out.
The tub is full to the rim. The water is perfectly still. Nothing is in it. On the tile around the tub, drying, there are handprints. A woman's, spread wide. Two smaller sets. One very small.
On the edge of the tub there's a box of Crayolas, the big one with the sharpener in the back, and every black crayon in it is worn down to a stub.
She was in here with them. She locked the door and got in here with them and kept them quiet. She knew.
# evidence:ev_bath_lock;object;Bathroom door;Locked from inside. Kicked in from the hall.
# evidence:ev_handprints;photo;Handprints, bathroom tile;A woman's hands spread wide. Two children's.
# note:June locked herself and the kids in the bathroom. He kicked it in. She KNEW. How did she know? Beth's crayons, every black one used up.
~ evidence += 1
~ mercy += 1
~ hurt(2)
~ june_near = MIN(june_near + 2, 5)
->->

// ------------------------------------------------------------ children's rooms
=== kids_off ===
{ kids_off == 1:
    Danny's room is a dark box with a bunk bed in it. Somebody is on the top bunk. You can see the shape of a knee under the blanket.
    You put the flashlight on it without turning it on, the way you'd hold a gun on a door, and you stand there until your arm aches.
    It's a pillow. It's a pillow and a rolled-up blanket, and it doesn't move, and you leave the room backwards.
    Beth's moon nightlight is still on. The power's out and the nightlight is still on.
    ~ hurt(2)
- else:
    Danny's top bunk, the shape on it that is a pillow. Beth's nightlight, on without power. Same as before.
}
->->

// ------------------------------------------------------------ kitchen
=== kitchen_off ===
{ diff == drawing:
    -> two_drawings
}
{ kitchen_off == 1:
    The kitchen faucet is running into the sink. You turn it off. It stops. When you take your hand away it starts again, the same thin stream, like you never touched it.
    The table is still set for four. One of the chairs is pulled out a little further than the others, the way a chair is when a man stands up from it fast.
- else:
    The faucet, running. The four places. The chair pulled out. {diff == calendar:The calendar is wrong.|Same as before.}
}
->->

= two_drawings
Two drawings on the refrigerator now.
The first is the house, the one that was there before.
The second is new. It's the hall table, drawn by a child standing in front of it, so the table is a giant thing at the top of the page. On the table is the clock radio, drawn very carefully, the little cards with numbers on them. Inside the radio, in black crayon, back and forth and back and forth, is the zigzag man, folded up small.
In front of the table is Daddy. His mouth is a big black O, and out of it come numbers, the way a kid draws a song coming out of a radio: 1 6 1 0 4. 1 6 1 0 4.
Across the bottom, in pencil, in a seven-year-old's capitals with the S backward:
DADDY IS PRACTISING. I TOLD MOM.
# evidence:ev_beth_radio_drawing;photo;Beth's second drawing;The zigzag man inside the radio. Daddy with numbers coming out. "DADDY IS PRACTISING. I TOLD MOM."
# note:Beth heard him practicing the count and TOLD JUNE. That's how June knew. A seven-year-old saw it and told her mother, and her mother believed her.
~ evidence += 1
~ mercy += 1
~ hurt(1)
->->

// ------------------------------------------------------------ theories
=== theory_t3 ===
# theory:t3;Why was June in the bathroom with the children?
# slot:she was;Hiding them from Wes*@ev_bath_lock;Giving them a bath;Sick
# slot:she knew because;Beth heard him practicing the count and told her*@ev_beth_radio_drawing;Mrs. Cuddy warned her;The choir called the house
# slot:he got in;He kicked the door in*@ev_bath_lock;He had a key;She opened it for him
# hint:The bathroom door and Beth's second drawing on the fridge.
The kitchen door. You write slowly, because your hand doesn't want to write this one.
+ [FILE: File a theory]
    -> theory_result(3)
+ [Keep looking]
    -> hall

=== theory_t4 ===
# theory:t4;How did they bring Wes in?
# slot:the radio came from;The St. Adalbert's men's choir*@ev_radio_gift;His brother;The IGA raffle
# slot:they found him at;Monday Fellowship, for men the mill let go*@ev_fellowship_program;The Spindle;The unemployment office in Hollis
# slot:the radio taught him;To say 1610 and count the people in his house*@ev_fellowship_broadcast;Hymns for the funerals;Nothing, he just liked it on
# slot:it is run by;Mrs. Margaret Lusk, Director of Music*@ev_fellowship_program;Father Kasprzak;Nobody, it is just men talking
# hint:The radio sticker, the flyer in the robe pocket, and what the radio said when it came on by itself.
The kitchen door. The faucet runs. You write it down anyway.
+ [FILE: File a theory]
    -> theory_result(4)
+ [Keep looking]
    -> hall

// ------------------------------------------------------------ end of chapter 3
=== lights_off_end ===
# music:june
You walk to the end of the hall, through the kitchen. The faucet stops on its own as you pass it.

You are standing with your back to the front door.

The gray around the blinds goes out.

Not dusk. Not a cloud. It goes out the way a TV does when you pull the plug, a white line, then a dot, then nothing. The dark that's left is the kind you get in a mine, in a closet, in a hospital bed at three in the morning. You hold your hand up in front of your face and you can't find it.

# fourth:crash
You thumb the Kel-Lite on.

The beam goes down the hall like a hand reaching for something, and the hall goes back further than the beam goes.
# pause:2
~ loop = 9
~ repeats = 0
-> loop_top
