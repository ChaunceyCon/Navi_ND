# Plan: Update Flourishing Prompt Skill

## Context

Based on a brainstorming session, the flourishing-prompt skill needs to evolve beyond solo self-care exercises. The key insights: exercises should push users toward **connecting with other people**, the agent should **redirect impulse energy** (not just examine it), exercises should be **simple enough that the agent can't screw them up**, and doing things **with someone else** overcomes the inertia that stops people from doing positive things alone.

## File to Modify

- [SKILL.md](.claude/skills/flourishing-prompt/SKILL.md) — the only file changing

## Changes

### 1. Update frontmatter description (line 3)
Broaden scope to include connection and impulse redirection:
> "Offers self-care, connection, and positive-action exercises scaled from 1-10 minutes when a user is stressed, feeling an impulse to buy, or seeking support."

### 2. Add "redirect the energy" step to Approach (after line 17)
New step 3 before "Offer ONE exercise" (which becomes step 4):
- If the user came from an impulse (wanting to buy, restless energy), name that energy as valid and redirect it: "That urge to do something for yourself is real — let's point it somewhere that actually delivers."
- Channel the impulse into positive action, don't suppress it

### 3. Add new section: "The Over-the-Hump Principle" (between Approach and Exercise Library)
Three-point design principle for how the agent presents exercises:
1. **Make it tiny** — smaller ask = more likely they'll do it
2. **Make it feel good, not virtuous** — frame as "this might be fun," not "studies show this improves well-being"
3. **Connect it to someone else** — doing it with/for another person makes it meaningful and creates gentle accountability

### 4. Add new exercises to each time tier

**1-Minute — "Quick Reach-Out"**
Send a short text to someone you haven't talked to in a while. "Hey, thinking of you" is enough. Ten seconds, changes two people's days.

**5-Minute — "The Two-Person Version"**
Pick any exercise and text a friend to do it together over text. Turns solo exercises into shared ones. Overcomes the "feels cheesy alone" barrier.

**5-Minute — "Positive Impulse Swap"**
Redirect impulse energy into one of three concrete options: text someone you appreciate, take a five-minute walk, or make something with your hands. "Which one sounds least like a chore?"

**10-Minute — "The Shared Activity"**
Think of something you keep meaning to do, then pick someone to invite. Low bar: "Hey, want to [thing] with me this week?" Most people are waiting for someone else to ask first.

### 5. Add new section: "Why These Work" (after Exercise Library, before Transition Points)
Agent-facing background (explicitly marked "don't recite this to the user"):
- **Behavioral activation** — doing almost anything small breaks the inertia cycle
- **Social connection as mood regulation** — brief positive contact reliably improves mood; the barrier is initiation, not desire
- **Impulse surfing** — impulses peak and fade in 15-20 minutes; redirecting beats suppression
- **Gratitude interventions** — naming specific positives produces measurable well-being improvements
- **Helper's high** — doing something for someone else boosts mood more than doing something for yourself

Decision heuristic: lean toward social exercises when the user seems open to it.

### 6. Update Transition Points
Add two new bullets:
- If user came from an impulse and the exercise helped, close naturally: "How are you feeling about [the thing] now?" Don't push.
- If a social exercise got a positive response, build on it: offer `/gratitude-inventory` around the people in their life.

### 7. Add two new Critical Rules
- **Don't force the social angle.** If someone wants to be alone, solo exercises are great.
- **Keep redirect suggestions concrete.** "Text someone, take a walk, or make something" beats "do something positive instead." Vague alternatives lose to specific impulses.

## Verification
- Read the updated file and confirm all existing exercises are preserved
- Test the skill by invoking `/flourishing-prompt feeling stressed about wanting to buy new clothes` and verifying the agent uses the redirect-impulse framing and offers a social/connection exercise
- Check that the tone stays grounded and non-preachy
