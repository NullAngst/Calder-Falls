// ============================================================
// Act I: 22 Cobb Road. The loop machinery.
//
// Twelve loops over three chapters. Every loop prints the same hallway
// text, laid out the same, with one phrase changed. Finding that change
// and looking at it is what clears a loop. Every second loop also asks
// for a theory at the kitchen door. A wrong theory, or walking through
// without finding the change, runs the loop again with the house worse.
//
// Chapter 2, loops 1-4: lights on       (act1/lights_on.ink)
// Chapter 3, loops 5-8: lights off      (act1/lights_off.ink)
// Chapter 4, loops 9-12: flashlight only (act1/flashlight.ink)
// ============================================================

LIST hallitem = nothing, photo, clock, phone, bathroom, drawing, hallradio, coats, extradoor, calendar

VAR diff = nothing        // what is different this loop
VAR found = false         // has the player looked at it
VAR tip = nothing         // what 1610 told you to look at this loop
VAR repeats = 0           // times this loop has been run again
VAR encounter_done = false

=== function phase() ===
{ loop <= 4:
    ~ return 1
- else:
    { loop <= 8:
        ~ return 2
    - else:
        ~ return 3
    }
}

=== function diff_for(n) ===
{ n:
- 2: ~ return photo
- 3: ~ return clock
- 4: ~ return phone
- 5: ~ return bathroom
- 6: ~ return drawing
- 7: ~ return hallradio
- 8: ~ return coats
- 9: ~ return extradoor
- 10: ~ return photo
- 11: ~ return phone
- 12: ~ return calendar
- else: ~ return nothing
}

=== function theory_loop() ===
~ return loop == 2 || loop == 4 || loop == 6 || loop == 8 || loop == 10 || loop == 12

=== act1_start ===
~ loop = 1
~ repeats = 0
-> loop_top

=== loop_top ===
~ diff = diff_for(loop)
~ found = false
~ tip = nothing
~ encounter_done = false
{ loop == 1 && repeats == 0:
    -> lights_on_intro
}
{ loop == 5 && repeats == 0:
    -> lights_off_intro
}
{ loop == 9 && repeats == 0:
    -> flashlight_intro
}
-> loop_begin

= loop_begin
# clear
# autosave
# time:16:20
{ phase() == 3:
    # dark:on
}
-> hallway_text ->
-> worse_line ->
{ june_near >= 4 && phase() >= 2:
    -> june_encounter ->
}
-> hall

// The text a player compares loop to loop. Keep every sentence the same
// length and wording within a phase, apart from the one changed phrase.
=== hallway_text ===
{ phase():
- 1:
    The front door is behind you. The hallway runs straight ahead of you, longer than the house is wide, under a ceiling light with a frosted glass shade and a dead moth in it.
    On your left are coat hooks with {diff == coats:four|three} coats on them, then the hall table with a lamp, a framed photo of {diff == photo && loop == 10:the three of you|{diff == photo:the three of them|the four of them}}, and a clock radio, {diff == hallradio:glowing|dark}. Above the table, a wall clock says {diff == clock:3:15|4:20}. Beside it, a beige phone {diff == phone:hangs off its cradle|sits in its cradle}.
    On your right, an arch opens into the living room. Past it, the bathroom door, {diff == bathroom:open an inch|closed}. Then the children's rooms. At the very end of the hall, the kitchen door stands open, and through it you can see the refrigerator with {diff == drawing:two drawings|a drawing} taped to it and a Halvorsen Hardware calendar that says {diff == calendar:OCTOBER 1957|OCTOBER 1986}.
- 2:
    The front door is behind you. The hallway runs ahead of you in the dark, longer than the house is wide. The ceiling light is off. The only light is the gray that comes in around the blinds.
    On your left are coat hooks with {diff == coats:four|three} shapes on them, then the hall table with a dark lamp, a framed photo of {diff == photo:the three of them|the four of them}, and a clock radio, {diff == hallradio:glowing|dark}. Above the table, a wall clock says {diff == clock:3:15|4:20}, if you squint. Beside it, the phone {diff == phone:hangs off its cradle|sits in its cradle}.
    On your right, the arch into the living room is a black square. Past it, the bathroom door, {diff == bathroom:open an inch|closed}. Then the children's rooms. At the very end of the hall, the kitchen door stands open on more dark, and on the refrigerator you can just make out {diff == drawing:two pale squares|one pale square} of paper and the calendar, {diff == calendar:OCTOBER 1957|OCTOBER 1986}.
- 3:
    The front door is behind you. The hallway is gone except for what the flashlight touches. You move the beam and the house comes back in pieces.
    Left: the coat hooks, {diff == coats:four|three} coats. The hall table. The photo of {diff == photo && loop == 10:the three of you|{diff == photo:the three of them|the four of them}}. The clock radio, {diff == hallradio:glowing|dark}. The wall clock, {diff == clock:3:15|4:20}. The phone, {diff == phone:ringing|in its cradle}.
    Right: the arch, black. The bathroom door, {diff == bathroom:open an inch|closed}. The children's doors. {diff == extradoor:Five|Four} doors in all, where there were four. Then the kitchen, far off, the beam barely reaching the refrigerator, the calendar, {diff == calendar:OCTOBER 1957|OCTOBER 1986}.
}
->->

// Something gets worse each time a loop is run again.
=== worse_line ===
{ repeats:
- 0:
    ->->
- 1:
    The house is a little colder than it was.
- 2:
    The furnace has stopped. You did not hear it stop.
- 3:
    Somewhere in the house a woman is breathing, slow, through her mouth.
- else:
    The hallway is longer than it was. You are sure of it now. You could not tell anyone how you are sure.
}
~ hurt(1)
->->

// ------------------------------------------------------------ the hall hub
=== hall ===
# hint:{hall_hint()}
{phase() == 1:What do you look at?|{phase() == 2:What do you look at, in the dark?|Where do you put the light?}}
+ [The coat hooks] -> look_coats -> hall
+ [The framed photo] -> look_photo -> hall
+ [The clock radio] -> look_radio -> hall
+ [The wall clock] -> look_clock -> hall
+ [The phone] -> look_phone -> hall
+ [The living room] -> look_living -> hall
+ [The bathroom door] -> look_bathroom -> hall
+ [The children's rooms] -> look_kids -> hall
+ {diff == extradoor || (look_extradoor && phase() == 3)} [The fifth door] -> look_extradoor -> hall
+ [RADIO:1610: The voice at the top of the dial] -> act1_1610 -> hall
+ [POLICE: Call Okafor] -> act1_okafor -> hall
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> hall
+ {nerve < 6} [Sit down a minute] -> rest -> hall
+ [Walk to the kitchen door at the end] -> end_door

=== function hall_hint() ===
{ loop == 1:
    ~ return "Look around as much as you like. When you are ready, walk to the kitchen door at the end."
}
{ theory_loop():
    ~ return "Something in the hallway text is different from last time. Find it and look at it. At the kitchen door you will file a theory; the options come from what you have found."
}
~ return "One thing in the hallway text is different from last time. Compare the description, then look at whatever changed."

=== function mark_found(item) ===
{ diff == item && not found:
    ~ found = true
    ~ evidence += 1
    { tip == item:
        ~ attunement += 1
    }
}

// ------------------------------------------------------------ items
// Each item hands off to the chapter that owns the current phase.

=== look_coats ===
{ phase():
- 1: -> coats_on ->
- 2: -> coats_off ->
- 3: -> coats_flash ->
}
~ mark_found(coats)
->->

=== look_photo ===
{ phase():
- 1: -> photo_on ->
- 2: -> photo_off ->
- 3: -> photo_flash ->
}
~ mark_found(photo)
->->

=== look_radio ===
{ phase():
- 1: -> radio_on ->
- 2: -> radio_off ->
- 3: -> radio_flash ->
}
~ mark_found(hallradio)
->->

=== look_clock ===
{ phase():
- 1: -> clock_on ->
- 2: -> clock_off ->
- 3: -> clock_flash ->
}
~ mark_found(clock)
->->

=== look_phone ===
{ phase():
- 1: -> phone_on ->
- 2: -> phone_off ->
- 3: -> phone_flash ->
}
~ mark_found(phone)
->->

=== look_living ===
{ phase():
- 1: -> living_on ->
- 2: -> living_off ->
- 3: -> living_flash ->
}
->->

=== look_bathroom ===
{ phase():
- 1: -> bathroom_on ->
- 2: -> bathroom_off ->
- 3: -> bathroom_flash ->
}
~ mark_found(bathroom)
->->

=== look_kids ===
{ phase():
- 1: -> kids_on ->
- 2: -> kids_off ->
- 3: -> kids_flash ->
}
->->

=== look_extradoor ===
-> extradoor_flash ->
~ mark_found(extradoor)
->->

// ------------------------------------------------------------ the end of the hall
=== end_door ===
{ diff == drawing || diff == calendar:
    // the change is in the kitchen itself: reaching it counts as looking
    -> kitchen_look ->
    ~ mark_found(diff)
}
{ theory_loop():
    -> theory_gate
}
{ loop > 1 && not found:
    -> missed
}
-> advance

= missed
You walk down the hall to the kitchen. You go through the door.

You are standing with your back to the front door. The hallway runs straight ahead of you.

You missed something. You know it the way you know you left the stove on, a cold certainty somewhere under the ribs.
~ repeats += 1
~ june_near = MIN(june_near + 1, 5)
-> loop_top.loop_begin

= theory_gate
{ loop:
- 2: -> theory_t1
- 4: -> theory_t2
- 6: -> theory_t3
- 8: -> theory_t4
- 10: -> theory_t5
- 12: -> theory_t6
}

= advance
~ repeats = 0
{ loop == 4:
    -> lights_on_end
}
{ loop == 8:
    -> lights_off_end
}
{ loop == 12:
    -> flashlight_end
}
~ loop += 1
You walk to the end of the hall and through the kitchen door.

You are standing with your back to the front door. The hallway runs straight ahead of you.
# pause:1.5
-> loop_top

// Shared result of filing a theory. Call with the slot count.
=== theory_result(total) ===
~ partial(theory_score, total)
{ theory_score == total:
    ~ resolve += 1
    -> end_door.advance
}
~ wrong_theories += 1
~ repeats += 1
~ june_near = MIN(june_near + 1, 5)
~ hurt(2)
{ theory_score > 0:
    Some of it was right. You can feel which parts, the way a key feels when it turns halfway and stops.
- else:
    None of it was right. The house knows that before you do.
}
You walk through the kitchen door.

You are standing with your back to the front door. The hallway runs straight ahead of you.
-> loop_top.loop_begin

// ------------------------------------------------------------ radio and police
=== act1_1610 ===
# music_static:0.3
# speaker:1610
{ diff:
- photo: "The picture. Count the picture."
    ~ tip = photo
- clock: "The time. It was always the time."
    ~ tip = clock
- phone: "Pick up. Somebody is counting."
    ~ tip = phone
- bathroom: "She is behind the door. She left it open for you."
    ~ tip = bathroom
- drawing: "The little one drew him. Go and see."
    ~ tip = drawing
- hallradio: "We are already on. Look at us."
    ~ tip = hallradio
- coats: "He hung his robe up like a good boy. Count the coats."
    ~ tip = coats
- extradoor: "There is a door for you. There always was."
    ~ tip = extradoor
- calendar: "Look what year it is."
    ~ tip = calendar
- else: "Traveler. You are expected. Walk to the end."
}
# music_static:0
~ attunement += 1
{ attunement >= 6 && phase() >= 2:
    The voice stops. Under the hiss, a lot of men are breathing in time.
    ~ hurt(1)
}
->->

=== act1_okafor ===
# speaker:police
{ phase():
- 1: "Cal. Copy. You've been in there about two minutes. What've you got?"
- 2: "Cal? Copy. You've been in there about two minutes." A pause. "Is the power out in there? The porch light just went."
- 3: "Cal." Static. "...two minutes. You've been in there two minutes. Cal, I can hear you breathing. Say something."
}
{ diff == nothing:
    You tell her the hallway is long. She tells you to walk it to the end. "Like you do. Slow."
- else:
    { loop:
    - 2: "Walk me through the hall table," she says. "Who's in the photo?"
    - 3: "What time did the neighbor say? Twelve-forty. Check the clocks, Cal. Clocks get knocked." A pause. "And Pell wants you to know the truck radio was jammed all the way up the dial. There's tape on the dash. 1610, dash, 4."
        # evidence:ev_truck_dial;object;Truck radio dial;Needle jammed past the top of the band. Tape on dash: "1610 - 4"
    - 4: "Phone in that house got a call at three fifteen. County pulled the log. Nobody on the other end." Paper rustles. "Truck radio, Cal. Pell says the dial was jammed at the top. Tape on the dash says 1610, dash, 4."
        # evidence:ev_truck_dial;object;Truck radio dial;Needle jammed past the top of the band. Tape on dash: "1610 - 4"
    - 5: "Pell says the bathroom door was locked from the inside. He didn't open it."
    - 6: "Kids draw what's going on at home, Cal. You know that. Look at what they drew."
    - 7: "Pell swears the truck radio came back on by itself after he turned it off. I told him that's not possible."
    - 8: "Coats," she says, and then, "Sorry. I don't know why I said that."
    - 9: "Count the doors, Cal. Mrs. Cuddy says four. Four doors off that hall."
    - 10: "That photo on the hall table. Cal. Who's in it now?"
    - 11: "Answer the phone, Cal. It's ringing. I can hear it from out here." She sounds afraid. You have never heard her sound afraid.
    - 12: "What year is it, Cal?" she asks, and then the band goes quiet before you can tell her.
    }
}
~ steady(1)
->->

// ------------------------------------------------------------ June
=== june_encounter ===
{ encounter_done:
    ->->
}
~ encounter_done = true
# music:june
# hint:She hunts by sound. Being still and quiet is safer than running. Looking at her costs you.
{phase() == 3:Something stands at the far end of the beam, where the light gives out.|There is someone at the end of the hall, in the kitchen doorway, where it is darkest.}
A woman, or the shape a woman leaves in a doorway when she has stood in it every day for fifteen years. Her head is tilted, listening. Her hair is wet. # timed:7:2
{&She has not seen you.|She turns her head a quarter inch toward the sound of your watch.|She takes one step. The floor does not creak. Floors creak in this house. You have heard them.|She is closer than she was a second ago, and she has not moved.}
+ [Hold still. Don't breathe.]
    You hold still. You do not breathe. Your lungs start to burn and you keep not breathing.
    June listens to the house for a long time. Then she goes into the kitchen, and the kitchen door swings shut behind her, slow, the way a door does when there is no one behind it.
    ~ june_near = MAX(june_near - 2, 0)
    ~ hurt(1)
+ [Duck into the living room and hide]
    You step through the arch, sideways, into the dark of the living room, and press your back to the wall beside it.
    Wet footsteps come up the hall. They stop at the arch. You can hear water dripping onto the carpet, a slow tick, tick, a foot from your shoulder.
    They move on.
    ~ june_near = MAX(june_near - 1, 0)
    ~ hurt(2)
+ [Run for the front door]
    You turn and grab the knob and it turns and the door opens and you are standing with your back to the front door, looking down the hallway.
    She is much closer now.
    ~ hurt(3)
    ~ resolve -= 1
+ [Look at her face]
    You look.
    You will not remember afterward what you saw. You will remember that you saw it, and that her mouth was moving, and that she was counting.
    ~ hurt(4)
    ~ attunement += 1
    # warp:title_count:4
+ [Listen]
    You listen.
    She is saying something, under the dripping. "Danny. Beth. Danny. Beth. Danny. Beth." Over and over. Not counting. Calling them. Calling them like they are out in the yard and it is getting dark.
    ~ mercy += 1
    ~ hurt(1)
-
# music:cobb_road
{ nerve == 0:
    -> black_out
}
->->

=== black_out ===
# fourth:crash
The hallway tips over sideways, very slowly, like a picture falling off a nail.
# pause:2
You come to on the carpet with your cheek against the plastic runner. You don't know how long. Your watch says 4:20.
~ nerve = 4
~ resolve -= 1
~ repeats += 1
-> loop_top.loop_begin
