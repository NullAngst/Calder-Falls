// ============================================================
// Chapter 12. Act IV: the mill floor. The Ledger's book in the mill
// office, where Margaret Lusk stops being kind. Then the full choir,
// singing a Kept through into whoever they have.
// ============================================================

=== mill_floor_start ===
# chapter:12:The mill floor
# theme:dead_signal
# music:mill_floor
# time:23:59
# fourth:howto
# warp:title_count:1
# hint:Read the ledger. Then go to the floor. What you have done all day decides what you can do there.
The mill office is a brick box at the head of the yard with OFFICE in gold leaf on the door glass. The key turns.

Inside: a counter, a time clock, a rack of punch cards with names on them, every card punched in at 11:59 tonight. Behind the counter, a private office with a frosted glass door. PLANT MANAGER, it said once. Somebody has scraped that off and painted, in neat librarian's printing, PRECENTOR.

Margaret Lusk is sitting behind the desk.

She's taken off the cardigan. She's wearing a black robe with a red stole, like the men, and the pearl treble clef is pinned to the stole. There's a big book open on the desk in front of her, a real ledger, cloth-bound, the corners worn round, the kind a hardware store used to keep accounts in.

"Sergeant," she says. Not Cal. "You came."
-> ledger_office

=== ledger_office ===
+ [Read the ledger] -> ledger_read_it
+ {ledger_read_it} [Arrest her] -> arrest_lusk
+ {ledger_read_it && rounds > 0} [Shoot her] -> shoot_lusk
+ {ledger_read_it} [Walk past her to the floor] -> floor

= ledger_read_it
~ ledger_read = true
She turns the book around and pushes it across the desk to you. She wants you to read it. She's been waiting for somebody to read it for thirty years.

Columns ruled in red and blue. NAME. BROUGHT IN. HOUSEHOLD. MADE ROOM. HELD. NOTES.

The first page, spring 1957. The first line.

BRENNICK, Walter J. March '57. Household 3. Wife removed the son, October. Failed to make room. Held 0. Unsuitable. Note: grief deep, will shallow. Took him in for the grief. Wanted him for the son.

You read it twice. You read the last part three times.

You turn the pages. Szymanski. Ostrowski. Haney. Kowal. Tamsin, Frank: held four years, would not let it out, died with it. Very nearly. Pruitt. Dorsey. Harlan. Tolliver, Raymond, the newest, the ink still bright. Every entry ends the same way. Unsuitable. Unsuitable. Unsuitable.

And in the margin beside each name, in smaller writing, in the same hand, a second column nobody ruled. Short notes. Wife sickly. Drinks. Beat his brother as a boy. Lost a child in '72. Son is slow. Owes the bank. Grief deep, will shallow. Will break.

She didn't pick the strong ones. She picked the ones who'd break. She looked for the cracks, and she wrote them down, and then she brought them a radio.

"Broken men say yes," Margaret Lusk says, watching you read. "Whole men say no. I've tried whole men. They just say no, Sergeant, and go home to their suppers. So I take the broken ones, and I give them the best thing that will ever happen to them, and most of them can't hold it." She folds her hands. "I knew what would happen to the families. Of course I knew. I'm not a fool. I wrote it down every time. It was necessary. It is necessary. One day one of them will hold it, and then none of it will have been for nothing."

"You wanted me," you say. "Not him. Me."

"I wanted the son," she agrees. "Ruth took you away before you were old enough to say yes. So I waited." She smiles, and there is nothing kind in it now, and you understand that there never was, that kindness was the thing she wore to Fellowship, like the cardigan. "Twenty-nine years. You held a house and never went in. You hold everything, Sergeant. Your wife. Your daughter. Your drink. You hold it all at arm's length and you never let a bit of it in. You are a room with nothing in it. You are the best vessel I have ever seen."

There's one line left at the bottom of the last page. It has a name in it already, and a date, today's. The other columns are blank.

BRENNICK, Calvin W. October '86. Household 1.
# evidence:ev_ledger;statement;The Ledger;Every man since 1957, graded "unsuitable." A second column: their cracks. Walt: "Wanted him for the son." Last line: BRENNICK, Calvin W. October '86. Household 1.
# note:She picked the BROKEN ones on purpose. She wrote down their cracks. She knew what they'd do to their families and she wrote it down. She wanted me since 1957. The last line in the book is mine.
~ evidence += 4
~ hurt(3)
-> ledger_office

= arrest_lusk
"Margaret Lusk, you're under arrest."

You come around the desk and take her by the arm and she lets you. She's very light. You get the cuffs out. She holds her wrists together for you, like she's done this before, like she's been looking forward to it.

"For what, dear?" she asks. "Leading a choir?"

The cuffs close. She's still smiling. Out on the mill floor, the singing gets louder.

"It doesn't matter where I am," she says. "It never mattered. I'm only the one who keeps the book." She looks past you, at the frosted door. "Go and see. They've started without me."

You cuff her to the radiator. She sits down on the floor beside it and arranges her robe over her knees.
~ resolve += 2
~ evidence += 1
-> floor

= shoot_lusk
You draw.

Margaret Lusk looks at the pistol with polite interest, like it's a book somebody's recommended to her.

"Go on," she says. "Walter wanted to, at the end. He didn't have the strength either."
+ [Fire]
    You fire. She goes back in the chair and doesn't make a sound, and the ledger on the desk in front of her takes the blood on its open page, over your name.
    The singing on the mill floor doesn't stop. It doesn't even falter.
    You stand there with the gun. It didn't change anything. You knew it wouldn't. You did it anyway.
    # theme:dead_signal
    ~ rounds -= 1
    ~ shot_person = true
    ~ mercy -= 10
    ~ resolve -= 2
    ~ hurt(4)
+ [Lower the gun]
    You lower it.
    "No," Margaret Lusk says, almost disappointed. "No, I didn't think so."
    ~ resolve += 1
- -> floor

=== floor ===
# music:mill_floor
# music_static:0.3
# hint:Whoever stands in the middle is the vessel. You can take their place.
{ ray_lost:
    ~ vessel = "ray"
}
{ vessel == "" && jo_with_you && not jo_saved:
    ~ vessel = "jo"
}
{ vessel == "":
    ~ vessel = "you"
}
The machine room is the size of a cathedral and built like one: brick piers, steel trusses, a roof of sawtooth skylights black with night. The paper machine runs down the middle of it, two hundred feet of rollers and dryers and felts, dead since April of 1985, rusting quietly.

The choir stands in front of it. All of them, the living Ledger men in their robes, in rows, their faces snow. Along the walls, all the way around the room, standing shoulder to shoulder in their gray churning hundreds, the Counted. Every family. Every house. June Harlan and her children are at the front, near the door, where you'll see them. Amy and Joel Dorsey are holding hands.

The singing is the hymn from St. Adalbert's, the ledger-line hymn, and it's enormous now, and it isn't numbers any more. It's a word you don't know, in a language that hasn't been spoken by anything with a throat, and it's being sung at a point in the middle of the floor, where the light from the skylights would fall if there were any light.

{ vessel:
- "ray": Ray Tolliver is standing there. Not in his robe. In his shirtsleeves, the way he was at the bar. His shirt is dark down the front. He went home. You were at the library, and he went home, and now he's here, and he's holding his arms out from his sides like a man being measured for a suit, and something is coming down into him out of the dark, and he is failing to hold it. You can see it. He's cracking like a plate.
- "jo": Jo Tamsin is standing there. She walked in ahead of you and nobody stopped her. She's singing with them, eyes closed, her shotgun on the floor at her feet. Something is coming down into her out of the dark, and her face is calm, and she is going to hold it four years, like her father, and then she is going to go to sleep.
- else: Nobody is standing there. There's an empty space on the concrete, a circle the size of a man, where the dust has been swept away. They've kept it for you. They've kept it for twenty-nine years.
}
-> the_floor_choice

=== the_floor_choice ===
+ {vessel != "you"} [Walk into the middle and take {vessel == "ray":Ray's|Jo's} place] -> take_place
+ {vessel != "you"} [Pull {vessel == "ray":Ray|Jo} out of the circle] -> pull_out
+ {vessel == "you"} [Walk into the circle] -> into_circle
+ [Say your number] -> say_number
+ [RADIO:1610: Listen to what they're really singing] -> floor_1610 -> the_floor_choice
+ {not floor_1610} [Turn and walk out @@ Listen to what they're really singing] -> floor_1610 -> the_floor_choice

= take_place
You walk out across the floor through the singing, and it's like wading into a river, the sound pushing at you, and you get to the middle and put your hand on {vessel == "ray":Ray's shoulder|Jo's arm} and pull, gently, the way you'd lead somebody off a ledge.

{ vessel == "ray":
    Ray comes. He stumbles out of the circle and goes down on his knees on the concrete and puts his hands over his face. Whatever was coming into him lets go, and turns, the way a dog turns its head.
    ~ ray_lost = false
    ~ mercy += 3
- else:
    Jo comes. She opens her eyes in the middle of a note and the note stops in her throat and she looks at you like she's never seen you, and then like she has. She picks up her shotgun. She backs away to the wall, by June Harlan's children.
    ~ jo_saved = true
    ~ mercy += 3
}
You're standing in the circle now.
~ vessel = "you"
-> into_circle

= pull_out
{ vessel == "ray":
    You grab Ray by the belt and drag him backwards out of the circle. He's heavy. He doesn't fight. He goes down on the concrete and lies there.
    The choir doesn't stop singing. The thing in the dark doesn't stop coming. It only needs a place to come down. There's one man left on the floor who doesn't have a family to make room from.
    ~ ray_lost = false
    ~ mercy += 2
- else:
    You take Jo by both shoulders and walk her backwards out of the circle, and she comes, still singing, and you put her against the wall by June Harlan's children and hold her there until her voice runs down.
    ~ jo_saved = true
    ~ mercy += 2
}
~ vessel = "you"
Then the choir turns, all of them, every robe, every snowing face, and looks at you.
-> into_circle

= say_number
"One," you say, out loud, into all that singing.

The choir stops.

Every face in the room turns to you. Every one of the Counted along the walls. In the silence you can hear the river, outside, and the ticking of the dead machine as it cools.

And then the whole room, all of them, gently, together, the way they said it on the phone:
# speaker:1610
"We heard you."
~ attunement += 3
~ vessel = "you"
-> into_circle

= floor_1610
# speaker:1610
# music_static:0.7
"We are not singing anything, Cally. We are asking. Please. Please. We have been where nothing ends for so long. Please let us in. We will be so quiet. We will only be in the radios. We will only be in the phones. You will hardly know we're there. Please. Please. Please."
# music_static:0.3
~ attunement += 2
~ mercy += 1
-> the_floor_choice

=== into_circle ===
# music_layer:drums off
# music_detune:-40
# warp:flinch
You stand in the circle.

It comes down.

There isn't a word for it. You'll try, later, if there's a later, and you won't find one. It's like a radio station coming in, at night, from very far away, when you've been turning the dial for an hour through static, and suddenly there's a voice, clear, in the room with you. It's like that, if the voice were a nation. If the voice had been waiting longer than there have been people.

They're so lonely. That's the first thing. They are so lonely, and they are so many.

And there's room. Margaret Lusk was right about that. There's so much room in you. You've kept it empty for twenty-nine years. They could all come in.
# hint:This is the end of the game. What you can do here comes from everything you did: how you held up, who you saved, what you built, how much you listened.
-> final_choice
