// ============================================================
// Chapter 10. Act III: the Precentor. Margaret Lusk, 64, retired town
// librarian, choir director for thirty years, kind and tired and
// helpful. Act IV opens her ledger. Here she is only a nice woman
// with a pot of tea.
// ============================================================

VAR lusk_number = ""
VAR read_history = false

=== library_start ===
# chapter:10:The Precentor
# theme:static
# music:precentor
# map:library
# hint:Talk to her. Read what's on the reading room table. Watch Jo.
{ not ray_saved && not ray_dead:
    ~ ray_lost = true
    On the way up Library Street you pass the end of Main, and you see the Spindle's Schlitz sign go dark. A Pontiac pulls away from the curb out front, no lights, and turns toward the edge of town, toward the houses.

    Jo watches it go in the side mirror. She doesn't say anything. Neither do you.
    ~ mercy -= 2
    ~ hurt(2)
    # note:Saw Ray Tolliver's Pontiac leave the Spindle, no lights, headed home. I went to the library first. I chose that.
}
The Calder Falls Public Library is a Carnegie building, 1909, brick and limestone, with CALDER FALLS PUBLIC LIBRARY cut into the lintel and a smaller line under it, KNOWLEDGE IS THE KEEPER OF THE DOOR. The steps are swept. There's a light on in the reading room, and a light on upstairs, behind lace curtains.

The door has a sign: CLOSED. Under it, smaller, handwritten: Sergeant Brennick, please come in.

Jo reads it over your shoulder. "Well," she says. "That's not great."
-> reading_room

=== reading_room ===
{ reading_room == 1:
    -> lusk_first
}
The reading room. The oak tables, the green lamps, the tea. Margaret Lusk in the wing chair by the card catalog.
-> lusk_menu

= lusk_first
The reading room is all oak and green glass lamps and the smell of old paper and floor wax. The card catalog runs the length of one wall, a hundred little drawers with brass pulls. A fire is going in the fireplace. There's a tea tray on the big table, three cups, a plate of shortbread arranged in a fan.

Three cups.

Margaret Lusk is sitting in a wing chair by the fire. She's sixty-four, small, straight-backed, in a gray cardigan with a pearl brooch shaped like a treble clef, her white hair pinned up in the way of women who learned to do it in 1940 and never saw a reason to stop. Reading glasses on a chain. A face that has been kind for so long it has set that way.

She gets up when you come in, slowly, one hand on the arm of the chair.

"Sergeant Brennick," she says. "Cal. Oh, look at you. You have his shoulders." She holds out both her hands. "And Josephine. Josephine Tamsin. You've grown so tall. You used to sit under the piano at Fellowship and untie the men's shoelaces. Do you remember?"

Jo doesn't answer. She's very pale. Her lips are moving.
~ jo_hums += 1
~ lusk_met = true
~ hurt(1)
-> lusk_menu

= lusk_menu
# hint:Margaret Lusk will answer almost anything you ask. She believes every word of it.
+ [Ask her what the choir is] -> ask_choir
+ [Ask her about your father] -> ask_walt
+ {ask_choir} [Ask her what happens to the families] -> ask_families
+ [Look at what's on the big table] -> big_table
+ {ask_choir && ask_walt} [She asks you a question] -> lusk_asks
+ [Watch Jo] -> watch_jo
+ {lusk_asks} [Leave] -> lusk_leave

= ask_choir
"What is the choir, Mrs. Lusk?"

"Margaret, please." She pours the tea. Her hands are steady. "It's a men's choir, Cal. Tuesday and Thursday. We sing at funerals. We do a drive at Christmas." She hands you a cup. You take it. You don't drink it. "And on Mondays, at Fellowship, I try to give the men somewhere to put it."

"Put what?"

"Everything," Margaret Lusk says. "Everything the mill took and the town took and their wives and their fathers took. You've seen them, Cal. You've seen the men in this town. They were made to carry a hundred pounds of pulp up a ramp ten hours a day, and then one day there's no ramp and no pulp, and they're still made for it. All that strength, with nothing to hold." She sits down. "So I found them something to hold."

"The Kept."

She smiles, pleased, a teacher whose slow pupil has finally gotten it. "You've been listening. Yes. The Kept. They're very lonely, Cal. They're like us. Or they were. And they need a man who can hold one of them long enough to bring it home. That's all. That's all any of it is." She sips her tea. "It's a very great honor."
~ evidence += 1
-> lusk_menu

= ask_walt
"Tell me about my father."

Margaret Lusk sets her cup down. For the first time she looks her age.

"Walter was the first," she says. "Did you know? Before Walter there was just me, and the radio, and my father's notes." She looks at the fire. "He was such a big man. Such a sad man. He'd lost his own father on the ramp at the mill, did you know that, and his brother in Korea, and he had all this grief and nowhere to put it, and he came to the first Fellowship in the spring of '57 and he said, what station is that, Margaret, and I said, it's past the end of the dial."

She folds her hands.

"He couldn't do it. He tried so hard. He couldn't make room. And then your mother took you away, and he had all of it and no room at all, and it went bad in him." She looks at you, and her eyes are wet. "I was so sorry, Cal. I was so sorry about Walter. I sat with him that last night. I held his hand."

"You were there. The night he died."

"Someone had to be," Margaret Lusk says gently.
# note:Lusk sat with my father the night he hanged himself. "Someone had to be." He was the first. Before him it was "just me and the radio and my father's notes." Her father's notes. Who was her father?
~ hurt(2)
~ evidence += 1
-> lusk_menu

= ask_families
"Wes Harlan killed his wife and two kids, Margaret. Lyle Dorsey killed two kids. Dale Pruitt killed his mother and his brother. Eight families since 1957. Twenty-six people."

"Twenty-seven," Margaret Lusk says quietly. "You're forgetting Mr. Kowal's mother-in-law. She was visiting." She shakes her head. "Those men weren't strong enough. That isn't their fault. When a man can't hold it, it goes bad in him, and he does what a frightened man does. He makes room the only way he can think of." She picks up her cup. "It's terrible. Of course it's terrible. That's why we keep trying. If we stop now, all of them died for nothing."

She means it. You've sat across from a lot of people who were lying to you. She isn't one of them.
# evidence:ev_lusk_families;statement;Margaret Lusk, on the families;"Twenty-seven. If we stop now, all of them died for nothing." She means it.
~ evidence += 1
~ hurt(1)
-> lusk_menu

= big_table
~ read_history = true
# evidence:ev_transmitter;statement;Ostrander Paper Gazette, 1956;Mill installs two-way radio for the yard. Transmitter in the water tower, designed by chief radio engineer Harold Lusk. Pictured: Harold Lusk and daughter Margaret, 34.
The big oak table has a stack of bound volumes on it, the Ostrander Paper Company Gazette, the mill's own newsletter, 1950 to 1984. One is open, as if somebody wanted you to see it.

April 1956. NEW TWO-WAY RADIO FOR YARD AND RIVER CREWS. A photograph: a man in a bow tie and shirtsleeves standing on the catwalk of the water tower beside a squat steel cabinet, one hand on it, proud. The caption: Chief radio engineer Harold Lusk with the new transmitter, which will broadcast on a frequency above the commercial band for the exclusive use of the mill. Mr. Lusk is assisted by his daughter, Miss Margaret Lusk.

Margaret, at thirty-four, on the catwalk behind him, in a trench coat, holding a clipboard. Not smiling for the camera. Looking at the cabinet.

Under it, a smaller item, three months later: HAROLD LUSK, 61, CHIEF RADIO ENGINEER, DIES. Found in the transmitter shed. Heart. Mr. Lusk was a widower. He is survived by his daughter.
# note:Mill Gazette, 1956. Harold Lusk, mill radio engineer, built a transmitter in the WATER TOWER on a frequency above the commercial band. Margaret was his assistant. He died in the transmitter shed three months later. Then 1957, Fellowship. The transmitter is still up there. The red light.
~ evidence += 2
-> lusk_menu

= watch_jo
Jo is standing by the card catalog with her back to it, very straight, her hands at her sides. The way you stand in a choir loft.

She's humming. Out loud now. Margaret Lusk is watching her with the same pleased look she gave you.

"She has a lovely voice," Margaret says. "Frank had a lovely voice. He held his for four years, Cal. Four years, and he never once raised a hand. He just got quieter and quieter, and one night he went to sleep. He was very nearly enough." She smiles at Jo. "It runs in families, you know. Strength. It's in the blood."
+ [Get Jo out of the room]
    You put yourself between Jo and the old woman, and you take Jo by the elbow, and you walk her out into the front hall, past the returns desk, to the door. She comes like a sleepwalker.
    At the door she blinks, hard, and shakes her head like a dog coming out of a lake.
    "What," she says. "What was I. Was I singing?"
    "You were humming."
    "God," Jo says. "God. Okay. I'm going to wait in the car. Is that okay? I'm going to wait in the car."
    ~ jo_hums = MAX(jo_hums - 2, 0)
    ~ mercy += 2
    ~ resolve += 1
+ [Let her be]
    You let her be. Jo hums. The fire pops. Margaret Lusk closes her eyes and listens to her like music on a Sunday afternoon.
    ~ jo_hums += 2
- -> lusk_menu

= lusk_asks
Margaret Lusk sets her cup in its saucer without a sound.

"May I ask you something, Cal? Just between us." She leans forward. "How many at home?"
+ [Tell her the truth: one]
    "One," you say. "I live alone. It's one."
    "One," she repeats, and something in her face lights up from the inside. "One is enough. I told your mother that. I told her one is enough." She sits back. "A man who lives alone has all the room in the world."
    ~ lusk_number = "one"
    ~ attunement += 2
    ~ hurt(1)
+ [Tell her three: you, Nora, Paula]
    "Three," you say. "Me. My daughter. Her mother."
    Margaret Lusk looks at you over her reading glasses with great tenderness.
    "Oh, Cal," she says. "You don't live with them. You know you don't. You can't count people you don't go home to." She pats your hand. "But it's sweet that you'd want to."
    ~ lusk_number = "three"
    ~ resolve -= 1
    ~ mercy += 1
+ [Say nothing. Keep your head down.]
    You say nothing. You look at the tea in your cup, the little island of light from the lamp floating on it, and you keep your head down, and you don't let her see your face.
    Margaret Lusk waits. Then she laughs, softly, delighted.
    "Ruth," she says. "Oh, that's Ruth. She taught you that." She sits back. "It won't help, dear. It didn't help Walter. We'd already heard you."
    ~ lusk_number = "none"
    ~ resolve += 2
- -> lusk_menu

= lusk_leave
"I have to go, Margaret."

"Of course." She stands. "The men will be at the mill tonight. Midnight. Everyone will be there. It would mean so much to them if you came." She takes something from her cardigan pocket and puts it in your hand: a key, old, iron, on a loop of red stole ribbon. "The mill office. So you won't have to break anything. You've broken enough doors today."

You look at the key. You put it in your pocket. You don't know why.
# evidence:ev_mill_key;object;Mill office key;Iron, on a loop of red stole ribbon. From Margaret Lusk. "Midnight. Everyone will be there."
# item:keys
~ evidence += 1
-> act3_hub
