# CoCo Analysis: phnpkckppepelhahjbjoookeeoeffhhg

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2

---

## Sink 1: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/phnpkckppepelhahjbjoookeeoeffhhg/opgen_generated_files/cs_0.js
Line 536: window.addEventListener("message", (event) => {
Line 540: if (event.data.sender=='Meta') {
Line 541: MM.request(event.data.data);
Line 557: MM.mods.push(data.mod);

**Code:**

```javascript
// Content script - cs_0.js
window.addEventListener("message", (event) => {
    if (event.source !== window) {
        return;
    }
    if (event.data.sender=='Meta') {
        MM.request(event.data.data); // ← attacker-controlled data
    }
});

MM.request = function(data) {
    if (data.req) {
         if (data.req=='add mod') {
            MM.mods.push(data.mod); // ← attacker-controlled
            MM.saveData();
            MM.send({req:'update mods', mods:MM.mods});
         }
    }
};

MM.saveData = function(){
    browser.storage.local.set({
        data: {
            modless: MM.modless,
            mods: MM.mods // ← attacker-controlled data written to storage
        }
    });
}
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - no retrieval path to attacker. The webpage can send postMessage with sender='Meta' to poison the MM.mods array in storage, but examining the code shows the stored mods are only sent back to the webpage via window.postMessage (MM.send function), not via any external message response. Since the attacker (webpage) already controls what they're sending, retrieving it back doesn't create additional exploitable impact.

---

## Sink 2: cs_window_eventListener_message → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/phnpkckppepelhahjbjoookeeoeffhhg/opgen_generated_files/cs_0.js
Line 536: window.addEventListener("message", (event) => {
Line 540: if (event.data.sender=='Meta') {
Line 541: MM.request(event.data.data);
Line 562: MM.mods=data.mods;

**Code:**

```javascript
// Same flow as Sink 1
MM.request = function(data) {
    if (data.req) {
        if (data.req=='update mods') {
            MM.mods=data.mods; // ← attacker-controlled
            MM.saveData(); // Stores to chrome.storage.local
        }
    }
};
```

**Classification:** FALSE POSITIVE

**Reason:** Storage poisoning only - no retrieval path to attacker. This is another path where the attacker can overwrite the entire MM.mods array, but the same limitation applies - the data is not accessible to external attackers beyond what they already control through postMessage.
