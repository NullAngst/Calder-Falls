// ============================================================
// Chapter 2. Act I: Cobb Road, lights on. Loops 1 to 4.
// ============================================================

=== lights_on_intro ===
# chapter:2:Cobb Road, lights on
# music:cobb_road
# theme:midnight
# clear
# time:16:20
# hint:Look at everything once. Then walk to the kitchen door at the end of the hall.
You've walked a lot of houses. You walk them the same way every time: stop inside the door, don't touch anything, let your eyes do the work before your feet do. Let the house tell you what it wants to tell you before you start asking it questions.

This house tells you it is warm, and clean, and that somebody vacuumed this morning, because the plastic runner over the hall carpet still has the stripes from the vacuum on the carpet showing through it.

It tells you that the hallway in front of you is longer than the house.

You stood out on the walk a minute ago and looked at this place. A split-level, maybe forty feet front to back. The hall in front of you goes back sixty feet if it goes back one. You check your watch, out of nothing but habit. 4:20. You look back down the hall. It hasn't gotten any shorter.

Okay. Houses look bigger inside. Everybody knows that. You take out your pad and you write HALL - LONG and you underline it twice, because you don't know what else to do with it yet.
# note:Hallway is longer than the outside of the house. Can't be. Measure it.
-> loop_top.loop_begin

// ------------------------------------------------------------ coats
=== coats_on ===
{ diff == coats:
    -> coats_four
}
{ coats_on == 1:
    Three coats on three brass hooks, the kind you screw into a board and the board into the wall. A woman's tan car coat with an IGA name tag still pinned to the lapel: JUNE, in red plastic letters, and under it, HAPPY TO HELP. A boy's Little League jacket, maroon satin, CALDER FALLS LIONS across the back in white felt. A pink nylon parka, small, the hood trimmed with fur that came off an animal nobody has ever heard of.
    No man's coat. He was wearing it.
    You check the pockets, because that's the job. The car coat has a folded church bulletin in it, today's date, ST. ADALBERT'S PARISH, 11:00 HIGH MASS, and on the back somebody has drawn a tic-tac-toe game in pencil and lost it.
    # evidence:ev_bulletin;statement;Sunday bulletin;St. Adalbert's, 11:00 Mass, Oct 12. In June's coat.
    # note:June's coat: today's bulletin, 11:00 Mass. They went to church this morning. All four?
    ~ evidence += 1
- else:
    The three coats. June's car coat, the name tag, HAPPY TO HELP. Danny's Lions jacket. Beth's pink parka. Same as before.
}
->->

= coats_four
Four coats.
The fourth is on a hook that wasn't there, between June's and Danny's, the brass new and bright where the others are dull. It isn't a coat. It's a robe, black, to the floor, with a white collar and a stole of dark red satin, and pinned to the stole there's a little enamel badge, a pair of musical notes on a staff with short lines above and below it.
You touch the sleeve. It's wet.
# evidence:ev_choir_robe;object;Fourth coat;A choir robe, soaking wet. Enamel pin: notes on a staff, little lines above and below.
~ hurt(1)
->->

// ------------------------------------------------------------ photo
=== photo_on ===
{ diff == photo:
    -> photo_three
}
{ photo_on == 1:
    A five-by-seven in a brass frame from the Rexall. The four of them in front of St. Adalbert's in their church clothes: Wes in a brown suit that pulls across the shoulders, June in a yellow dress with her hand on Beth's head, Beth missing her front teeth, Danny with his tie loosened like he's already in trouble for it. EASTER '86 in June's handwriting on the mat.
    Wes is smiling the way men smile when the photographer has told them to for the third time. Everyone else is smiling at something off to the side.
    # evidence:ev_family_photo;photo;Easter '86;Wes, June, Beth, Danny. St. Adalbert's steps.
    ~ evidence += 1
- else:
    The photo. Easter, the four of them on the church steps. June's hand on Beth's head. Same as before.
}
->->

= photo_three
The photo.
Three of them. June in the yellow dress, her hand on Beth's head. Danny with his loose tie. And beside Danny, where his father stood, the church steps, the brick, the bottom of the door. Nobody.
Not cut out. Not scratched off. The brick behind where Wes was standing is all there, every line of mortar, like the camera never saw him.
You turn the frame over. On the back, in the same handwriting as the mat, it says EASTER '86, and under it, in different ink, pressed so hard it has come through on the front of the paper as a ridge: ONE SIX ONE ZERO, THREE.
# evidence:ev_photo_three;photo;Easter '86, again;Wes is gone from the picture. Back: "one six one zero, three."
# note:Photo now shows three. Wes is gone from it. "Three" on the back. Three left in the house after he went to the truck?
~ hurt(1)
->->

// ------------------------------------------------------------ radio
=== radio_on ===
{ radio_on == 1:
    A GE clock radio, the newer kind with the numbers that flip down on little cards. Almond plastic. It's so new it still smells like the box.
    There's a gold foil sticker on top, the kind a jeweler puts on a watch box. Printed on it in black script:
    A GIFT FROM YOUR BROTHERS
    ST. ADALBERT'S MEN'S CHOIR
    WE ARE GLAD YOU SAID YES
    The tuning needle is all the way at the top of the AM band. You turn it on. Hiss, even and soft, like breathing on the other side of a wall. You turn it off.
    # evidence:ev_radio_gift;object;Clock radio;Gift sticker: "From your brothers, St. Adalbert's Men's Choir. We are glad you said yes."
    # note:Clock radio, a GIFT from the men's choir. Tuned to the top of the dial, same as the truck.
    ~ evidence += 1
- else:
    The clock radio. Almond plastic, the gold sticker. WE ARE GLAD YOU SAID YES. The needle at the top of the dial. Same as before.
}
->->

// ------------------------------------------------------------ clock
=== clock_on ===
{ diff == clock:
    -> clock_stopped
}
{ clock_on == 1:
    A sunburst clock, gold-painted spokes around a white face, the kind that came free with a fill-up at the Sunoco for a while in the sixties. It says 4:20.
    So does your watch. You check twice.
    The second hand goes around. It sounds louder than a clock that size should.
- else:
    The sunburst clock. 4:20. Your watch agrees. The second hand goes around.
}
->->

= clock_stopped
The clock says 3:15.
The second hand is stopped on the twelve, and it is trying to move. You can see it. It strains forward a hair, and falls back, and strains forward, every second, tick, tick, like a finger tapping on glass from the other side.
Your watch says 4:20.
# evidence:ev_clock_315;time;Wall clock, 3:15;Stopped at 3:15. Second hand trying to move.
# note:Hall clock stopped at 3:15. Neighbor came at 12:40. Pell 1:10. So 3:15 isn't the shooting. 3:15 is something else. Okafor: phone call logged at 3:15?
~ hurt(1)
->->

// ------------------------------------------------------------ phone
=== phone_on ===
{ diff == phone:
    -> phone_off_hook
}
{ phone_on == 1:
    A beige wall phone, rotary, with a cord that's been stretched so many times it reaches the kitchen. Beside it, taped to the wall, an index card of numbers in June's round handwriting: IGA, DR. NOVAK, FATHER KASPRZAK, POISON, MOM, and at the bottom, in a different pen, newer, MARGARET L. (CHOIR) and a number.
    # evidence:ev_phone_list;statement;Phone list;June's card of numbers. Newest: "Margaret L. (choir)".
    # note:Phone list: MARGARET L. (CHOIR). Who is Margaret L.? Choir director? Men's choir with a woman for a contact?
    ~ evidence += 1
- else:
    The phone in its cradle. The card of numbers. MARGARET L. (CHOIR). Same as before.
}
->->

= phone_off_hook
The phone is off its cradle, the receiver hanging by its stretched cord, turning slowly a few inches above the runner.
You pick it up.
It's not a dial tone. It's not static. It's a man's voice, close to the mouthpiece, low and patient and very tired, the voice of someone who has said the same thing so many times it has worn smooth.
# speaker:1610
"One six one zero, four. One six one zero, four. One six one zero, four."
You say "Hello." You say "This is the state police." The voice doesn't change. It is not talking to you. It is practicing.
# speaker:1610
"One six one zero, four."
You hang it up. It takes you two tries to get it in the cradle.
# evidence:ev_phone_count;statement;The phone;A man's voice: "One six one zero, four." Over and over. Practicing.
# note:Phone. Man counting. 1610 and four. The truck tape says 1610 - 4. Four people in the house. He was counting THEM.
~ hurt(2)
~ attunement += 1
->->

// ------------------------------------------------------------ living room
=== living_on ===
{ living_on == 1:
    -> living_first
}
{&The living room. The vacuum lines. The TV with the sound down. Three plates. The box on the tray. Same as before.|The living room again. Okafor said they were inside. You stand in the arch and look at the clean carpet until your eyes water.|The living room. The ball game is still in the same inning. It has been in the same inning since you walked in.}
->->

= living_first
Okafor said they were inside.
They aren't.
The living room is clean. The carpet is gold shag and somebody has vacuumed it so carefully that the lines go all the way to the baseboards. The couch has an afghan over the back, orange and brown squares. The TV is on with the sound off, a Zenith in a wood cabinet, the Sunday game, somebody in pinstripes standing on second base.
There are three plates on TV trays in front of the couch, two small and one regular. Ham sandwiches with the crusts cut off the small ones. Potato chips. A glass of milk on each tray. Nobody has touched the milk.
There's a fourth TV tray, folded, leaning against the wall. On top of it there's a box of Remington .38 Special, the lid open. You count without wanting to. Forty-six. It's a box of fifty.
That's what it left. That's all it left. No blood. No sheets. No chalk. You were told there were three people in this room and there is a ball game with no sound and a box of shells with four missing.
You stand in the arch a long time.
# evidence:ev_shells;object;.38 Special, box of 50;On a folded TV tray. Four rounds missing.
# evidence:ev_lunch;object;Lunch on three trays;Three plates, three glasses of milk, untouched. After church.
# note:Living room. NO BODIES. Three lunches. Box of .38, four gone. Okafor walked through this and "couldn't tell me." Now I know what she meant.
~ evidence += 2
~ hurt(2)
->->

// ------------------------------------------------------------ bathroom
=== bathroom_on ===
{ bathroom_on == 1:
    The bathroom door is the hollow-core kind with a brass knob that locks with a push button. You try it. Locked.
    You put your ear against it. Water. A drip, slow, into a lot of water. Like a full tub.
    You knock, which is stupid, and you know it's stupid while you're doing it. Nobody answers. The drip goes on.
    # note:Bathroom locked from inside (Pell said so too). Water dripping into a full tub.
- else:
    The bathroom door. Locked. The drip on the other side of it, slow. Same as before.
}
->->

// ------------------------------------------------------------ children's rooms
=== kids_on ===
{ kids_on == 1:
    -> kids_first
}
The children's rooms. Danny's glove under the bunk. Beth's nightlight, the drawings over her bed. Same as before.
->->

= kids_first
Two doors side by side.
Danny's room is the boy's room of every boy you went to school with: a Pirates pennant, a Lions team photo with his face circled in red marker, a glove with a ball wedged in the pocket and a rubber band around it to break it in, a bunk bed with nobody on the top bunk. Ten years old. You were nine.
Beth's room is yellow, the walls, the bedspread, the curtains. A nightlight shaped like a moon, on. A doll with yarn hair on the pillow. Over the bed, eight or nine drawings in crayon taped to the wall in a row, the way kids do when nobody tells them not to. The house, always the house, with the hoop on the garage. A sun with a face. Mom and Danny and Beth and Daddy, holding hands, all the same height except Daddy.
In the last three drawings there is somebody else. A tall shape beside Daddy, taller than the house, done in black crayon, back and forth and back and forth, a zigzag of a person. In the last drawing Daddy is holding its hand instead of Mom's.
# evidence:ev_beth_drawings;photo;Beth's drawings;Family of four. In the last three, a tall zigzag figure. Daddy holds its hand.
# note:Beth drew someone tall made of zigzag lines standing with her father. Started three drawings ago. When? Ask the school?
~ evidence += 1
~ hurt(1)
->->

// ------------------------------------------------------------ kitchen
=== kitchen_look ===
{ phase():
- 1: -> kitchen_on ->
- 2: -> kitchen_off ->
- 3: -> kitchen_flash ->
}
->->

=== kitchen_on ===
{ kitchen_on == 1:
    The kitchen is yellow linoleum and white cabinets with copper handles shaped like leaves. The table's set for Sunday supper already, four places, which is the saddest thing you've seen today and you've seen a TV tray with a box of shells on it.
    On the refrigerator, under a magnet shaped like a strawberry, one of Beth's drawings: the house again. Beside it the Halvorsen Hardware calendar, OCTOBER 1986, a photograph of a covered bridge in fall. Every Sunday says MASS in June's hand. Every Tuesday and Thursday, in a different hand, a man's, blocky capitals: CHOIR. Every Monday: FELLOWSHIP. Today's square has nothing written in it at all.
    # evidence:ev_calendar;time;Kitchen calendar;Sun MASS. Tue/Thu CHOIR. Mon FELLOWSHIP, in Wes's hand.
    # note:Wes: Monday "Fellowship," Tue and Thu choir. Every week. A man who lost his job, with a schedule. Who runs the Fellowship?
    ~ evidence += 1
- else:
    The kitchen. Four places set for supper. The drawing on the fridge, the calendar. {diff == drawing || diff == calendar:Something here is wrong.|Same as before.}
}
->->

// ------------------------------------------------------------ theories
=== theory_t1 ===
# theory:t1;What happened in this house?
# slot:who;Wes Harlan*@ev_photo_three;June Harlan;Someone from outside the family
# slot:what;He shot his family, then himself in the truck*@ev_shells;A fire that was put out;Gas from the furnace
# slot:when;Sunday afternoon, after the 11:00 Mass*@ev_bulletin;Saturday night;Early Sunday morning
# hint:File what you can support. If an option you expect isn't there, you haven't found what supports it yet.
At the kitchen door you stop, with your hand on the frame, and you take out the pad. This is the part of the job you're good at. You put the house in order on paper before it puts you in order.
+ [FILE: File a theory]
    -> theory_result(3)
+ [Keep looking]
    -> hall

=== theory_t2 ===
# theory:t2;After the house, where did he go, and what was he doing?
# slot:went;To his truck in the drive*@ev_truck_dial;Down to the basement;Out to the mill
# slot:listening;To 1610, the top of the AM dial*@ev_truck_dial;To the Sunday ball game;To the police band
# slot:the number;How many people were in his house*@ev_phone_count;His house number;A hymn number in the bulletin@ev_bulletin
# slot:it ended;At 3:15*@ev_clock_315;At 12:40, when Mrs. Cuddy came;At 1:10, when Pell came
# hint:Think about the truck radio from before you came in, and what the phone said.
The kitchen door. Your pen is already moving.
+ [FILE: File a theory]
    -> theory_result(4)
+ [Keep looking]
    -> hall

// ------------------------------------------------------------ end of chapter 2
=== lights_on_end ===
# music_layer:drums off
You walk to the end of the hall and through the kitchen door.

You are standing with your back to the front door. The hallway runs straight ahead of you.

The ceiling light goes out with a small tink, like a fingernail on a glass.

Not a bulb blowing. You know what a bulb sounds like. This is the sound of somebody reaching up and turning it, a quarter turn, in the socket.

The gray from around the blinds comes up slowly as your eyes adjust. The clock radio on the hall table is a dark box. The house is very quiet. The furnace has stopped.

Far down the hall, in the kitchen, a faucet starts to run.
# pause:2
~ loop = 5
~ repeats = 0
-> loop_top
