# Word the prompt

A prompt states the intent and the check for done. The playbook supplies the steps, so a few plain sentences beat a spec.

## Put in

- The goal. Say what is wrong or what the user wants.
- The done check. It can pass or fail. "Make it better" and a duration are not checks.
- The proof to show. Ask for the real command output, the stored value, or a before and after number.
- What the user already knows. A symptom, a repro step, a log, or a link saves a search.
- The real constraints. "repro first", "don't change any code yet", "zero behavior change", and "let me review before proceeding" each change what the agent does.

## Leave out

- The how. Say what to achieve, and leave room to find a better way.
- A list of skills or steps. A hand-written order drops or reorders steps the playbook keeps. Name a skill only to override one choice.
- The user's theory of the cause, until the problem is restated. A stated guess narrows the search.

## Load the context first

- For a noisy report, restate the underlying issue in plain words before changing anything.
- Read the code the request names, and read the playbook that owns the work, before editing.
- On this slice the included procedures are the router, bug-fix, no-comments, figure-it-out, correct, and the principle skills. Do not route to a skill that is not in core.

## Follow up short

- "do it", "continue", and "keep going until done" are whole prompts once the chat holds the task.
- Start with "new task" when the subject changes. Otherwise the next message is treated as the next step.

## Before stepping away

- Say "im stepping away" so the run stops asking.
- Write done as checks a later pass can run. A long hunt requests overnight mode until with that done condition.
- Ask for a fresh worktree off a named base when the run must not share the current tree.
- Pre-answer what the run would stop for, such as "don't ask me before committing".
- Ask for a decision log to audit later.
- Give an exit: "if you're truly stuck, stop and write up why".

## Steer in one line

- Restate the goal: "i said the goal is to repro. i did not ask for a fix yet."
- Name the principle: "apply prove it works. show me the real output, not the build log."
- A principle name works because the playbook already read the rule. The reply names the decision the rule changed.
