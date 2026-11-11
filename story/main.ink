// Calder Falls
// Main story file. inklecate compiles this, and it pulls in every chapter.
// Writing conventions are in story/README-ink.md.

INCLUDE prologue.ink
INCLUDE act1/hallway.ink
INCLUDE act1/lights_on.ink
INCLUDE act1/lights_off.ink
INCLUDE act1/flashlight.ink
INCLUDE act2/hush.ink
INCLUDE act2/pruitt.ink
INCLUDE act2/dorsey.ink
INCLUDE act3/adalberts.ink
INCLUDE act3/spindle.ink
INCLUDE act3/precentor.ink
INCLUDE act4/tower.ink
INCLUDE act4/mill_floor.ink
INCLUDE act4/endings.ink

// ------------------------------------------------------------ visible state
VAR nerve = 10          // 0..10, shown in the top strip
VAR rounds = 6          // service pistol
VAR cigarettes = 7

// ------------------------------------------------------------ hidden, long-term
VAR resolve = 0         // how you hold up
VAR attunement = 0      // how much you listen to 1610 and do what it says
VAR mercy = 0           // who you save
VAR evidence = 0        // how much of the truth you actually built

// ------------------------------------------------------------ set by the game
VAR second_run = false
VAR theory_score = 0

// ------------------------------------------------------------ story flags
VAR loop = 0
VAR june_near = 0       // how close June is in the hallway, 0..5
VAR wrong_theories = 0
VAR told_okafor_truth = false
VAR okafor_gone = false // the voice on the police band is not her any more
VAR houses_closed = 0
VAR pruitt_closed = false
VAR dorsey_closed = false
VAR ada_trusts = false
VAR mill_street_in = false
VAR ray_saved = false
VAR ray_lost = false
VAR ray_dead = false
VAR jo_saved = false
VAR jo_with_you = false
VAR lusk_met = false
VAR ledger_read = false
VAR transmitter_damaged = false
VAR called_ruth = 0
VAR shot_person = false
VAR vessel = ""         // who the choir sings into: ray, jo, you

-> prologue

// ------------------------------------------------------------ helpers

=== function hurt(n) ===
~ nerve = MAX(nerve - n, 0)

=== function steady(n) ===
~ nerve = MIN(nerve + n, 10)

=== function partial(score, total) ===
// Partial credit on a theory still counts toward the truth you built.
~ evidence += score
{ score == total:
    ~ evidence += 1
}

// Light one. Tunnel: -> smoke ->
=== smoke ===
{ cigarettes > 0:
    ~ cigarettes -= 1
    ~ steady(3)
    {&You shake one out of the pack and light it with the Zippo you never fill all the way. The first drag does what it always does.|You light one. Your hand is steadier than it was a minute ago, which is the whole point of the thing.|The lighter takes three tries. The smoke tastes like the inside of the cruiser.|You smoke it down to the filter without thinking about anything at all. That is the best minute you have had today.|You light one and hold it, mostly. The ember is the warmest thing in the room.|You count what's left in the pack before you can stop yourself. Then you light one anyway.|Last one. You smoke it slowly, like that will make it last.}
    ~ temp left = cigarettes
    { left == 0:
        The pack is empty now. You fold it flat and put it in your coat.
    }
- else:
    You pat your coat for the pack and find it folded flat. You knew that. You checked anyway.
}
->->

// Sit down a minute. Tunnel: -> rest ->
=== rest ===
~ steady(2)
{&You sit on the nearest hard surface and let your eyes close for a count of ten. Nothing happens in the dark behind your eyelids. You are almost disappointed.|You lean your back against the wall and breathe the way the department shrink told you to, in for four, out for four. It works about as well as it did then.|You rest. Your knees thank you. Your watch does not move while you do it, and you decide not to think about that.}
->->
