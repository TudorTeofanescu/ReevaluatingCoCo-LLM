# CoCo Analysis: oohipoojgodobmpkcebmmkffpbckijoc

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_getToDataURLForFont → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oohipoojgodobmpkcebmmkffpbckijoc/opgen_generated_files/cs_0.js
Line 530 document.addEventListener('getToDataURLForFont', function(data) {
Line 531 ZS_INJECT.sendMessage({action : "FONT_CANVAS" , fontData : data.detail}).then(function(resp) {

**Code:**

```javascript
// Content script (cs_0.js, lines 530-536)
document.addEventListener('getToDataURLForFont', function(data) {
    ZS_INJECT.sendMessage({action : "FONT_CANVAS" , fontData : data.detail}).then(function(resp) {
        document.dispatchEvent(new CustomEvent("DATA_URL_FOR_FONT", {
            detail : resp
        }));
    });
});
```

**Classification:** FALSE POSITIVE

**Reason:** The custom event 'getToDataURLForFont' can only be dispatched from within the same origin context (the injected script running in the same page context as the extension's content script). While the event listener receives data.detail and sends it via message passing to the background script which may use it in a fetch operation, this is internal extension functionality for font canvas data processing in the Zoho Show extension. The event cannot be triggered by an external attacker from a different origin - only by code already running in the same privileged context. Additionally, the background script is minified/bundled making it unclear whether the fetch destination is hardcoded to Zoho's backend infrastructure (trusted).
