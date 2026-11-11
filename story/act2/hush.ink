// ============================================================
// Chapter 5. Act II: The Hush.
// Calder Falls as a hub, worked in any order: the county substation,
// Ostrander County Hospital, 9 Mill Street, and the two murder houses
// (Pruitt, chapter 6, and Dorsey, chapter 7). Close both houses and the
// way into Act III opens.
// ============================================================

=== hush_start ===
# chapter:5:The Hush
# theme:fog
# music:the_hush
# time:16:20
# map:cobb_road
# hint:The town is a hub now. The Map tab shows where you have been. Close both murder houses, the Pruitt house and the Dorsey house.
The fog has no edges. It isn't weather. It sits on Cobb Road like it has been poured in and left to set.

Your cruiser is where you parked it, behind the place where Okafor's Ford was. The Ford is gone. The county cars are gone. There are no tire marks in the gravel where they turned around, because they didn't turn around. They were never here, or they were here and then they weren't, and the gravel has decided not to take a side.

The yellow tape is gone too. The rosebush, the lamppost. The truck is still in the drive. Brown and tan. The cloth is gone from the inside of the windshield. You don't look into the cab. You've already decided you won't, and you are going to keep deciding it.

Your watch says 4:20.

You get in the cruiser. The engine starts on the first try, which nothing in this county has done for you today. The heater blows warm. The police radio under the dash is dark. You key it anyway.
# speaker:police
"Cal." Okafor, clear as anything. "Copy. Where are you?"

"Cobb Road. Outside the Harlan house. Where are you?"
# speaker:police
"I'm at the county substation on Front Street. We all are." A pause. "You've been in there a while, Cal. You come down to the substation when you're done. Drink some coffee. We'll go over it."

"Dana, the cars are gone. You're gone. There's nobody here."
# speaker:police
"I know," she says, very gently. "Come down to the substation."
~ hurt(1)
# note:Out of the house. Fog. No cars, no tape, no Okafor. Okafor on the radio says they're all at the county substation, Front St. She said "I know."
-> hush_hub

=== hush_hub ===
# music:the_hush
# time:16:20
{ houses_closed >= 2:
    -> act2_end
}
{ pruitt_closed && not okafor_gone:
    ~ okafor_gone = true
}
{ not okafor_gone:
    The fog moves past the windshield from left to right. Calder Falls is out there somewhere, all of it, quiet.
- else:
    The fog moves past the windshield from right to left now. You don't know when it changed.
}
# hint:{hush_hint()}
+ [Drive to the county substation on Front Street] -> substation
+ [Drive to Ostrander County Hospital] -> hospital
+ [Drive to 9 Mill Street] -> mill_street
+ {not pruitt_closed} [Drive to the Pruitt house, Kessler Lane] -> pruitt_house
+ {not dorsey_closed} [Drive to the Dorsey house, Birch Street] -> dorsey_house
+ [Drive through the square] -> square
+ [POLICE: Call the substation] -> hush_police -> hush_hub
+ [RADIO:1610: Tune the cruiser to the top of the dial] -> hush_1610 -> hush_hub
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> hush_hub
+ {nerve < 7} [Sit a minute with the engine running] -> rest -> hush_hub

=== function hush_hint() ===
{ houses_closed == 0:
    ~ return "Two murder houses: Pruitt on Kessler Lane, Dorsey on Birch Street. Ada Dorsey at the hospital knows the Dorsey house. The substation is safe."
}
{ not dorsey_closed:
    ~ return "The Dorsey house is left. If you haven't, talk to Ada Dorsey at the hospital first."
}
~ return "The Pruitt house on Kessler Lane is left."

=== hush_police ===
# speaker:police
{ not okafor_gone:
    {&"Cal. Copy. Come on down to the substation. The coffee's on."|"Copy, Cal. We're all here. Front Street. Come in."|"Cal, the ME called. He says he'll be here at six." A pause. "It's still four-twenty, isn't it."}
- else:
    {&"Cally." It is Okafor's voice. Okafor has never called you Cally in her life. Nobody has called you Cally since 1957. "Copy, Cally. Come down to the substation."|"Copy." The voice is Okafor's, and the breathing behind it isn't. Too many people breathing. "We're all here. All of us."|"One six one zero," the voice that is not Okafor says, conversationally, and then, "Sorry. Copy, Cal. Go ahead."}
    ~ hurt(1)
}
->->

=== hush_1610 ===
# speaker:1610
# music_static:0.4
{ houses_closed:
- 0: "Kessler Lane. The Pruitt boy. Ask him who he made room for. Birch Street, after. Mrs. Dorsey has the key, and she will not give it to a liar."
- 1: "One more house, traveler. Then the church. They are singing for you already. Can you hear it?"
- else: "Come to church."
}
# music_static:0
~ attunement += 1
->->

// ------------------------------------------------------------ the square
=== square ===
# map:spindle
# map:st_adalberts
The square is a rectangle of brown grass with a bandstand in the middle and a granite soldier on a plinth, facing the wrong way, toward the mill instead of the road. Every storefront is dark except the Spindle, whose Schlitz sign hums blue in the window. The Pontiac is still out front. Nobody's in it.

St. Adalbert's is up the hill. You can see the bottom third of the steeple. The marquee by the steps still says MEN'S CHOIR TUES & THURS 7PM. The bottom line has changed.

HE KNOWS YOUR NUMBER, it said, two hours ago or no time at all.

WE KNOW YOUR NUMBER, it says now.
~ hurt(1)
{ houses_closed < 2:
    You climb the steps. The church doors are chained, a heavy logging chain through both handles and a padlock the size of your fist. From inside, very faint, you can hear a piano. One note, then the same note again.
    Not yet, then.
- else:
    The doors are open.
}
+ {called_ruth < 3} [Use the payphone outside the Rexall] -> payphone -> square_out
+ [Look in the window of the Spindle] -> spindle_window -> square_out
+ [Back to the car] -> hush_hub

= square_out
+ [Back to the car] -> hush_hub

=== spindle_window ===
You cup your hands against the glass. The Spindle is a long room with a bar down the left side and booths down the right and a jukebox at the back, lit up, the 45s inside turning in their slots.

There's a man behind the bar. Heavyset, fifties, a towel over his shoulder. He's wiping the same glass in slow circles, and his lips are moving. You can't hear him through the glass. You can see the shape of the words.

One. Six. One. Zero.

You knock. He doesn't look up. You try the door. Locked.

The jukebox changes records. You can feel the bass through the glass.
# note:The Spindle. Bartender, 50s, towel on shoulder, wiping a glass, mouthing 1610. Alive? He didn't hear me knock. Door locked.
~ evidence += 1
->->

// ------------------------------------------------------------ Ruth
=== payphone ===
# hint:The payphones in town can reach Ardell, three hours south. Your mother is not always lucid.
The payphone is in a steel hood bolted to the wall of the Rexall. You have a roll of dimes in the glove box because you are a man who keeps a roll of dimes in the glove box. You dial the Ardell Hospice. Long distance. The operator asks for a dollar forty. You feed it.

It rings eight times.
~ called_ruth += 1
{ called_ruth:
- 1: -> ruth_first
- 2: -> ruth_second
- else: -> ruth_third
}

= ruth_first
"Ardell." A night-shift voice, though it's four in the afternoon. "Hold for Mrs. Brennick's room."

Clicks. Then her.

"Hello?"

"Mom. It's Cal."

"Cal." She says it like she's reading it off a card. Then her voice changes, and it's her, really her, the voice that used to wake you for school. "Cal. Where are you? You sound like you're in a can."

"I'm in Calder Falls, Mom."

The line goes so quiet you think she's hung up.

"Why would you go there," she says finally. Not a question. "Why would you go there, after I took you all that way."

"I'm working a case."

"Is it the church?"

You hold the phone so hard the cord creaks. "What do you know about the church, Mom?"

"Margaret Lusk," your mother says. "She played the organ. She came to the house with a radio in a box with a bow on it. She was so nice to your father. She was so nice to me. She asked how many children we had and I said just the one and she said, oh, that's all right, one is enough." A long breath. "One is enough. I never forgot that. I'm tired now, Cal."

"Mom, wait."

"Keep your head down," she says, and the line clicks, and a recorded voice tells you to deposit sixty cents for an additional three minutes.
# evidence:ev_ruth_lusk;statement;Mom, on the payphone;Margaret Lusk brought my father the radio in 1957. Asked how many children. "One is enough."
# note:Mom: Margaret Lusk came to Mill St in 1957 with the radio. Asked how many kids. "One is enough." Lusk was there THEN. She's still here NOW. Thirty years.
~ mercy += 1
~ evidence += 1
~ steady(1)
->->

= ruth_second
"Hello? Walt?"

"Mom. It's Cal."

"Walt, he's asleep. He's asleep in the back seat. Don't you come out here. Don't you come out to the car." Her voice is high and fast. She's not in Ardell. She's on Route 9 in a 1951 Plymouth with the gas gauge on a quarter and a nine-year-old in the back, and she's been there for twenty-nine years.

"Mom, it's Cally. I'm grown up. It's 1986."

"You keep your head down," she whispers. "If he calls, you don't say a word, you hear me? He can't count you if he can't hear you."

The line goes dead. You stand there with the receiver against your ear for a long time, listening to the dial tone, which is the plainest sound in the world and which, right now, you are very grateful for.
# note:Mom thought I was Dad. "He can't count you if he can't hear you." That's why she kept me quiet in the car. That's why the Kept count people by their voices?
~ mercy += 1
~ hurt(2)
->->

= ruth_third
It rings and rings. Then a voice that isn't the night nurse and isn't your mother says, very close to the mouthpiece:
# speaker:1610
"She's sleeping, Cally. We'll tell her you called. We're very good at keeping people."
~ attunement += 1
~ hurt(3)
You hang up so hard the hook rings.
->->

// ------------------------------------------------------------ substation
=== substation ===
# music:substation
# map:substation
# autosave
# hint:The substation is safe. Rest, read the county files, use the radio. Okafor is here, on the base set.
{ substation == 1:
    -> substation_first
}
The substation. The coffee, the cot, the base radio. The files on the desk where you left them.
-> substation_menu

= substation_first
The Ostrander County substation is a one-room brick building on Front Street with a flagpole and no flag. Inside: a steel desk, a filing cabinet, a cot with an army blanket folded on it, a Mr. Coffee with a full pot on the warmer, a base station radio on the wall with a red ON light, and a calendar from the Grange.

Nobody's here. The coffee is hot.

You pour a cup. It's the best cup of coffee you've ever had, which tells you something about your day.
~ steady(3)
-> substation_menu

= substation_menu
+ [Sit on the cot and rest] -> rest_full
+ [Read the county files on the desk] -> county_files
+ [Talk to Okafor on the base set] -> base_set
+ {substation_menu > 2} [Look at the Grange calendar] -> grange_calendar
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> substation_menu
+ [Back to the car] -> hush_hub

= rest_full
You lie down on the cot with your shoes on and the blanket over your legs and you close your eyes.

You don't sleep. You lie there and listen to the coffee maker tick and the base radio hiss and the flagpole rope outside slapping the pole in a wind you can't feel, and after a while your hands stop shaking.
~ nerve = 10
~ resolve += 1
-> substation_menu

= county_files
# evidence:ev_county_files;statement;County files;Fathers, 1957 to 1986: Brennick, Szymanski, Ostrowski, Haney, Kowal, Pruitt, Dorsey, Harlan. Every one: St. Adalbert's men's choir.
The files are in a stack on the desk, manila folders tied with string. Somebody pulled them for you. You don't know who. You don't ask.

You know most of these. You have clippings for most of these. You've never seen the files.

1957. BRENNICK, Walter J., 9 Mill St. Suicide by hanging, garage. Wife and son had left the residence that morning. Note recovered. Contents: "I will get him one day. I could not make room."

1962. SZYMANSKI, Leon, 41 River Rd. Wife and three children. Then himself.

1966. OSTROWSKI, Paul. Wife and one child.

1971. HANEY, Robert. Wife, mother-in-law, two children.

1979. KOWAL, Edward. Wife and two children.

1985, March. PRUITT, Dale, 14 Kessler Ln. Mother and brother. Dale Pruitt found at the residence, alive, unresponsive. Committed, state hospital, Ardell. You go cold at that, because Ardell is where your mother is.

1985, December. DORSEY, Lyle, 6 Birch St. Two children. Wife was at work. Then himself.

1986, October. HARLAN, Wesley. The folder for this one is the thinnest. Somebody has written the date in already. Somebody has written CLOSED on the tab.

Every folder has the same line typed in the background section, in the same flat department prose, like a form they all filled in the same way:

Subject was an active member of the St. Adalbert's Men's Choir.
# note:County files. Eight fathers since 1957. My father is the first. EVERY ONE was in the St. Adalbert's men's choir. Nobody connected it. Or somebody did, and typed it in the same place every time and never said it out loud.
~ evidence += 2
~ hurt(1)
-> substation_menu

= base_set
{ okafor_gone:
    -> base_fake
}
# speaker:police
"Cal." It's her. You can tell it's her by how she doesn't waste anything. "You're at the substation. Good. Drink the coffee. I've got the ME on the other line. Six o'clock." A pause. "Are you all right? Tell me before, not after. That was the deal."
+ [Tell her the truth: you're not all right]
    "I'm not all right, Dana."
    # speaker:police
    "Okay." No pity in it. "Okay. Then you sit down, and you drink the coffee, and you do one thing at a time. That's how you get through these. One thing, then the next thing."
    ~ resolve += 1
    ~ steady(2)
+ [Tell her you're fine]
    "I'm fine."
    # speaker:police
    "Mm," she says, and you can see her face exactly. "Drink the coffee, Cal."
    ~ resolve -= 1
- -> substation_menu

= base_fake
# speaker:police
"Cally," says the voice on the base set. "Sit down. Have some coffee. You must be so tired, after all that walking. There's a cot."
"Who is this?"
# speaker:police
"It's Dana," the voice says, hurt. "Lieutenant Okafor. You know me." A pause, and the breathing behind it. "We know you."
~ hurt(2)
# note:The base set isn't Okafor any more. It's her voice. It isn't her. When did it change? After the Pruitt house?
-> substation_menu

= grange_calendar
The Grange calendar is for 1986, October, a picture of a combine in a wheat field. Somebody has gone through the whole month with a red marker and crossed out every day, carefully, each X the same size.

Every day except today. Today, the twelfth, has been circled. Inside the circle, in red, in neat librarian's printing:

C.B. 1
~ hurt(2)
# note:Grange calendar in the substation. Every day X'd but today. Circled: "C.B. 1". Cal Brennick. One. I live alone. One.
-> substation_menu

// ------------------------------------------------------------ hospital
=== hospital ===
# music:the_hush
# map:hospital
# hint:Ada Dorsey can give you the key to the Dorsey house. She will not give it to someone who lies to her.
{ hospital == 1:
    -> hospital_first
}
Ostrander County Hospital. The lobby, the lino, the payphone by the gift shop. Third floor, the nurses' station.
-> hospital_menu

= hospital_first
Ostrander County Hospital is three stories of yellow brick with a portico held up by four white columns, built in 1923 by the Ostrander family when they still lived here and wanted their name on things. The doors open when you push them. The lobby is lit, every light on, and empty. A wheelchair sits in the middle of the floor where somebody left it, facing the doors, like it's waiting for you.

The board by the elevator says SURGERY 2, MATERNITY 3, ADMINISTRATION 1. Someone has scratched a fourth line into the brass with a key. LISTENING B.

There's no B on the elevator panel.
-> hospital_menu

= hospital_menu
+ [Take the stairs to the third floor] -> ada
+ {called_ruth < 3} [Use the payphone by the gift shop] -> payphone -> hospital_menu
+ [Look for Mrs. Cuddy] -> cuddy
+ [Back to the car] -> hush_hub

= cuddy
Room 114, a name card on the door: CUDDY, M.

She's asleep in the bed, a small woman with her hair in pink foam curlers, the blanket pulled up to her chin, a cup of ice chips going to water on the tray. She looks like she's been asleep for a long time.

The TV on the wall is on, sound off. It's the Harlans' living room. The couch, the afghan, the Zenith inside the Zenith. Three people on the couch, faces turned away. As you watch, the camera, if it's a camera, starts to turn toward them.

You turn the TV off at the knob. It stays off. You check twice.
~ hurt(2)
-> hospital_menu

= ada
{ ada == 1:
    -> ada_first
}
Ada Dorsey at the nurses' station, her charts in front of her, her coffee cold. She looks up when you come in, and she's glad to see you, and she hides it.
-> ada_talk

= ada_first
The third floor is maternity, which is a cruelty you don't have time to think about.

There's a woman at the nurses' station, the only person you've seen alive since you closed the Harlans' front door. White uniform, white stockings, white shoes, a little white cap with a black stripe pinned to dark hair. Thirty-four, maybe. She's charting by the light of a desk lamp, and she doesn't look up until you're right in front of her, and when she does she isn't startled. She's been waiting for somebody to come up those stairs for a very long time.

"Visiting hours are over," she says. "It's after midnight."

"It's four-twenty in the afternoon."

She looks at the clock over the station. You look too. It says 12:05. The second hand isn't moving.

"It's always after midnight on this floor," she says. Her name tag says A. DORSEY, R.N. "You're the state policeman. They said you'd come."

"Who said?"

She looks at the radio on the desk, a little transistor in a leather case, the dial lit up, the volume turned all the way down. She doesn't answer.
# evidence:ev_ada;statement;Ada Dorsey, R.N.;Night shift, Ostrander County Hospital. Clock at 12:05, stopped. "They said you'd come."
~ evidence += 1
-> ada_talk

= ada_talk
+ [Ask about December]
    -> ada_december
+ {ada_december} [Ask about Lyle and the choir]
    -> ada_choir
+ {ada_december && not ada_trusts} [Ask for the key to her house]
    -> ada_key
+ [Ask why she's still here]
    -> ada_why
+ [Leave her to her charts]
    -> hospital_menu

= ada_december
"I was on nights," she says. "Lyle didn't like it. He'd been off since the line shut and he didn't like being home alone with them at night, he said. He liked it better after he started with the choir. He was better. He was a lot better. He stopped drinking. He went to church."

She lines up the charts on the desk so their edges match.

"December fourteenth. I had a double. I called home at ten to say goodnight to Amy and Joel, like always. Lyle answered. He said they were asleep. He said, 'Four,' and I said, 'What?' and he said, 'Nothing. I'm practicing.' I didn't think anything. They practiced all the time, the choir. Christmas music."

She stops. You let her stop.

"I came home at seven-thirty in the morning. The Christmas lights were still on outside. He'd never leave the lights on, it ran up the bill."
# evidence:ev_ada_december;statement;Ada on Dec 14;Lyle said "Four" on the phone at 10 PM. "I'm practicing." She was at work. Two kids.
# note:Ada Dorsey: Dec 14, 1985. Lyle on the phone: "Four." Then "I'm practicing." Four = Lyle, Ada, Amy, Joel. But Ada wasn't home. He counted her anyway. Then he was short one.
~ evidence += 1
~ mercy += 1
-> ada_talk

= ada_choir
"Margaret brought him," Ada says. "Mrs. Lusk. She came by the house in the spring with a coffee cake and a flyer for the Fellowship. She said the men who worked the mill were the backbone of this town and the town had broken their backs and somebody had to help. She said it right there at my kitchen table. I thought she was the kindest woman I'd ever met."

Her hands are still on the charts.

"She gave him a radio. A clock radio, from the choir. He listened to it all the time. In bed. He'd lie there with it on, real low, and I'd hear it through the pillow. It wasn't music. It was people talking. Like a call-in show, but all the callers were saying the same thing."

"What were they saying?"

"Their numbers," Ada says. "Just their numbers."
# evidence:ev_ada_radio;statement;Ada on the radio;Lusk brought Lyle the Fellowship flyer and a clock radio. He listened in bed. "People saying their numbers."
~ evidence += 1
-> ada_talk

= ada_key
"You want to go in the house," Ada says.

"I need to."

"Why?" She looks at you properly for the first time. "What do you get out of it? You tell me the truth, and I'll give you the key. You lie to me, and you can kick the door in like he did to the bathroom, and see how far that gets you."
+ [Tell her the truth: your father was the first one, in 1957]
    "My father was one of them," you say. "1957. The first one. My mother got me out the morning of. He hanged himself in the garage that night. He left a note that said he'd get me one day." You've never said it all in one piece out loud. It comes out flat, like reading a file. "I want to know why. I want to know who did this to him. To all of them."
    Ada looks at you for a long time.
    Then she takes a key off the ring at her belt, a brass Schlage key with a red plastic cap, and slides it across the desk.
    "Back door," she says. "The front's chained. I chained it."
    # item:keys
    # evidence:ev_dorsey_key;object;Dorsey house key;Brass Schlage, red cap. Back door. From Ada.
    ~ ada_trusts = true
    ~ resolve += 1
    ~ mercy += 1
+ [Tell her it's procedure]
    "It's procedure, ma'am. The state's reopening the case."
    "The state," Ada says. "The state sent a man up in December who stood in my kitchen for nine minutes and wrote 'domestic' on a form. Procedure." She goes back to her charts. "Kick the door in, Sergeant."
    ~ resolve -= 1
- -> ada_talk

= ada_why
"I'm on shift," she says, like it's obvious. "If I go home, it's morning. If it's morning, I walk up the path and the lights are on." She turns a page in the chart. There's nothing written on it. "So I stay on shift. Somebody has to watch the babies."

There are no babies on the floor. Every bassinet in the nursery window is empty and made up neat.

"How long have you been on shift, Ada?"

"Since the fourteenth."

"Which fourteenth?"

She doesn't answer.
~ mercy += 1
-> ada_talk

// ------------------------------------------------------------ 9 Mill Street
=== mill_street ===
# map:mill_street
# music:listening_room
# music_layer:drums off
# music_layer:noise off
# hint:You can drive past 9 Mill Street as many times as you want. Going in is your call.
{ mill_street_in:
    -> mill_street_after
}
{ mill_street:
- 1: -> pass_one
- 2: -> pass_two
- 3: -> pass_three
- else: -> pass_more
}

= pass_one
Mill Street runs down from the square toward the river, two rows of narrow frame houses built by the company in 1911, all the same, each with a porch and a peaked roof and a little yard with a chain-link fence. Number 9 is the fifth on the left.

It's still there. Of course it's still there. White once, gray now, the paint gone to chalk. The porch sags in the middle like a hammock. There's a FOR SALE sign in the yard from a realty in Hollis that went out of business in 1974.

You don't stop. You drive past at twenty miles an hour, and you look at it in the mirror until the fog takes it.
~ hurt(1)
-> pass_choice

= pass_two
You drive past again.

The porch light is on. It wasn't on before. There's a 1951 Plymouth in the driveway, two-tone, green over cream, with the back door open.

You drive past.
~ hurt(1)
-> pass_choice

= pass_three
You drive past again, slower.

There's a boy sitting on the porch steps. Nine years old, in a striped shirt and corduroys, with his shoes in his hands and his head down. Keeping his head down. He doesn't look up as you go by.

You don't stop. You can't. You drive to the bottom of Mill Street and sit at the stop sign with the engine running and your forehead on the wheel.
~ hurt(2)
~ mercy += 1
-> pass_choice

= pass_more
You drive past 9 Mill Street. {&The porch light is on.|The porch is empty.|The Plymouth's back door is still open.|The front door is open now, too.} You are going to have to go in eventually. You know that. The house knows that. It's in no hurry.
-> pass_choice

= pass_choice
+ [Stop the car and go in] -> mill_street_inside
+ [Keep driving] -> hush_hub

= mill_street_inside
# theme:bleed
# music:listening_room
# warp:cursor_needle
You park at the curb where your father parked. You open the gate, which squeals the way it always squealed. You go up the steps, past the place where the boy was sitting, and the boards give under your feet in exactly the places they gave when you were nine.

The front door is open.

Inside, it isn't the house you remember, and it is. The shape of it is right: the front room, the kitchen at the back, the stairs. But it's wet. Every surface sweats. The wallpaper, the roses you used to count when you were sick in bed, has gone dark and soft and the roses are swollen, rising off the wall like blisters. There's a hum in the walls, low, a little under the sound of a refrigerator, and it's everywhere, it's in your teeth.

This is what the Bleed is. Not a different place. The same place, with the static let in.
-> mill_street_rooms

= mill_street_rooms
+ [The front room] -> front_room
+ [The kitchen] -> walt_kitchen
+ {walt_kitchen} [The garage] -> garage
+ [RADIO:1610: The radio on the kitchen shelf] -> walt_radio
+ [Go back out to the car] -> leave_mill

= front_room
The front room has your mother's davenport, the green one with the doilies on the arms, and the Philco floor radio your father bought the year before you were born. The dial on the Philco is lit. The needle is all the way to the right.

On the davenport there's an indentation, small, a child's, like someone has been sitting there with their knees pulled up for a very long time.

You sit beside it. You don't know why. It's warm.
~ mercy += 1
~ steady(1)
-> mill_street_rooms

= walt_kitchen
The kitchen. The table where you ate oatmeal. The window over the sink that looks out at the garage.

Your father is standing at the sink.

He is a big man, in a mill shirt, his back to you. You know the back of his neck better than you know his face, because that is mostly what you saw of him the last year: the back of his neck, as he stood at the sink with the radio on, saying things under his breath.

He is saying them now.
# speaker:1610
"One six one zero, three. One six one zero, three. One six one zero, three."
He stops. His head tilts, a dog hearing a whistle.
# speaker:1610
"Two," he says. Then, slowly, like he's working out a sum he doesn't like: "One."
+ [Say "Dad."]
    "Dad."
    He doesn't turn around. His shoulders go stiff.
    # speaker:1610
    "I couldn't make room," he says to the window. "They gave me so much and I couldn't make room. They said a strong man could. I wasn't strong. Your mother took you, Cally, and I couldn't hold it, and it went bad in me." He puts both hands flat on the counter. "Don't let them give it to you. Don't you say yes."
    ~ resolve += 2
    ~ mercy += 1
    # evidence:ev_walt;statement;Walt, at the sink;"I couldn't make room. They gave me so much. Don't let them give it to you. Don't you say yes."
    ~ evidence += 1
+ [Keep your head down. Say nothing.]
    You keep your head down. You say nothing. Your mother would be proud of you. You are forty minutes from having a heart attack.
    He counts down to one again. Then to nothing. Then he stands there in silence, and the hum in the walls rises, and you back out of the kitchen with your eyes on the linoleum.
    ~ hurt(2)
    ~ resolve += 1
+ [Look at his face]
    You walk around the table until you can see him.
    He doesn't have a face. Where his face should be the static has gotten in, a gray churning snow, the screen of the Zenith in the Harlans' front room, and in the snow there are mouths, a lot of them, small, opening and closing on numbers.
    ~ hurt(4)
    ~ attunement += 2
- -> mill_street_rooms

= garage
The garage door is open. The garage is empty except for a sawhorse under the crossbeam, and a coil of rope on the floor, and a sheet of paper nailed to the beam itself.

You know what the paper is. You've read it in a file an hour ago, or you'll read it in an hour. You read it anyway, because you are not going to come into this garage twice in your life.

I WILL GET HIM ONE DAY. I COULD NOT MAKE ROOM.

Somebody has added something underneath, in red marker, in neat librarian's printing.

UNSUITABLE.
# evidence:ev_walt_note;statement;Dad's note, the garage;"I will get him one day. I could not make room." Underneath, in red, neat printing: "UNSUITABLE."
# note:Dad's note in the garage. Under it in red, the same printing as the Grange calendar: UNSUITABLE. She graded him. She came here after and graded him.
~ evidence += 2
~ hurt(3)
-> mill_street_rooms

= walt_radio
# speaker:1610
# music_static:0.5
"Welcome home, Cally. He couldn't hold us. We knew you could. You held this house for twenty-nine years and you never once went inside. That is a strong man. That is a room with nothing in it."
# music_static:0
~ attunement += 2
~ hurt(1)
-> mill_street_rooms

= leave_mill
# theme:fog
# warp:cursor_normal
You go out the front door and down the steps and through the squealing gate, and you sit in the cruiser with the engine off for a while.

You went in. Twenty-nine years. You went in.
~ mill_street_in = true
~ resolve += 1
-> hush_hub

= mill_street_after
You drive past 9 Mill Street. The porch light is off. The Plymouth is gone. The front door is shut, and on the porch steps, where the boy was sitting, there's a pair of small shoes, side by side, laces tucked in.

You don't stop. You don't need to.
-> hush_hub

// ------------------------------------------------------------ end of Act II
=== act2_end ===
# music:substation
# map:substation
# autosave
# hint:Talk to Jo Tamsin. She is real, and she is on your side.
Two houses. You drive back to the substation through fog that has started to move in both directions at once, like the town is breathing.

The substation light is on. The coffee is on. There's a cruiser outside that isn't yours, an Ostrander County Plymouth Gran Fury with a dented quarter panel, and there's somebody sitting on the cot inside with a shotgun across her knees.

She has the gun on you before you're through the door. She's good. The barrel doesn't move at all.

"Say your name," she says.

"Brennick. State police. Major Crimes."

"Say how many people live in your house."

"What?"

"Say it." The barrel is very steady.

"One," you say. "I live alone. It's one."

She lowers the gun. She's in a county uniform, a deputy, maybe thirty, big shoulders, her hair cut short as a man's, a scar through one eyebrow. She looks like she hasn't slept since the mill closed.

"Okay," she says. "Okay. Sorry. They can't say their numbers like that. They sing them. You said it like a person."

"Who are you?"

"Tamsin. Jo. Deputy." She stands up, sets the shotgun on the desk, and holds out her hand, and her grip is warm and dry and real, and it's the best thing that's happened to you since the coffee. "I've been holed up in here since the fog. I heard you on the band talking to the lieutenant." She looks at the base set. "That's not the lieutenant, by the way."

"I know."

"Okay." She nods, once, a person filing something away. "Then we're on the same page. Choir practice is tonight. Seven o'clock. It's always tonight now. You want to go see what they're singing?"
# evidence:ev_jo;statement;Deputy Jo Tamsin;Ostrander County. Alive. Holed up in the substation since the fog. "They sing their numbers."
# item:keys
~ jo_with_you = true
~ resolve += 1
-> act3_start
