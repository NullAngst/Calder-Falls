// ============================================================
// Chapter 4. Act I: Cobb Road, flashlight only. Loops 9 to 12.
// The house starts showing Brennick his own life. The window lies.
// ============================================================

=== flashlight_intro ===
# chapter:4:Cobb Road, flashlight only
# clear
# time:16:20
# dark:on
# music:june
# warp:radio_drift
# hint:Move the mouse to move the flashlight over the text. The difference this loop is somewhere in the hall again.
The flashlight makes a circle the size of a dinner plate wherever you put it. Everything outside the circle is gone.

You can do this. You have done this. You have walked a farmhouse in Kettering at four in the morning with this same light and a man in the barn with a shotgun, and you came out, and you went home, and you didn't go home, you went to the Rustic Inn on Route 4 and you sat there until they closed.

You key the handheld.
# speaker:police
"Cal," Okafor says, from a long way off. "You've been in there about two minutes."
"I know."
# speaker:police
"You don't sound right."
"I know," you say again, and you let go of the key before she can answer.
-> loop_top.loop_begin

// ------------------------------------------------------------ coats
=== coats_flash ===
{ coats_flash == 1:
    The beam finds the coats one at a time. June's. Danny's. Beth's. When you move off Beth's parka and come back to it, the hood is turned toward you, the fur ruffled like someone has just pulled it off a small head.
    ~ hurt(1)
- else:
    The coats in the beam. Three of them. The hood of the parka, turned toward you. Same as before.
}
->->

// ------------------------------------------------------------ photo
=== photo_flash ===
{ diff == photo:
    -> photo_yours
}
{ photo_flash == 1:
    The photo in the beam. The four of them, Easter, the church steps. In the flashlight the colors are too bright, the yellow of June's dress almost white.
    Wes is back in the picture. He's looking straight into the lens now. Not smiling.
    ~ hurt(1)
- else:
    The photo. Wes in it again, looking into the lens. Same as before.
}
->->

= photo_yours
# warp:tabs_rename
The photo of the three of you.
Not the Harlans. You. Easter 1980, the steps of St. Luke's in Hollis, Paula in the blue coat she bought at Sibley's for that Easter and wore every Easter after until the divorce, Nora at six in white tights with one knee skinned, and you, thirty-two, in the only suit you owned, squinting. Paula's mother took this one. You've never seen this print. You have the other one, the one where Nora's laughing. This is the one before that. Nobody's laughing in this one.
You're standing a little apart from them. You don't remember standing apart from them. You turn the frame over.
ONE SIX ONE ZERO, THREE.
In your handwriting.
# evidence:ev_own_photo;photo;Easter 1980;Me, Paula, Nora. St. Luke's, Hollis. Back: "one six one zero, three." My handwriting.
# note:The photo is MINE. Easter 1980. The back says three. In my hand. I never wrote that. I never wrote that.
~ hurt(2)
~ evidence += 1
->->

// ------------------------------------------------------------ radio
=== radio_flash ===
{ radio_flash == 1:
    The clock radio in the beam. Dark. The numbers on the little cards say 16:10. They said something else before, you're sure of it, and you can't remember what.
    You look over at the Radio tab you carry in your head, the one where you keep track of the dial. The needle has moved. You didn't move it.
- else:
    The clock radio, dark, 16:10 on its cards. Same as before.
}
->->

// ------------------------------------------------------------ clock
=== clock_flash ===
{ clock_flash == 1:
    The sunburst clock. 4:20. Your watch, 4:20. You have been looking at 4:20 for, by your own count, a little over an hour of walking.
    You tap the watch face, because people do that. It doesn't help. It never helps.
- else:
    The clock. 4:20. Same as before. It's always going to be 4:20.
}
->->

// ------------------------------------------------------------ phone
=== phone_flash ===
{ diff == phone:
    -> phone_ringing
}
{ phone_flash == 1:
    The phone, quiet, in its cradle. The card of numbers. In the flashlight you can see that the bottom line, MARGARET L. (CHOIR), was written over something else that was erased. You tilt the card. The erased word comes up in the grooves of the paper. POLICE.
    # note:June's phone card: MARGARET L. (CHOIR) written over POLICE. Somebody erased the police number and wrote the choir in its place.
    ~ evidence += 1
- else:
    The phone in its cradle. MARGARET L. over POLICE. Same as before.
}
->->

= phone_ringing
# battery:low
# fourth:corrupt_save
The phone is ringing. An old ring, a real bell inside the box, the kind phones haven't had in this county since they switched over the exchange.
You pick it up.
# speaker:1610
"Cally?"
A woman's voice. Young. Out of breath, like she's been carrying something heavy down stairs.
# speaker:1610
"Cally, it's Mama. Listen to me. Listen. When he comes home tonight he's going to count. He's going to stand in the kitchen and count. When he says your name you keep your head down, baby, you hear me? You keep your head down and you don't let him see your face."
"Mom."
# speaker:1610
"We're going to go for a drive. We're going to go see Aunt Lil. Get your shoes."
And then there's static, and in the static an older voice, the same voice gone thin and dry with sixty-three years and whatever they've got her on at the hospice in Ardell, saying "Cal? Is that you? Where are you, honey? They said you called."
The line goes dead before you can answer either of them.
# evidence:ev_mothers_call;statement;The phone, ringing;Mom in 1957: "When he counts, keep your head down." Then Mom now, at the hospice: "Where are you?"
# note:The phone. My mother, 1957, the day she took me. "When he counts keep your head down." Then her now. She's at Ardell. I haven't called in three weeks.
~ hurt(2)
~ mercy += 1
->->

// ------------------------------------------------------------ living room
=== living_flash ===
{ living_flash == 1:
    The beam goes into the living room and finds the couch.
    There are three people on it, sitting close together, a woman and two children, their faces turned away from the light toward the dead television.
    You don't make a sound. You put the beam on the floor and count to five and bring it back up.
    The afghan. The cushions. Three plates on three trays. Nobody.
    # shadow:they are on the couch
    ~ hurt(3)
- else:
    The living room. The couch, empty, every time you look straight at it. Same as before.
}
->->

// ------------------------------------------------------------ bathroom
=== bathroom_flash ===
{ bathroom_flash == 1:
    The bathroom door is closed again. The splinters around the lock are back in the frame, smooth, painted over, like it never happened. Like it hasn't happened yet.
    Behind the door, very quietly, a woman is singing. Not a hymn. The thing you sing to a kid who won't sleep, half the words gone, the tune carrying the rest.
    ~ mercy += 1
    ~ hurt(1)
- else:
    The bathroom door, mended. The singing behind it, very low. Same as before.
}
->->

// ------------------------------------------------------------ children's rooms
=== kids_flash ===
{ kids_flash == 1:
    Danny's room: the glove, the pennant, and on the top bunk, the pillow that isn't anything. Beth's room: the moon nightlight is off now. The drawings over the bed are gone. There are nine clean rectangles on the yellow wall where they were, and tape marks, and nothing else.
    Someone took them down. Someone wanted them not to be found.
    ~ hurt(1)
- else:
    The children's rooms. Beth's wall with the nine clean rectangles. Same as before.
}
->->

// ------------------------------------------------------------ the fifth door
=== extradoor_flash ===
{ extradoor_flash == 1:
    -> your_door
}
The fifth door. 3B. BRENNICK. You know what's behind it.
+ [Go in anyway] -> inside
+ [Leave it] ->->

= your_door
# shadow:you know this door
Between Beth's room and the kitchen there is a door that was not there before.
It isn't a door from this house. It's a steel apartment door painted landlord brown, with a peephole and brass numbers screwed on at an angle, 3B, and under the peephole a strip of embossed red Dymo tape that says BRENNICK.
You made that label. You made it the week you moved out, in March of '83, on Paula's label gun that she let you take. You never gave the gun back.
-> inside

= inside
The knob turns.
It's your apartment. Hollis, Lark Street, the third floor walkup over the dry cleaner. You know it by the smell first, the perc from downstairs and the cigarettes and the radiator. The flashlight finds the recliner you bought at the Salvation Army, the TV on its cart, a TV tray beside the recliner with a glass on it and a bottle of Seagram's Seven with two inches left.
The answering machine on the kitchen counter is blinking. 3, it says, in red.
+ [Play the messages] -> messages
+ [Pour the two inches into the glass] -> bottle
+ [Back out and close the door] -> back_out

= messages
You press PLAY. The tape squeals and rewinds.
"Dad? It's me." Nora. Eleven, maybe, when she left this one, not twelve yet. "Mom says you're picking me up Saturday at ten. Are you? Okay. Bye."
Beep.
"Dad, it's Saturday. It's ten thirty. Mom says call her. Okay." A breath. "Bye."
Beep.
"It's Nora." Older. Flatter. A girl who has stopped expecting anything. "Never mind."
The machine clicks off. The 3 goes back to 0.
You remember every one of those Saturdays. You were working, two of them. The third you were at the Rustic Inn, and you told Paula you were working.
# evidence:ev_own_door;object;Apartment 3B;My door. Seagram's, two inches left. Three messages from Nora I didn't return.
# note:3B. My place. Three of Nora's messages. I was working for two. The third I was drinking and lied about it. Wes Harlan didn't go home either. He went to Fellowship.
~ resolve += 1
~ mercy += 1
~ hurt(2)
~ evidence += 1
-> back_out

= bottle
You pour it. Two inches, more or less. It's the most natural thing in the world, doing that, here, in the dark.
You don't drink it. You stand there holding it, and the glass is cold, and you can smell it, and the machine blinks 3, 3, 3 at you like it's counting.
You set it down. You leave it full. That will have to be enough for today.
# evidence:ev_own_door;object;Apartment 3B;My door. Seagram's, poured, not drunk. Three messages blinking. I didn't play them.
~ resolve -= 1
~ hurt(1)
-> back_out

= back_out
You step back out into the Harlans' hall and close the door of 3B. The Dymo label catches the light. BRENNICK.
->->

// ------------------------------------------------------------ kitchen
=== kitchen_flash ===
{ diff == calendar:
    -> calendar_1957
}
{ kitchen_flash == 1:
    The beam crosses the kitchen. The table, four places. Behind the table, by the back door, a man is standing with his hands at his sides, very straight, the way you stand in a choir loft.
    The beam shakes. When it steadies he's gone, and the back door is shut, and the deadbolt is turned.
    # shadow:he was practicing
    ~ hurt(2)
- else:
    The kitchen. The table set for four. The back door, bolted from inside. Same as before.
}
->->

= calendar_1957
The calendar on the refrigerator says OCTOBER 1957.
It's the same Halvorsen Hardware calendar, same covered bridge, the paper gone yellow and soft. The handwriting on it isn't June's and it isn't Wes's. It's blocky capitals, a carpenter's pencil, a hand you haven't seen since you were nine years old and you would know anywhere.
MON FELLOWSHIP. TUE CHOIR. THU CHOIR.
The last Thursday of the month is circled twice, hard enough to tear the paper. Written inside the circle:
WALT 3
Walt. Ruth. Cally. Three.
# evidence:ev_walt_calendar;time;Kitchen calendar, 1957;My father's hand. Mon FELLOWSHIP, Tue/Thu CHOIR. Last Thursday circled: "WALT 3".
# note:1957. My father's calendar. Same Fellowship, same choir. He circled the last Thursday in October and wrote 3. Mom took me the morning of that Thursday. He was going to do it that night.
~ hurt(3)
~ evidence += 2
->->

// ------------------------------------------------------------ theories
=== theory_t5 ===
# theory:t5;What is the house showing you?
# slot:whose family;Mine*@ev_own_photo;The Harlans';Nobody's, it is a trick of the light
# slot:the drinking;I drink more than I say*@ev_own_door;I don't drink;Only on weekends, it's under control
# slot:going home;I don't go home either*@ev_own_door;I'm there every Saturday;Paula keeps Nora from me
# hint:This one only clears if you are honest. The photo of the three of you and the fifth door.
The kitchen door. You hold the pen over the pad for a long time. You know what the right answers are. You've known for years.
+ [FILE: File a theory]
    -> theory_result(3)
+ [Keep looking]
    -> hall

=== theory_t6 ===
# theory:t6;What happened in this house, all of it?
# slot:wes did it because;The choir's radio taught him to make room*@ev_fellowship_broadcast;He lost his job;June was leaving him
# slot:before wes there was;My father, Walt Brennick, 1957*@ev_walt_calendar;Nobody;A stranger passing through
# slot:my father didn't finish because;My mother took me away first*@ev_mothers_call;He changed his mind;The police stopped him
# slot:the thing on 1610 wants;Someone who can hear it and not break*@ev_phone_count;To be left alone;Revenge on the mill
# hint:Everything you've found in twelve loops. The 1957 calendar and your mother's call matter here.
The kitchen door. The beam is yellow now, the batteries going. You write it all down. Every word of it. You put your own name in it where it belongs.
+ [FILE: File a theory]
    -> theory_result(4)
+ [Keep looking]
    -> hall

// ------------------------------------------------------------ end of Act I
=== flashlight_end ===
# warp:tabs_normal
# warp:radio_still
# battery:ok
You put the pad away.

You walk to the end of the hall and you stop at the kitchen door, and the phone on the wall behind you rings.

Once.

You walk back up the hall to it. You're not afraid now. You've been afraid for about four hours of a house where it is always 4:20, and you've run out. You pick up the receiver.

Nothing. Not a dial tone, not static. The open sound of a line with someone on it, a great many someones, a whole room of them, breathing very quietly the way people do when they're trying not to laugh at a surprise party.

Then, all of them together, close to your ear, gentle:
# speaker:1610
"We heard you."
# pause:1.5
The line clicks off.

Behind you, the front door opens.

You turn. The doorway is a rectangle of white. Fog, solid as a wall, moving very slowly, from left to right. No porch light. No cruisers. No Okafor at the fender of the Ford with her arms crossed. No Pell at the tape. No tape. No sound at all.

You step out onto the stoop. The door closes behind you, gently, and the lock turns.
# dark:off
# pause:2
-> hush_start
