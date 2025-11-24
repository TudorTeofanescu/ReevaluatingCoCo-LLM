# CoCo Analysis: ahkegepjekjppmhajnhaiodhfmgemdag

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 6 (all sending attacker data to hardcoded backend URL)

---

## Sink: cs_window_eventListener_message → XMLHttpRequest_post_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ahkegepjekjppmhajnhaiodhfmgemdag/opgen_generated_files/cs_0.js
Line 481		window.addEventListener("message", (event) => {
Line 482			if(event.data.source != "page"){
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ahkegepjekjppmhajnhaiodhfmgemdag/opgen_generated_files/bg.js
Line 1008					currentUser = message.userId
Line 1264		http.send(JSON.stringify(params));

(Multiple similar flows detected with different message fields: userId, enroleeId, auditorId, link)

**Code:**

```javascript
// Content script (cs_0.js, lines 481-503)
window.addEventListener("message", (event) => {
    if(event.data.source != "page"){ // ← attacker-controlled
        return
    }

    switch (event.data.type) {
        case "START SESSION":
        case "START ENROLLMENT SESSION":
        case "TRIAL MATCH":
        case "FINALIZE":
            changeStatusText("Connecting to 1Rotary Servers")
            background.postMessage(event.data) // Forward to background
            break;
        // ...
    }
})

// Background script (bg.js, lines 1003-1040)
contentScript.onMessage.addListener(
    function(message){
        if(message.type == "START SESSION"){
            currentAction = message.action
            currentUser = message.userId // ← attacker-controlled
            // ...
            sendProbeRequest()
        }
        else if (message.type == "START ENROLLMENT SESSION"){
            currentAction = message.type;
            currentUser = message.enroleeId; // ← attacker-controlled
            sendStartEnrollmentProcessRequest(message);
        }
        else if (message.type == "FINALIZE"){
            currentAction = message.type;
            sendSaveRequest(message.link) // ← attacker-controlled
        }
    }
)

// Background script - sendProbeRequest (line 967, 1094, 1264)
var phpBiometricEndpoint = "https://www.arwan.biz/acrossyrs/framfiles/biometrics.php";

function sendProbeRequest() {
    var http = new XMLHttpRequest();
    var params = ({
        extensionId: chrome.runtime.id,
        userId: currentUser, // Contains attacker-controlled data
        // ...
    })
    http.open('POST', phpBiometricEndpoint, true); // Hardcoded backend URL
    http.setRequestHeader('Content-type', 'application/json');
    http.send(JSON.stringify(params)); // Sink
}
```

**Classification:** FALSE POSITIVE

**Reason:** All flows send attacker-controlled data TO a hardcoded backend URL (`https://www.arwan.biz/acrossyrs/framfiles/biometrics.php`). This is the developer's trusted infrastructure. According to the methodology, data TO hardcoded backend URLs is considered trusted infrastructure, not a vulnerability. Compromising the developer's backend server is a separate infrastructure issue, not an extension vulnerability.
