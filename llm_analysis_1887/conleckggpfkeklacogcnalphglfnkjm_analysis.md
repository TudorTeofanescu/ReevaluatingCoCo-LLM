# CoCo Analysis: conleckggpfkeklacogcnalphglfnkjm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 8 (all storage.sync.set from bg_chrome_runtime_MessageExternal)

---

## Sink: bg_chrome_runtime_MessageExternal → chrome_storage_sync_set_sink

**CoCo Trace:**

All 8 detections follow the same pattern from external messages to storage:

```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/conleckggpfkeklacogcnalphglfnkjm/opgen_generated_files/bg.js
Line 972-979: Storage.sync.set with multiple fields from request object
```

The fields detected are:
1. Line 972: `selectedDays: request.selectedDays`
2. Line 973: `startTime: request.startTime`
3. Line 974: `finishTime: request.finishTime`
4. Line 975: `intervalMinutes: request.intervalMinutes`
5. Line 976: `selectedExercises: request.selectedExercises`
6. Line 977: `userID: request.userID`
7. Line 978: `active: request.active`
8. Line 979: `plan: request.plan`

**Code:**

```javascript
// Background script - External message handler (line 1175)
chrome.runtime.onMessageExternal.addListener((request, sender, sendResponse) => {
    const handler = messageHandlers[request.action]; // ← attacker-controlled action
    if (handler) {
        handler(request); // ← calls updatePreferences with attacker data
        sendResponse({ status: "done" });
    }
});

// Message handler (line 969-982)
const messageHandlers = {
    updatePreferences: (request) => {
        chrome.storage.sync.set({
            selectedDays: request.selectedDays,        // ← attacker-controlled
            startTime: request.startTime,              // ← attacker-controlled
            finishTime: request.finishTime,            // ← attacker-controlled
            intervalMinutes: request.intervalMinutes,  // ← attacker-controlled
            selectedExercises: request.selectedExercises, // ← attacker-controlled
            userID: request.userID,                    // ← attacker-controlled
            active: request.active,                    // ← attacker-controlled
            plan: request.plan                         // ← attacker-controlled
        });
    }
};

// Storage retrieval - data sent to hardcoded backend (line 1108-1115)
chrome.storage.sync.get(['userID', 'plan'], function(data) {
    if (data.userID) {
        getRandomExercise((exercise) => {
            if (exercise) {
                createNotification(data.userID, exercise.id); // ← sends to backend
            }
        });
    }
});

// Backend communication - hardcoded URL (line 1083-1090)
function createNotification(userID, exerciseID) {
    fetch('https://eof4we1qadd5ut6.m.pipedream.net', { // ← hardcoded backend URL
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userID, exerciseID: exerciseID })
    })
}
```

**Classification:** FALSE POSITIVE

**Reason:** While external messages can trigger storage poisoning, the stored data is only retrieved and sent to the developer's hardcoded backend URL (`https://eof4we1qadd5ut6.m.pipedream.net`). This is trusted infrastructure - compromising the developer's backend is a separate concern from extension vulnerabilities. The attacker has no mechanism to retrieve the poisoned data back (no sendResponse with stored data, no attacker-controlled fetch URLs). Per the methodology: "Data TO hardcoded backend: attacker-data → fetch('hardcoded URL')" is FALSE POSITIVE.
