# CoCo Analysis: egmkjljocjiilghgjemeknhmgliloiii

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (user_id and time to storage)

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/egmkjljocjiilghgjemeknhmgliloiii/opgen_generated_files/cs_0.js
Line 580: `window.addEventListener("message", function(event) {`
Line 586: `if (event.data.type && (event.data.type == "READ_MSG")) {`
Line 587: `console.log('read mesage', event.data.data)`
Line 592: `READ_MSG[message_data.user_id] = message_data.time`

**Code:**

```javascript
// Content script (cs_0.js) - Lines 580-600
window.addEventListener("message", function(event) {
  // We only accept messages from ourselves
  if (event.source != window)  // ← This check does NOT prevent attacks
      return;                   // Attacker webpage can pass this check

  // Save last read message on storage
  if (event.data.type && (event.data.type == "READ_MSG")) {
    console.log('read mesage', event.data.data)
    let message_data = event.data.data  // ← attacker-controlled
    chrome.storage.local.get(['READ_MSG'], function(res) {
      var READ_MSG = res['READ_MSG']?res['READ_MSG']:{};

      READ_MSG[message_data.user_id] = message_data.time  // ← attacker-controlled values

      chrome.storage.local.set({READ_MSG: READ_MSG}, function() {
        // Update the page mailbox, and present the result
        updateMailbox(message_data)
      });
    })
  }
});

function updateMailbox(message_data) {
  if(window.location.href.includes('mailbox') && window.location.href.includes(message_data.user_id)){
    $('#ext-msg-holder').remove()
    $('#chat_ta').prepend(`<p id="ext-msg-holder">${message_data.time}</p>`)
  }
}
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While an attacker webpage can trigger the flow via `window.postMessage({type: "READ_MSG", data: {user_id: "evil", time: "malicious"}}, "*")` (the `event.source != window` check is not a security boundary as content scripts run in page context), there is no retrieval path for the attacker to read back the poisoned storage data. The data is:
1. Stored in chrome.storage.local (attacker cannot directly access)
2. Written to DOM via updateMailbox (but attacker already controls the webpage DOM)

The storage poisoning provides no exploitable impact - the attacker cannot retrieve the stored values through sendResponse, postMessage back to attacker, or any other mechanism. According to the methodology Pattern Y: Incomplete Storage Exploitation - storage.set without retrieval path to attacker is FALSE POSITIVE.
