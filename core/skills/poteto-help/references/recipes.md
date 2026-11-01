# Prompts worth copying

Swap in the real paths and done checks. Informal wording works. These prompts stay on the skills shipped in this slice.

## Understand

- `mstack read <thread>. restate the underlying issue in your own words, in plain english. don't change any code yet.`
- `mstack <symptom>. tell me what we know, what you read, and your best hypotheses. don't change any code yet.`

## Build

- Bug: `mstack <symptom>. repro first, then fix and verify.`
- Bug with a cheap test: `mstack repro <bug> first. write the failing test before the fix when that test is cheap. then fix and rerun.`
- The bug-fix playbook keeps cheap failing-test-first and skips that test when it would be impractical or expensive. It does not call the tdd skill.

## Away and back

- `mstack im stepping away. <goal>. done means <checks>. request overnight mode until with that done check. if you're truly stuck, stop and write up why.`
- `mstack what changed while I was away. name the evidence.`

## Steer

- `i said the goal is to repro. i did not ask for a fix yet.`
- `apply prove it works. show me the real output.`
- `new task. <next goal>.`
