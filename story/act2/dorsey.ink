// ============================================================
// Chapter 7. Act II: the Dorsey house, 6 Birch Street. December 14th,
// 1985. Lyle Dorsey, two children. Ada was on night shift. The
// Christmas lights are still on.
// ============================================================

VAR dorsey_loop = 0
VAR dorsey_found = false
VAR kicked_in = false
VAR ada_home = false

=== dorsey_house ===
# chapter:7:The Dorsey house
# map:dorsey
# theme:fog
# music:the_hush
# hint:{ada_trusts:Ada's key opens the back door.|Without Ada's key you will have to kick in the chained front door. Ada at the hospital will give you the key if you tell her the truth.}
{ dorsey_house > 1:
    -> dorsey_again
}
Birch Street is the nice street, or it was: brick ranches with picture windows, put up in 1962 for the mill's shift supervisors, each with a two-car garage and a maple in the front yard. Number 6 is the one with the Christmas lights.

Ten months later, they're still on. Big old-fashioned bulbs, red and green and blue and orange, strung along the gutter and around the picture window and wound up the trunk of the maple. In the fog they make soft colored halos, like streetlights in the rain. Somebody's been paying the electric on this house too.

There's a chain across the front door, a real chain, through the storm door handle and around the porch post, padlocked. Ada said she chained it. She didn't say she'd be the one paying the electric.
-> dorsey_door

= dorsey_again
The Dorsey house on Birch Street. The lights in the fog. The chain on the front door.
-> dorsey_door

= dorsey_door
+ {ada_trusts} [Go around back and use Ada's key] -> dorsey_back
+ {not ada_trusts} [Kick the front door in] -> dorsey_kick
+ {not ada_trusts} [Go back to the hospital and talk to Ada first] -> hospital
+ [Not yet. Back to the car.] -> hush_hub

= dorsey_back
You go around by the garage. The back door has a window with a gingham curtain. Ada's key turns in the lock like it's been oiled.

The kitchen smells like pine needles and cinnamon and something burnt a long time ago.
~ steady(1)
-> dorsey_enter

= dorsey_kick
You don't bother with the chain. You go to the side of the porch where the picture window is and you put your heel into the wood of the door frame beside the lock, the way they teach you, and it takes four tries.

The frame splinters inward in long pale strips. You know exactly what that looks like from the inside. You saw it in the Harlans' bathroom.

Behind you, on Birch Street, every Christmas bulb on every house goes out at once, and comes back on.
~ kicked_in = true
~ mercy -= 1
~ hurt(3)
-> dorsey_enter

=== dorsey_enter ===
# theme:bleed
# music:listening_room
# warp:cursor_needle
~ dorsey_loop = 1
-> dorsey_top

=== dorsey_top ===
~ dorsey_found = false
# clear
# autosave
# time:22:00
-> dorsey_text ->
-> dorsey_rooms

=== dorsey_text ===
You are standing in the Dorsey kitchen. The clock on the stove says ten o'clock. A wet green smell of pine. The hum is in the walls, and the Christmas lights outside the window blink in a slow pattern that is not random.
Through the arch, the living room and the tree, {dorsey_loop == 1:with two small shapes sitting under it|lit, the presents stacked under it}. The phone on the kitchen wall, {dorsey_loop == 2:with a tall shape standing at it|in its cradle}. Down the hall, the children's room, the door {dorsey_loop == 3:open|shut}.
->->

=== dorsey_rooms ===
# hint:The changed thing this pass: {dorsey_loop == 1:under the tree.|{dorsey_loop == 2:the phone.|the children's room.}}
+ [The living room and the tree] -> dorsey_tree
+ [The phone on the kitchen wall] -> dorsey_phone
+ [The children's room] -> dorsey_kids
+ [RADIO:1610: The radio on the windowsill] -> dorsey_radio -> dorsey_rooms
+ [POLICE: Call it in] -> dorsey_police -> dorsey_rooms
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> dorsey_rooms
+ {dorsey_loop < 3} [Go back out the door you came in] -> dorsey_exit
+ {dorsey_loop == 3} [Go back out the door you came in @@ Go back to the children's room] -> dorsey_kids

=== dorsey_tree ===
{ dorsey_loop == 1 && not dorsey_found:
    -> tree_counted
}
The tree, a real Scotch pine, gone brown and bare in places, the needles in a ring on the carpet. The ornaments are the kind kids make in school: paper chains, a pinecone painted gold, a clothespin reindeer. The presents underneath are wrapped in the Sunday comics. Two stockings on the mantel, AMY and JOEL in glitter glue.
{ dorsey_tree == 1:
    # evidence:ev_dorsey_tree;photo;The Dorsey tree;Ten months up. Presents wrapped in the funnies, never opened. Stockings: AMY, JOEL.
    ~ evidence += 1
}
-> dorsey_rooms

= tree_counted
There are two Counted sitting under the tree.

Small ones. Children-sized, cross-legged, the way you sit on Christmas morning when you've been told not to touch anything until Daddy has his coffee. The snow churns inside them, faster than in the grown ones, like they can't sit still even now.

They aren't counting. They're whispering to each other. You crouch, and you listen.
# speaker:1610
"Is Mom coming?"
# speaker:1610
"She's at work."
# speaker:1610
"Daddy said four."
# speaker:1610
"Daddy said we're three without Mom. Daddy said three isn't enough. Daddy said he's short."
# evidence:ev_dorsey_children;statement;Under the tree;Two small Counted. "Daddy said four." "Three isn't enough. He's short."
# note:Dorsey kids under the tree: Lyle counted FOUR with Ada. Ada wasn't home. He was "short." He did it anyway, three instead of four, and it went wrong. Short one.
~ dorsey_found = true
~ evidence += 1
~ mercy += 1
~ hurt(2)
+ [Tell them their mother is all right]
    "Your mom's okay," you say. "She's at the hospital. She's working. She's okay."
    The whispering stops. The snow inside them slows, and slows, and for a second, you'd swear to it, the smaller one leans against the bigger one, the way kids lean when they're falling asleep in the car.
    ~ mercy += 2
    ~ steady(1)
+ [Back away]
    You back away. They go on whispering. You can hear them all the way to the kitchen.
- -> dorsey_rooms

=== dorsey_phone ===
{ dorsey_loop == 2 && not dorsey_found:
    -> phone_counted
}
The phone in its cradle. A yellow wall phone, a long cord. Beside it a list in Ada's hand: HOSP 3RD FL NIGHT DESK, and the number.
-> dorsey_rooms

= phone_counted
There is a tall Counted standing at the phone.

A man. Broad, a little stooped. He has the receiver in his hand, held to where his ear would be, and the snow is churning in his head so fast it's almost white.
# speaker:1610
"Hey, babe," he says, and it is a man's voice, warm, ordinary. "Yeah. They're asleep. Yeah." A pause. "Four." Another pause. "Nothing. I'm practicing."
He hangs up the phone. He stands with his hand on it. Then he says, quieter, not into the phone:
# speaker:1610
"I'm short. I'm short one. She said four and I'm short one."
On the counter by the phone, under a magnet, there's a ruled page torn out of a ledger.
DORSEY, L. Brought in April '85. Made room December. Counted four, house held three. Short. Went bad within the hour. Unsuitable.
# evidence:ev_dorsey_page;statement;Ledger page, Dorsey kitchen;"DORSEY, L. Counted four, house held three. Short. Went bad within the hour. Unsuitable."
# note:Dorsey ledger page. Lyle counted four, the house held three because Ada was at work. "Short." It went bad in an HOUR. Pruitt held it six days. They grade them like a cattle auction.
~ dorsey_found = true
~ evidence += 2
~ hurt(2)
-> dorsey_rooms

=== dorsey_kids ===
{ dorsey_loop == 3 && not dorsey_found:
    -> kids_open
}
{ dorsey_loop == 3:
    -> exit_after_kids
}
The children's room door is shut. Taped to it, a construction-paper sign: AMY AND JOEL'S ROOM, KNOCK FIRST.
You knock, before you can stop yourself. Nobody answers. It's the right thing to have done anyway.
-> dorsey_rooms

= kids_open
The door is open.

Twin beds, matching quilts, a lamp shaped like a carousel that turns when it's lit. It's lit. Horses go round on the ceiling.

The beds are made. The quilts are pulled up tight. There's nothing in them and nothing on them and no Counted anywhere, and the carousel turns, and on Amy's pillow there's a nurse's cap, white, with a black stripe, laid there carefully, like a present.

Ada's cap. The one she's wearing on the third floor. The one she's always wearing.

She's been here. She comes home. She comes home every morning at seven-thirty, and walks up the path, and the lights are on, and she comes in here and leaves her cap on the pillow and goes back to the hospital, and it's after midnight again.
# evidence:ev_ada_cap;object;Nurse's cap, Amy's pillow;Ada's cap, with the black stripe. Left on the pillow. She comes home every morning and goes back.
# note:Ada's nurse's cap on Amy's pillow. She comes HOME. Every morning at 7:30 she walks in and finds it and goes back to the night shift so it can't be morning. She's been doing it for ten months.
~ dorsey_found = true
~ mercy += 2
~ evidence += 1
~ hurt(1)
-> dorsey_rooms

= exit_after_kids
The children's room. The carousel lamp turning. You meant to leave. You're sure you meant to leave.
+ [Go back out the door you came in] -> dorsey_exit
+ [Stay a minute] -> dorsey_rooms

=== dorsey_radio ===
# speaker:1610
# music_static:0.4
{&"Short one. Short one. Short one. You would never be short, traveler. One is so easy to count."|"Mrs. Dorsey should come home. Tell her. Tell her it's morning. Then she'll be home, and the house will be full, and we can try again."|"Lyle cried. Did you know? The whole hour. We could hear him."}
# music_static:0
~ attunement += 1
->->

=== dorsey_police ===
# speaker:police
{ okafor_gone:
    "Cally," says the voice that is not Okafor. "Is the tree still up? It's so pretty. We always loved the lights on Birch Street."
    ~ hurt(1)
- else:
    "Copy, Cal. Dorsey, Birch Street. December." Paper rustles. "Night shift nurse. Two kids. We sent a man up from Troop F. He was there nine minutes." A pause. "That's on us, Cal. That's on all of us."
    ~ resolve += 1
}
->->

=== dorsey_exit ===
{ not dorsey_found:
    You go out the door you came in.

    You are standing in the Dorsey kitchen. The stove clock says ten o'clock.

    You missed it.
    ~ hurt(1)
    -> dorsey_top
}
{ dorsey_loop < 3:
    ~ dorsey_loop += 1
    You go out the door, and you're in the kitchen again, and the Christmas lights outside blink the same slow pattern, a little faster.
    -> dorsey_top
}
-> dorsey_theory

=== dorsey_theory ===
# theory:dorsey;What happened in the Dorsey house, and what does Ada need?
# slot:lyle counted;Four, counting Ada*@ev_dorsey_children;Three;Two
# slot:ada lived because;She was on night shift*@ev_ada_december;She hid;Lyle spared her on purpose
# slot:afterward;He was short one, and it went bad in him within the hour*@ev_dorsey_page;He felt nothing;He called the police
# slot:ada needs;To be told it's morning, so she can go home*@ev_ada_cap;To stay on shift forever;To forget them
# hint:Under the tree, the phone, the children's room, and what Ada told you at the hospital.
The door. Three passes. Your pen is already out.
+ [FILE: File a theory]
    -> dorsey_result
+ [Go round again]
    -> dorsey_top
+ [Leave the house for now]
    You go out the way you came, and this time it's Birch Street. The lights blink. The house will start over when you come back.
    -> hush_hub

=== dorsey_result ===
~ partial(theory_score, 4)
{ theory_score < 4:
    ~ wrong_theories += 1
    ~ hurt(2)
    Not all of it. Outside, the lights speed up.
    -> dorsey_top
}
# theme:fog
# warp:cursor_normal
# music:the_hush
# time:16:20
You go out the back door, and it's the back yard, and the garage, and the fog, and Birch Street.

Behind you, one by one, starting at the gutter and working down the maple, the Christmas lights go out.

Not all at once. Like someone going around the house turning them off before bed, taking their time, the way you do when it's the last thing you'll do today and you know you've done everything else.
~ dorsey_closed = true
~ houses_closed += 1
~ resolve += 1
~ evidence += 1
-> ada_morning

=== ada_morning ===
# hint:You can go and tell Ada. It costs you nothing but a drive.
+ [Drive to the hospital and tell Ada it's morning] -> tell_ada
+ [Leave it. Back to the car.] -> hush_hub

= tell_ada
# map:hospital
The third floor. The nurses' station. Ada with her charts.

"It's morning, Ada," you say.

She looks at the clock. It says 12:05.

"It's morning," you say again. "I was at the house. The lights are off. I watched them go off. Amy and Joel are asleep." You don't know if that's true. You decide it's true. "You can go home now. It's morning."

Ada looks at the clock for a long time. The second hand moves. One tick. Two. It goes around.

She stands up, and unpins the little white cap with the black stripe, and puts it on the desk, square in the middle of her charts. She takes her coat off the hook.

"Thank you, Sergeant," she says. She doesn't cry. She looks like she has done all of that, a long time ago, in a room you'll never see.

She takes the stairs. You hear her all the way down, her white shoes on the treads, one floor, two, the lobby door.

Then nothing.

On the desk the transistor radio is off. You didn't see her turn it off.
# note:Told Ada it was morning. She clocked out. She went home. I hope she went home.
~ ada_home = true
~ mercy += 3
~ steady(3)
-> hush_hub
