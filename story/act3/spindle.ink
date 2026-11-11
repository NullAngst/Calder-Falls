// ============================================================
// Chapter 9. Act III: the Spindle. Ray Tolliver has started counting.
// Reach him in time, or don't.
// ============================================================

VAR ray_radio_off = false
VAR carol_called = false
VAR ray_talking = false
VAR spindle_visits = 0

=== spindle_start ===
# chapter:9:The Spindle
# theme:static
# music:the_spindle
# map:spindle
# hint:Three things stop Ray: get him talking, kill the radio behind the bar, and get his family out of the house. Pointing a gun at him is not one of them.
~ spindle_visits += 1
The Spindle's door is unlocked now. The Schlitz sign buzzes. The jukebox is playing something with a shuffle beat and a walking bass line, a bar record, the kind that's been on the jukebox since 1971 because nobody ever thought to take it off.

Ray Tolliver is behind the bar, wiping the same glass. Up close he's bigger than he looked through the window, a heavy man with a gray crew cut and forearms like a longshoreman's, a towel over one shoulder, a St. Christopher medal at his throat. His eyes are red. He's been crying, or not sleeping, or both.

There's a radio on the back bar between the Seagram's and the Canadian Club. A clock radio, almond plastic, with a gold foil sticker on top. It's on, very low. Not music. People saying their numbers.

"We're closed," Ray says, without looking up. "Closed for choir."

Jo stays by the door, her hand near her holster, not on it. She knows him. Everybody knows Ray.
-> spindle_bar

=== spindle_bar ===
# music_tempo:{spindle_tempo()}
{ ray_radio_off && carol_called && ray_talking:
    -> ray_saved_scene
}
+ {not ray_talking} [Sit at the bar and talk to him] -> ray_talk
+ {not ray_radio_off} [Do something about the radio] -> ray_radio
+ {ray_talking && not carol_called} [Use the payphone by the restrooms] -> ray_carol
+ [Draw your pistol on him] -> ray_gun
+ [Play something on the jukebox] -> jukebox
+ {cigarettes > 0} [Smoke a cigarette at the bar] -> smoke -> spindle_bar
+ {jukebox} [Leave] -> act3_hub
+ {not jukebox} [Leave @@ Play something on the jukebox] -> jukebox

=== function spindle_tempo() ===
// The record gets slower every visit. The file stays at 90 bpm.
{ spindle_visits:
- 1: ~ return "1.0"
- 2: ~ return "0.85"
- else: ~ return "0.7"
}

=== ray_talk ===
You sit on a stool. The vinyl is cracked and taped. You put your hands flat on the bar where he can see them.

"Ray. I'm Cal Brennick. State police."

"I know who you are." He puts the glass down, finally, and picks up another one. "Margaret said you'd come. She said you were the strong one. She said you'd held a house for twenty-nine years without going in." He looks at you for the first time. "That true?"
+ {tapes_heard >= 3} [Tell him you heard his tape]
    "I heard your tape, Ray. September. You told her you didn't want to make room."
    The glass stops moving.
    "That was private," he says. "That was Fellowship."
    "You said Carol. You said Tyler."
    Ray puts the glass down very carefully, the way you put down something you're afraid you'll throw.
    "He's four," Ray says. "Tyler. He's four years old. His mom's in Florida with some guy. He calls me Pop." He grips the edge of the bar. "Every night that radio says three. I lie there and it says three and I say it back, and Carol's asleep next to me, and the boy's in the next room in the bed I built him, and I say three. And it's getting easy. It's getting easy, mister."
    ~ ray_talking = true
    ~ mercy += 1
    ~ evidence += 1
+ {mill_street_in} [Tell him about your father]
    "My father was the first one, Ray. 1957. Walt Brennick. My mother got me out the morning of. He hanged himself in the garage that night because he couldn't do it and he couldn't stop wanting to." You take a breath. "I went in the house today. First time. He was at the sink, counting. Still. Twenty-nine years."
    Ray looks at you for a long time.
    "Walt Brennick," he says. "My dad knew a Walt Brennick." He wipes his face with the bar towel, roughly, like he's wiping a counter. "Okay. Okay. What do I do?"
    ~ ray_talking = true
    ~ resolve += 1
    ~ mercy += 1
+ [Tell him it's an investigation and he'd better cooperate]
    "This is a homicide investigation, Mr. Tolliver. Eight families. I need you to tell me about the choir."
    "Homicide," Ray says. He laughs, a short ugly sound. "Sure. Write it on your form." He goes back to the glass. One six one zero, his mouth says. Three.
    ~ resolve -= 1
- -> spindle_bar

=== ray_radio ===
The clock radio sits on the back bar, saying numbers in a lot of soft voices.
+ [Pull the plug]
    You reach over the bar and follow the cord down to the outlet and pull the plug.
    The radio keeps playing. The numbers keep coming, a little louder now, as if offended.
    Ray watches you with no expression at all. "Did that, too," he says. "Week ago."
    ~ hurt(1)
    -> ray_radio
+ [Smash it with the flashlight]
    You bring the Kel-Lite down on it overhand, the way you'd bring it down on an arm holding a knife. The plastic case splits. The cards fly. You hit it again and the speaker comes loose on its wires, and it's still talking, so you hit it again, and again, and the voices go to a crackle, and a hiss, and nothing.
    The bar is very quiet. The jukebox has stopped between songs.
    Ray is staring at the pieces. His face is doing something complicated.
    "Okay," he says, finally, in a voice like a man coming up out of anesthesia. "Okay. Huh. That's the first time in two months I haven't heard it."
    ~ ray_radio_off = true
    ~ resolve += 1
    ~ hurt(1)
+ {rounds > 0} [Shoot it]
    You draw and you put one round through the almond plastic from four feet away. The noise in the little bar is enormous. The radio jumps off the back bar and hits the floor in two pieces and lies there, sparking, saying nothing.
    Ray has both hands up over his ears. Jo has her gun out, pointed at the floor, her eyes very wide.
    "Jesus," Jo says. "Jesus, Cal. Warn somebody."
    ~ rounds -= 1
    ~ ray_radio_off = true
    ~ hurt(2)
+ [RADIO:1610: Listen to it first]
    # speaker:1610
    "Hello, Cally. Raymond is almost ready. Isn't it nice? He fought so hard. They always fight, the good ones." A pause. "You could let him finish. You could sit right there and have a drink and let him go home at closing. Nobody would blame you. You've had such a long day."
    ~ attunement += 2
    -> ray_radio
- -> spindle_bar

=== ray_carol ===
The payphone is between the doors marked BUOYS and GULLS. Ray gives you the number without being asked. His hands are shaking now. That's good. That means he's here.

It rings twice.

"Hello?" A woman, sixties, sleepy, a TV on in the background. "Ray? Is that you? Are you closing up?"

"Mrs. Tolliver, my name is Sergeant Brennick, state police. Ray's all right. He's right here. I need you to do something for me."
+ [Tell her the truth]
    You tell her. Not all of it. Enough of it. The choir, the radio, the families. You hear her stop breathing on the other end. You hear the TV go off.
    "I knew," Carol Tolliver says, in a small voice. "I knew something was. He talks in his sleep now. He counts." A pause. "What do I do?"
    "Take Tyler to your sister's. Tonight. Right now. Don't pack. Don't turn on the radio in the car."
    "Hollis," she says. "My sister's in Hollis." You hear keys. "Is Ray coming?"
    You look at Ray. He's holding on to the bar.
    "Not tonight," you say. "He'll call you in the morning."
    ~ carol_called = true
    ~ mercy += 2
+ [Tell her there's a gas leak]
    "There's been a report of a gas leak on your street, ma'am. I need you and your grandson out of the house right away. Go to a relative's, out of town if you can."
    "A gas leak? Ray, is that." A pause. "All right. All right, we'll go to Doreen's in Hollis."
    She hangs up. It worked. It didn't feel like anything.
    ~ carol_called = true
    ~ mercy += 1
- -> spindle_bar

=== ray_gun ===
{ rounds <= 0:
    You reach for your pistol and remember it's empty. Your hand stays on the grip anyway.
    -> spindle_bar
}
You draw and level the pistol at Ray Tolliver's chest across the bar.

"Hands where I can see them, Ray."

Something goes out of his face, and something else comes in, something that's been waiting behind it.
# speaker:1610
"Three," Ray says, in a voice that is a lot of voices. He reaches under the bar.
+ [Fire]
    You fire.
    The round takes him in the chest and he sits down hard on the duckboards behind the bar, and what's in his hand clatters on the floor: a bar knife, a cheap one, for limes.
    He looks up at you. It's just Ray's face now. Just Ray, surprised.
    "I wasn't," he says. "I was getting the towel. I wasn't going to."
    He doesn't say anything else.
    Jo is staring at you from the door. She doesn't say anything either. She doesn't have to.
    # theme:dead_signal
    ~ rounds -= 1
    ~ shot_person = true
    ~ mercy -= 10
    ~ resolve -= 3
    ~ ray_dead = true
    ~ hurt(5)
    # note:I shot Ray Tolliver. He had a lime knife. He said he wasn't going to. I don't know. I'll never know.
    -> spindle_leave
+ [Lower the gun]
    You lower the gun. You holster it. Your hands are shaking so badly the snap takes three tries.
    Ray's hand comes out from under the bar with a towel in it. Just a bar towel. He drops it on the bar between you.
    "I wasn't," he says. "I wasn't going to."
    "I know," you say. You don't know.
    ~ resolve += 1
    ~ hurt(2)
    -> spindle_bar

=== jukebox ===
The jukebox is a Seeburg with a chrome front. Every selection card is typed in the same neat hand. Every song on every card is the same title, a hundred times over, A sides and B sides.

ONE SIX ONE ZERO.

You put a quarter in anyway. B7. The record drops. It's the bar record again, the shuffle, a little slower than before.
~ hurt(1)
-> spindle_bar

=== ray_saved_scene ===
# music_tempo:1.0
# music:substation
Ray comes around the end of the bar. He takes his apron off and folds it and puts it on a stool, and he takes the towel off his shoulder and puts it on top of the apron, and he stands there in his shirtsleeves, looking at the pieces of the radio on the floor.

"It's quiet," he says.

"Jo's going to take you to the substation," you say. "There's coffee. There's a cot. You stay there. You don't go home, you don't go to church, you don't turn anything on that has a speaker in it."

"Till when?"

"Till morning."

"Is there going to be a morning?" Ray asks, not like a joke.

You don't answer. Jo takes his arm, gently, the way you'd take an old man's arm on ice, and walks him out to the Gran Fury. You watch her put him in the back, and lean in and say something to him, and he nods.

She comes back in alone.

"He'll stay," she says. "He's not going anywhere. He's just sitting there. He looks about ten years younger." She looks at you. "That was good, Cal. That was real good."
# note:Ray Tolliver: radio dead, Carol and Tyler on the way to Hollis, Ray at the substation. He said it's quiet. One family that didn't go into the ledger.
~ ray_saved = true
~ mercy += 3
~ resolve += 2
~ steady(3)
-> spindle_leave

=== spindle_leave ===
# music:fellowship
You go out to the street. The Schlitz sign in the window goes dark behind you, and the jukebox stops mid-note, and the Spindle is just a closed bar on a closed street in a town with no one in it.
-> act3_hub
