// ============================================================
// Chapter 8. Act III: St. Adalbert's, the Fellowship.
// Choir practice is still going in an empty church. The Fellowship
// tapes in the parish hall. Jo hums something she can't name.
// ============================================================

VAR tapes_heard = 0
VAR roster_found = false
VAR jo_hums = 0

=== act3_start ===
# chapter:8:St. Adalbert's
# theme:static
# music:fellowship
# map:st_adalberts
# time:19:00
# hint:Find out what the choir is. The parish hall has the Fellowship tapes. Keep Jo close.
Your watch says seven o'clock. You don't remember it moving. Jo's says seven too. She shows you, without being asked, holding her wrist out in the cruiser's dome light like a kid showing a scraped knee.

"It does that," she says. "When it's choir night, it's seven. When it's not, it's whatever it wants."

She drives. She drives the way county deputies drive on roads they've known since they were sixteen, one hand at the bottom of the wheel, taking the curves before they come. The fog parts for her headlights like it knows the car.

"You're from here," you say.

"Born at County, second floor, 1956." Her mouth goes sideways. "Maternity was on two then. My dad was a millwright. Thirty-one years. He died in '83 before they shut it. Mom says that was a mercy." She glances at you. "You?"

"Nine Mill Street."

"Oh," Jo says, and nothing else, which tells you she's read the files too.

The marquee by the church steps says MEN'S CHOIR TUES & THURS 7PM. The bottom line is blank. Somebody took the letters down. The chain is gone from the doors.

The doors are standing open, and from inside, warm yellow light, and singing.
-> church_steps

=== church_steps ===
+ [Go in the front] -> nave
+ [Go around to the parish hall] -> parish_hall
+ [POLICE: Try the base set] -> church_police -> church_steps
+ {cigarettes > 0} [Smoke a cigarette on the steps] -> smoke -> church_steps

=== church_police ===
# speaker:police
"Cally! You made it." The not-Okafor voice is warm, delighted, a hostess at the door. "Go on in. They've been practicing for you all day."
Jo reaches over and turns the handheld off at the knob, and holds her hand over it for a second, like a lid on a pot.
"Don't," she says. "Don't talk to it. It likes being talked to."
~ jo_hums += 0
->->

// ------------------------------------------------------------ the nave
=== nave ===
# music:fellowship
# hint:The Choirmen are Ledger men. Their faces don't tune in. They don't like being looked at, and they don't like being interrupted.
{ nave == 1:
    -> nave_first
}
The nave. The pews, the loft, the voices. The men in the robes at the rail.
-> nave_menu

= nave_first
St. Adalbert's is bigger inside than out, which you're getting used to. Polish Gothic on a mill town budget: plaster vaulting painted to look like stone, stained glass windows donated by families whose names are on brass plates under them, the Stations of the Cross in a ring around the walls. Every candle in the place is lit. The pews are empty.

The singing is coming from the choir loft at the back, over the doors you just came through.

You turn around and look up.

There are men in the loft. Twenty, maybe. Black robes, red stoles. They're standing at the rail in two rows, singing, and their faces won't hold still. Not moving. Not holding. Like a television between two stations where the picture keeps trying to come in, a jaw, an ear, a pair of glasses, and keeps losing it to snow.

They're singing in English. It's a hymn, or it's the shape of a hymn, four-square and slow and solemn. You know every hymn there is, your mother saw to that. You don't know this one. The words are mostly numbers.

Jo stands beside you with her head tilted back. Under her breath, so quietly you only hear it because the choir comes to the end of a line, she's humming along.
~ jo_hums += 1
~ hurt(1)
-> nave_menu

= nave_menu
+ [Count the Choirmen] -> count_choir
+ [Climb to the loft] -> loft
+ [Ask Jo what she's humming] -> jo_humming
+ [Light a candle] -> candle
+ [Go to the parish hall] -> parish_hall
+ {loft} [Leave the church] -> act3_hub
+ {not loft} [Leave the church @@ Climb to the loft] -> loft

= count_choir
You count. You can't help it now. Nobody in this town can.

Twenty-two Choirmen in two rows. The front row is old men, stooped, the snow in their faces slow and settled. The back row is younger. In the back row, on the end, there's one whose face keeps almost coming in, a heavy face with a mustache and a towel over his shoulder that he's wearing on top of his robe.

The bartender from the Spindle.

He's the only one who isn't singing. His mouth is moving, but it's out of time with the rest. He's still counting.
# note:22 Choirmen in the loft. Old men in front, younger behind. The Spindle bartender is in the back row, wearing his bar towel over the robe, still counting, out of time. He's NEW. He hasn't made room yet.
~ evidence += 1
-> nave_menu

= loft
The stairs to the loft are behind a door by the font, narrow, turning twice. You climb them. The singing gets louder as you go up, and then, on the last step, it stops.

The loft is empty. Twenty-two robes lie on the floor in two rows, flat, like the men inside them stepped out all at once. The organ is open. On the music stand there's a sheet of manuscript paper with a staff ruled on it by hand and notes written above and below the lines, way above, way below, on short extra lines that climb off the edge of the paper.

Somebody's written a title at the top in neat librarian's printing.

FOR THE ONES PAST THE EDGE. (LEDGER LINES.)
# evidence:ev_ledger_lines;object;Choir loft music;Hand-ruled staff, notes far above and below on short extra lines. Title: "For the ones past the edge. (Ledger lines.)"
# note:Choir loft. The music is all LEDGER LINES, the little lines for notes outside the normal staff. That's the pin on the Harlan robe. That's what they call themselves. The Ledger. They sing what's past the edge.
~ evidence += 2
~ hurt(1)
+ [Look down into the nave]
    You look down over the rail.
    The pews aren't empty now. Every one is full, families, all of them gray and churning, sitting very straight with their hands in their laps, facing the altar. Hundreds of the Counted. Every house the Ledger ever emptied, sitting through Mass.
    They all turn to look up at you at the same time.
    ~ hurt(3)
    ~ attunement += 1
+ [Go back down without looking]
    You go back down. You don't look over the rail. Jo is waiting at the bottom with her hand on her gun.
- -> nave_menu

= jo_humming
"Jo. What's that you're humming?"

She stops. She looks surprised. "Was I?"

"You were humming along with them."

"Huh." She thinks about it. "It's from Fellowship. Mom used to bring me when I was little, when Dad went. There were always kids running around the parish hall. Mrs. Lusk played the piano." She frowns. "I don't know the words. I never knew the words. It just comes on, sometimes, when I'm tired."

"When did your dad start going to Fellowship?"

"After his back went. 1979?" She sees your face. "He didn't do anything, Cal. He didn't do anything. He died in his sleep in '83."

"Okay."

"He died in his sleep," Jo says again, and starts humming without knowing she's doing it.
# note:Jo's father went to Fellowship from 1979. Died in his sleep in '83. Jo came as a little girl. She hums the tune and doesn't know she does it.
~ jo_hums += 1
~ mercy += 1
-> nave_menu

= candle
There's a rack of votive candles in red glass by the side altar, a coin box, a sign: OFFERING 25 CENTS. Every candle is lit except one.

You put a quarter in the box. You light the last one. You don't pray. You haven't since you were nine, when you prayed every night for a year that your father would come and get you, and then stopped, on the night you understood what your mother had been afraid of.

You light it for Beth Harlan, who told her mother.
~ mercy += 1
~ steady(2)
-> nave_menu

// ------------------------------------------------------------ the parish hall
=== parish_hall ===
# music:fellowship
# map:st_adalberts
{ parish_hall == 1:
    -> hall_first
}
The parish hall. The folding chairs in their circle. The coffee urn. The piano. The office with the tapes.
-> hall_menu

= hall_first
The parish hall is a long low room under the church with a linoleum floor and a drop ceiling and fluorescent lights, half of them out. Folding chairs are set up in a circle in the middle, twelve of them, with a coffee urn on a card table and a plate of sugar cookies with plastic wrap over them. An upright piano against the wall, with a hymnal open on it.

A banner hangs over the piano, felt letters glued on burlap, the kind a church ladies' committee makes:

MONDAY NIGHT FELLOWSHIP
YOU WERE MADE FOR SOMETHING LARGER

Jo goes to the circle of chairs and stands behind one of them with her hands on the back, and you know, without asking, that this was her father's chair.
-> hall_menu

= hall_menu
+ [The office at the back] -> office
+ [The piano] -> hall_piano
+ [The circle of chairs] -> chairs
+ {tapes_heard >= 2 && roster_found} [Go back up to the church steps] -> act3_hub
+ [Go up to the church] -> nave

= hall_piano
The upright is a Wurlitzer, cheap, the veneer peeling. You press middle C. It's flat. You press the next one. Flat by a different amount. The whole piano is out of tune in a way that isn't neglect. Someone tuned it like this. Each string a little off from where it should be, so that any chord you play is almost right, and wrong underneath, like a smile with something behind it.

On the music rest, the hymnal is open to a page that isn't a hymn. Someone has glued manuscript paper over it. Ledger lines.
-> hall_menu

= chairs
Twelve chairs. On the seat of each, a name tag in a plastic sleeve, the kind with a safety pin on the back. HELLO, MY NAME IS, and a first name in marker.

WES. LYLE. DALE. ED. BOB. PAUL. LEON. RAY. And four that say nothing at all, blank, waiting.

The one Jo is standing behind says FRANK. Her father's name was Frank. She's not looking at it.
+ [Ask her about it]
    "Jo."
    "I know," she says. "I know it's his. I see it." She takes her hands off the chair back. "He was in the choir. Okay? I didn't say before. He was in the choir and he died in his sleep and he never did anything to anybody. Some of them don't. Okay? Some of them just go to sleep."
    ~ mercy += 1
    ~ jo_hums += 1
+ [Leave it]
    You leave it. She'll tell you or she won't.
- # note:Fellowship chairs. Name tags: WES, LYLE, DALE, ED, BOB, PAUL, LEON, RAY, four blank. And FRANK, Jo's father. RAY is the only living one on the list I don't have a file for. Ray. The bartender?
~ evidence += 1
-> hall_menu

= office
The office is a closet with a desk in it. A reel-to-reel tape recorder on the desk, a Wollensak, the kind schools had, and a metal shelf of tape boxes, each labeled on the spine in the neat printing you've been seeing all day.

FELLOWSHIP 3/57. FELLOWSHIP 9/62. FELLOWSHIP 4/85. FELLOWSHIP 9/86. Dozens. Thirty years of Monday nights.

There's a three-ring binder on the desk too, with a typed label. CHOIR ROSTER, CURRENT.
-> office_menu

= office_menu
+ {tapes_heard < 3} [Play a tape] -> play_tape
+ {not roster_found} [Read the roster] -> roster
+ [Back out to the hall] -> hall_menu

= play_tape
~ tapes_heard += 1
You thread a reel. It's been a while. Your hands remember.
{ tapes_heard:
- 1: -> tape_1957
- 2: -> tape_1985
- else: -> tape_1986
}

= tape_1957
# speaker:1610
FELLOWSHIP 3/57. Hiss, and the clatter of folding chairs. Then a woman's voice, younger than the one on the Harlans' radio, brighter, eager.
# speaker:1610
"Welcome, gentlemen. My name is Margaret Lusk, and I play the organ upstairs, and Father has been good enough to let me borrow this room on Monday nights. I know times are hard. I know the mill took the second shift and some of you are wondering what you're for." A pause. "I want to tell you about something I heard on the radio."
Then a man's voice, off-mic, a voice you know, a voice you would know anywhere, though you were five years old in March of 1957.
"What station?" your father asks.
# speaker:1610
"Oh," says Margaret Lusk, "it's not on any station, Walt. It's past the end of the dial. That's the wonderful thing about it."
# evidence:ev_tape_1957;statement;Fellowship tape, 3/57;Margaret Lusk's first Fellowship. My father asks "What station?" She says "It's past the end of the dial."
# note:Tape, March 1957. The FIRST Fellowship. Margaret Lusk, organist, young. My father was there. He asked what station. "Past the end of the dial." She started this. She started it with him.
~ evidence += 2
~ hurt(2)
-> office_menu

= tape_1985
# speaker:1610
FELLOWSHIP 4/85. The voice is older now, the one from the Harlans' radio, warm and tired.
# speaker:1610
"...and they're still there, gentlemen, the people in the static. A whole nation of them. People like us, or people who were us once. Trapped where nothing dies. They're so lonely. They only want to come home. And when they come home they'll bring what they have with them, which is that they never end, and that they can be heard on every radio and every telephone and every television there is. Can you imagine? Never to be useless again. Never to be unheard."
A man's voice, tentative: "How do they come?"
# speaker:1610
"Through a man," says Margaret Lusk. "A man who can hold one long enough. Most can't. That isn't their fault. It's a very great thing to hold. But we keep trying, don't we? Because one day one of you will be strong enough. And then all of us, all of us, will be kept."
# evidence:ev_tape_1985;statement;Fellowship tape, 4/85;Lusk: a nation in the static, the Kept, trapped where nothing dies. They come through a man who can hold one. "Then all of us will be kept."
# note:Tape, April 1985. Lusk on the Kept: people in the static who never die and can be heard everywhere. They come through a man who can HOLD one. Most can't. "We keep trying." The families are what's left when a man can't hold it.
~ evidence += 2
~ attunement += 1
~ hurt(1)
-> office_menu

= tape_1986
# speaker:1610
FELLOWSHIP 9/86. Recent. Lusk's voice, and under it, too close to the microphone, a man breathing hard.
# speaker:1610
"It's all right, Raymond. Say it with me. One six one zero."
"One six one zero."
# speaker:1610
"And the ones at home."
A long silence. Then: "Three. Carol. Me. And the boy, Tyler, our grandson, he's with us since his mom." The man's voice cracks. "I don't want to, Margaret. I don't want to make room."
# speaker:1610
"I know," says Margaret Lusk, so gently. "Nobody wants to, at first. Keep the radio on at night, Raymond. Keep it on at the bar. It gets easier."
# evidence:ev_tape_1986;statement;Fellowship tape, 9/86;Raymond: "Three. Carol, me, and Tyler, our grandson." "I don't want to make room." Lusk: "Keep the radio on at the bar."
# note:Tape, Sept '86. RAYMOND. Three at home: Carol, Ray, grandson Tyler. He doesn't want to. She told him to keep the radio on at the bar. The Spindle. It's Ray. It's tonight, or it's soon.
~ evidence += 2
~ mercy += 1
-> office_menu

= roster
~ roster_found = true
# evidence:ev_roster;statement;Choir roster, current;Typed list of living members. Last entry, added in pen: TOLLIVER, Raymond, the Spindle. Under "Precentor": Mrs. M. Lusk, Calder Falls Public Library.
The roster is typed, names and addresses, a list of living men, half of whom you'd guess are over seventy. Retired millwrights, a pharmacist, two funeral directors, a man who owns the Agway. Under each name, a date: BROUGHT IN, and a year.

At the very end, added in blue pen: TOLLIVER, Raymond. The Spindle, Main St. Brought in Aug '86. And beside it, in red: READY?

On the inside cover, typed:

PRECENTOR: Mrs. Margaret Lusk
Calder Falls Public Library (residence above)
For all matters of the choir.
# note:Roster. Living members, old men, the Agway, two undertakers. Newest: TOLLIVER, Raymond, the Spindle, Aug '86, "READY?" in red. Precentor: Mrs. Margaret Lusk, the Public Library, lives upstairs. Precentor is the one who leads the singing. She LEADS it.
~ evidence += 2
-> office_menu

// ------------------------------------------------------------ the Act III hub
=== act3_hub ===
# theme:static
# music:fellowship
# hint:{ray_saved || ray_lost || ray_dead:Go to the library and see Margaret Lusk.|Ray Tolliver at the Spindle is counting. If you go to the library first, you may be too late for him.}
{ (ray_saved || ray_lost || ray_dead) && lusk_met:
    -> act4_start
}
You and Jo stand on the church steps. The fog has gone the color of a dead TV channel, and it hisses, very softly, all the time now.

"Where to?" Jo says.
+ {not ray_saved && not ray_lost && not ray_dead} [The Spindle. Ray Tolliver.] -> spindle_start
+ {not lusk_met} [The library. Margaret Lusk.] -> library_start
+ [Back into the church] -> nave
+ {cigarettes > 0} [Smoke a cigarette] -> smoke -> act3_hub
