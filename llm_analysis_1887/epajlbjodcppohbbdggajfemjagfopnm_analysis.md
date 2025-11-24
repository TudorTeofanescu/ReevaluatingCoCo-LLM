# CoCo Analysis: epajlbjodcppohbbdggajfemjagfopnm

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (variations of the same flow)

---

## Sink: document_eventListener_mouseup → chrome_storage_local_set_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/epajlbjodcppohbbdggajfemjagfopnm/opgen_generated_files/cs_0.js
Line 629  document.addEventListener("mouseup", function(event) {

Line 637  let localSizeDelta = startX - event.clientX;
Line 642  totalSizeDelta += localSizeDelta;
```

**Code:**
```javascript
// Content script - cs_0.js
document.addEventListener("mouseup", function(event) { // ← attacker can dispatch event
    buddyDiv.style.background = "transparent";
    if (event.target.id === undefined) {
        setBuddySize(originalWidth);
        totalSizeDelta = 0;
    } else if (ttClicked) {
        let localSizeDelta = startX - event.clientX; // ← attacker-controlled via event.clientX

        if (totalSizeDelta === undefined) {
            totalSizeDelta = localSizeDelta;
        } else {
            totalSizeDelta += localSizeDelta; // ← attacker-controlled value
        }

        if (totalSizeDelta < -100) {
            totalSizeDelta = -100;
        } else if (totalSizeDelta > 0) {
            totalSizeDelta = 0;
        }
    }

    if (ttClicked) {
        chrome.storage.local.set({"totalSizeDelta": totalSizeDelta}, () => {}); // ← storage write (SINK)
        ttClicked = false;
    }
    dragMDtarget.removeEventListener("mousemove", mouseMoveHandler);
    document.removeEventListener("mouseup", mouseMoveHandler);
});

// Storage read (Line 598) - but NO retrieval to attacker
function updateSizeDelta() {
    chrome.storage.local.get("totalSizeDelta", (result) => {
        let res = result["totalSizeDelta"]
        if (res !== undefined) {
            totalSizeDelta = res; // ← only used internally, never sent back to attacker
        }
    })
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. While an attacker can dispatch a custom mouseup event with controlled clientX values to poison chrome.storage.local, the stored value is only retrieved for internal use (updating a local variable) and is never sent back to the attacker via sendResponse, postMessage, or any attacker-accessible channel. Storage poisoning without a retrieval path to the attacker is not exploitable per the methodology.
