# CoCo Analysis: nenflolfcmpfejdelljajnleghondpoa

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nenflolfcmpfejdelljajnleghondpoa/opgen_generated_files/cs_0.js
Line 468	window.addEventListener('message', (event) => {
Line 470	if (event.data.type && event.data.type == 'htnini' && event.data.key && event.data.value) {
Line 470	event.data.value

**Code:**

```javascript
// Content script (cs_0.js / site.js) - Lines 467-475
let runtime = typeof chrome == 'object' ? chrome : browser;
window.addEventListener('message', (event) => {  // ← attacker-controlled via postMessage
    if (event.source != window) return;
    if (event.data.type && event.data.type == 'htnini' && event.data.key && event.data.value) {
        let msg={}; msg['htnini.website.'+event.data.key] = event.data.value;  // ← attacker-controlled key/value
        runtime.storage.local.set(msg);  // ← storage poisoning
    }
});
runtime.storage.local.get((r) => {document.getElementsByTagName('html')[0].setAttribute('data-htnini-hash', btoa(r[atob('aHRuaW5pLnVzZXIua2V5')]));});

// Other content script (cs_1.js) reads some of these keys - Line 2040-2061
if (window.HTnini.storage.get('htnini.website.anniv4.finished')==1) {
    this.cleanStorage();
}
// Used in URL matching pattern
if (window.location.pathname == '/Club/Players/Player.aspx' &&
    window.location.search.match(new RegExp('playerid='+window.HTnini.storage.get('htnini.website.anniv4.witness')+'(?=&|$)','i'))) {
    this.startWitness();
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - attacker can store arbitrary key-value pairs with 'htnini.website.' prefix, but this data never flows back to the attacker via sendResponse, postMessage, or other attacker-accessible output. The stored values are only used internally for extension logic.
