# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    The main objects will be Owner, Pet, Task, Schedule

- What classes did you include, and what responsibilities did you assign to each?
    Owner - Will represent the pet owner's profile.
    Pet - The pet that will receive the care.
    Task - What activity the pet will need.
    Schedule - the daily plan for the pet.

**b. Design changes**

- Did your design change during implementation?
    Yes
- If yes, describe at least one change and why you made it.
    I modified the initial skeleton based on the following AI suggestions: 
        assigned_time: str → time	ScheduledTask now uses datetime.time — sortable and comparable

        Owner.start_time added	generate_plan() can now compute actual clock times for each task

        Schedule.skipped_tasks added	Dropped tasks are recorded with a reason — explain() can surface them
        
        _sort_by_priority() comment	Sorting strategy documented: required → priority value → preferred time

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

    One of the tradeoffs is that when generating the plan, it walks the sorted list top to bottom and skips any tasks that doesn't fit the remaining time. For this instance, the tradeoff should be ok since a pet owner typically only has at most a handful of tasks per day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
