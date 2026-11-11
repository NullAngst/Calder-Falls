// ============================================================
// Chapter 6. Act II: the Pruitt house, 14 Kessler Lane. A small loop
// in the Bleed. Dale Pruitt killed his mother and brother in March of
// 1985 and was found alive. The Counted stand where people sat.
// ============================================================

VAR pruitt_loop = 0
VAR pruitt_found = false

=== pruitt_house ===
# chapter:6:The Pruitt house
# map:pruitt
# theme:fog
# music:the_hush
# hint:A smaller loop: three passes through the house. Each pass, one of the Counted is somewhere new. Find it, hear its number, find what changed.
{ pruitt_house > 1:
    -> pruitt_again
}
Kessler Lane is a dead end off the county road behind the Agway, five houses and a turnaround. Number 14 is a ranch with green asbestos shingles, a carport, and a chain-link fence with a BEWARE OF DOG sign and no dog.

You read the file. March of 1985. Dale Pruitt, twenty-six. Laid off with the second wave. Lived here with his mother Irene, fifty-eight, a seamstress who did alterations for half the town out of the back bedroom, and his brother Gary, nineteen, who worked at the Agway and was going to start at the community college in Hollis in the fall.

Dale did it on a Tuesday, the file says. Choir night. A neighbor found him on the sixth day, sitting at the kitchen table in a clean shirt with his hands folded, looking at the radio. He hadn't eaten. He hadn't slept, as far as anyone could tell. He said one thing to the county officers, and he said it over and over in the ambulance and he's still saying it, they say, at the state hospital in Ardell.

"I'm still holding it."
# evidence:ev_pruitt_file;statement;Pruitt file;Dale Pruitt, 26. Mother Irene, brother Gary. Found on the 6th day at the kitchen table. "I'm still holding it."
~ evidence += 1
-> pruitt_door

= pruitt_again
The Pruitt house on Kessler Lane. The carport. The fence. The sign with no dog.
-> pruitt_door

= pruitt_door
+ [Go in] -> pruitt_enter
+ {cigarettes > 0} [Smoke a cigarette first] -> smoke -> pruitt_door
+ [Not yet. Back to the car.] -> hush_hub

=== pruitt_enter ===
# theme:bleed
# music:listening_room
# warp:cursor_needle
~ pruitt_loop = 1
-> pruitt_top

=== pruitt_top ===
~ pruitt_found = false
# clear
# autosave
-> pruitt_text ->
-> pruitt_rooms

=== pruitt_text ===
The front door is behind you. The house is small, a hall no longer than a man lying down, and wet, every surface beaded like the inside of a car on a cold morning. The hum is in the walls here too.
To your right, the kitchen, where a radio sits on the table. Straight ahead, Irene's sewing room, the door {pruitt_loop == 2:open|shut}. To your left, Gary's room, the door {pruitt_loop == 3:open|shut}. Above the kitchen table there is a calendar, {pruitt_loop == 1:with a woman standing in front of it|MARCH 1985}.
->->

=== pruitt_rooms ===
# hint:The changed thing this pass: {pruitt_loop == 1:something in front of the kitchen calendar.|{pruitt_loop == 2:the sewing room door.|Gary's door.}}
+ [The kitchen] -> pruitt_kitchen
+ [Irene's sewing room] -> pruitt_sewing
+ [Gary's room] -> pruitt_gary
+ [RADIO:1610: The radio on the kitchen table] -> pruitt_radio -> pruitt_rooms
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> pruitt_rooms
+ [Go back out the front door] -> pruitt_exit

=== pruitt_kitchen ===
{ pruitt_loop == 1 && not pruitt_found:
    -> counted_irene
}
The kitchen table, two chairs pushed in and one pulled out. A clock radio on the table, the same almond GE as the one on the Harlans' hall table, the same gold sticker. WE ARE GLAD YOU SAID YES.
A plate with a sandwich on it, dried to cardboard. Six days of mail on the floor under the slot, fanned out where it fell.
{ pruitt_kitchen == 1:
    # evidence:ev_pruitt_kitchen;object;Pruitt kitchen;Same GE clock radio, same gift sticker. Six days of mail under the slot.
    ~ evidence += 1
}
-> pruitt_rooms

= counted_irene
There is a woman standing in front of the calendar.

She is not a woman. She is the shape a woman leaves behind when she has stood in one place every morning for thirty years, pinning up a hem or reading the date, and then stopped. She is the right height. She has the right stoop. She is gray, all of her, the gray of television snow, and up close you can see it moving inside her, churning, the way snow does on a set with no station.

This is one of the Counted. Nobody had to tell you. You knew the word as soon as you saw her, the way you know a word in a dream.

Her face is turned to the wall. She is speaking, softly, steadily, the way you'd say a rosary.
# speaker:1610
"Three. Three. Three. Three."
# evidence:ev_counted;photo;One of the Counted;A gray shape where Irene Pruitt stood every morning. Static inside. Says "three."
~ pruitt_found = true
~ evidence += 1
~ hurt(2)
+ [Keep your head down and back away]
    You keep your head down. You back away. She keeps counting to the wall.
    ~ resolve += 1
+ [Say your own number to her]
    "One," you say.
    She stops. Her head begins to turn, the snow inside her swirling faster, and you get out of the kitchen before it finishes turning.
    ~ attunement += 1
    ~ hurt(2)
+ [Touch her shoulder]
    You put your hand on her shoulder. There is nothing there, and the nothing is cold, and it holds on to your hand for a second longer than nothing should.
    ~ hurt(3)
    ~ mercy += 1
- -> pruitt_rooms

=== pruitt_sewing ===
{ pruitt_loop == 2 && not pruitt_found:
    -> sewing_open
}
{ pruitt_loop < 2:
    The sewing room door is shut. From behind it, the rattle of a treadle machine, running fast, running with nobody's foot on it.
- else:
    The sewing room. The Singer, the dress form, the jars of buttons. Same as before.
}
-> pruitt_rooms

= sewing_open
The sewing room door is open.

Irene Pruitt's back bedroom: a black Singer treadle machine under the window, a dress form, jars and jars of buttons on shelves sorted by color, a corkboard of paper patterns. A man's suit jacket is on the dress form, half-altered, the sleeves pinned. Gary's, for the community college interviews in Hollis. The pins are still in.

The dress form is wearing a Counted. You can see it from the doorway, the snow churning under the jacket, a young man's shoulders. It isn't facing the wall. It's facing the door. It's facing you.
# speaker:1610
"Two," it says, in Gary Pruitt's nineteen-year-old voice. "Two. Two. Two."
On the corkboard, between the patterns, someone has written on the wall itself, in pencil, in small careful letters going round and round the board in a spiral, the same line hundreds of times.
I HELD IT SIX DAYS I HELD IT SIX DAYS I HELD IT SIX DAYS
# evidence:ev_pruitt_wall;object;Sewing room wall;In pencil, in a spiral around the patterns, hundreds of times: "I HELD IT SIX DAYS."
# evidence:ev_pruitt_sewing;photo;Irene's sewing room;Gary's jacket on the dress form, pins in. A Counted inside it, says "two."
# note:Pruitt. Dale wrote I HELD IT SIX DAYS round and round the sewing room wall. Six days before the neighbor came. He held it. Held WHAT for six days? And he's still holding it, at Ardell.
~ pruitt_found = true
~ evidence += 2
~ hurt(2)
-> pruitt_rooms

=== pruitt_gary ===
{ pruitt_loop == 3 && not pruitt_found:
    -> gary_open
}
{ pruitt_loop < 3:
    Gary's door is shut. Taped to it is a pennant from the community college in Hollis, still shiny, never used.
- else:
    Gary's room. The college catalog on the desk, the pages dog-eared. The chair. Same as before.
}
-> pruitt_rooms

= gary_open
Gary's door is open.

A boy's room that got stopped at the edge of being a man's room. A poster of a Camaro. A rack of cassettes. A desk with the Hollis Community College catalog open on it, the pages dog-eared at Drafting, at Accounting, at Electronics, as if he couldn't decide and didn't think he'd have to for a while.

There's a chair in the middle of the floor, a kitchen chair, carried in here and set down facing the window. Nobody's in it. Nothing's in it, not even a Counted. That's what's wrong. It's the only chair in this house without one.

On the seat, folded small, a sheet of ruled paper torn from a ledger book, the kind with the red and blue lines and the columns. One entry, in neat librarian's printing.

PRUITT, D. Brought in Feb '85. Made room March. Held six days. Still holding at Ardell. Not suitable: will not let go. Note: the strong ones keep it and keep it from us.
# evidence:ev_pruitt_page;statement;Ledger page, Gary's chair;"PRUITT, D. Held six days. Still holding at Ardell. Not suitable: will not let go. The strong ones keep it and keep it from us."
# note:Ledger page. Dale is STILL HOLDING something at Ardell and won't let go and that makes him NOT SUITABLE. They don't want a man who holds it. They want a man who holds it and hands it over? Who LETS it out?
~ pruitt_found = true
~ evidence += 2
~ hurt(1)
-> pruitt_rooms

=== pruitt_radio ===
# speaker:1610
# music_static:0.4
{&"He is so selfish, the Pruitt boy. He took one of us and he will not share. Six days, and then a locked ward, and still he holds on, and we cannot get out."|"You could go to Ardell, traveler. Your mother is there. So is Dale. You could ask him to let go. He would listen to a policeman."|"Three. Two. One. Count with us. It's easy."}
# music_static:0
~ attunement += 1
->->

=== pruitt_exit ===
{ not pruitt_found:
    You go back out the front door.

    You are standing with your back to the front door, inside. The hall no longer than a man lying down.

    You missed it.
    ~ hurt(1)
    -> pruitt_top
}
{ pruitt_loop < 3:
    ~ pruitt_loop += 1
    You go out the front door, and you are standing inside it again, with the hall in front of you, and the hum in the walls is a little louder.
    -> pruitt_top
}
-> pruitt_theory

=== pruitt_theory ===
# theory:pruitt;What happened in the Pruitt house, and what is Dale holding?
# slot:dale made room by;Killing his mother and his brother*@ev_pruitt_sewing;Moving out;Selling the house
# slot:dale is now;Alive, at the state hospital in Ardell*@ev_pruitt_file;Dead;Missing
# slot:dale held it;Six days, and he still won't let it go*@ev_pruitt_wall;One night;He never had it
# slot:the ledger wants;Someone who takes it and lets it out*@ev_pruitt_page;Someone who keeps it locked up;Nobody, it's random
# hint:The file, the sewing room wall, and the page on Gary's chair.
The front door. You stand with your hand on the knob. Three passes. You take out the pad.
+ [FILE: File a theory]
    -> pruitt_result
+ [Go round again]
    -> pruitt_top
+ [Leave the house for now]
    You go out, and this time the door lets you. Kessler Lane. The fog. The house will start over when you come back.
    -> hush_hub

=== pruitt_result ===
~ partial(theory_score, 4)
{ theory_score < 4:
    ~ wrong_theories += 1
    ~ hurt(2)
    Not all of it. The hum in the walls goes up a step, like someone turning a dial.
    -> pruitt_top
}
# theme:fog
# warp:cursor_normal
# music:the_hush
You open the front door, and it's Kessler Lane. The fence. The carport. The fog.

Behind you, in the house, the treadle machine stops. The counting stops. In the quiet you can hear, very faint, someone crying, a young man, the way you cry when you're exhausted and something has finally stopped hurting.

The house is just a house. Somebody should sell it. Nobody will.
# note:Pruitt house closed. Dale took the thing in and HELD it. The ledger calls that a failure. The Ledger isn't trying to kill families. Killing families is what happens when it fails. They want something to come THROUGH a man.
~ pruitt_closed = true
~ houses_closed += 1
~ resolve += 1
~ evidence += 1
-> hush_hub
