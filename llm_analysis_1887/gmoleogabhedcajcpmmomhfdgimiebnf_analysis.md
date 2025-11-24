# CoCo Analysis: gmoleogabhedcajcpmmomhfdgimiebnf

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1 (3 storage writes detected)

---

## Sink: cs_window_eventListener_HaderMessage → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gmoleogabhedcajcpmmomhfdgimiebnf/opgen_generated_files/cs_0.js
Line 467: `window.addEventListener('HaderMessage', function (event) {`
Line 468: `chrome.runtime.sendMessage(event.detail, function (response) {`

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/gmoleogabhedcajcpmmomhfdgimiebnf/opgen_generated_files/bg.js
Line 969: `chrome.storage.local.set({ HaderTime: request.time });`
Line 970: `chrome.storage.local.set({ HaderData: request.data });`
Line 971: `chrome.storage.local.set({ type: request.type });`

**Code:**

```javascript
// Content script (cs_0.js:467-473)
window.addEventListener('HaderMessage', function (event) { // ← Entry point: custom DOM event
    chrome.runtime.sendMessage(event.detail, function (response) { // ← event.detail is attacker-controlled
        if (response.error) {
            alert(response.error);
        }
    });
});

// Background script (bg.js:967-993)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.action == 'openNoor') { // request contains event.detail from content script
        chrome.storage.local.set({ HaderTime: request.time }); // ← attacker-controlled
        chrome.storage.local.set({ HaderData: request.data }); // ← attacker-controlled
        chrome.storage.local.set({ type: request.type }); // ← attacker-controlled
        chrome.storage.local.set({ currentIndex: 1 });

        const targetUrl = 'https://noor.moe.gov.sa/Noor/EduWaveSMS/ManageAttendance.aspx';
        chrome.tabs.query({}, function (tabs) {
            const foundTab = tabs.find(tab => tab.url && tab.url.includes(targetUrl));

            if (foundTab) {
                chrome.tabs.update(foundTab.id, { active: true }, function (tab) {
                    chrome.windows.update(tab.windowId, { focused: true });
                    chrome.scripting.executeScript({
                        target: { tabId: foundTab.id },
                        files: ['injectCode/searchStudents.js']
                    });
                    sendResponse({ success: true });
                });
            } else {
                sendResponse({ error: "يرجى فتح صفحة ادخال السلوك والمواظبة." });
            }
        });
        return true;
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** Incomplete storage exploitation. While a malicious webpage on hader4schools.com/* or noor.moe.gov.sa/* can dispatch a custom 'HaderMessage' event to poison chrome.storage.local with attacker-controlled data (request.time, request.data, request.type), the stored data does not flow back to the attacker. The poisoned values are later retrieved in injected scripts (searchStudents.js line 87-99, selectStudents.js line 64-68) and used to set form field values on noor.moe.gov.sa (e.g., TimeElement.value = HaderTime). However, this is internal DOM manipulation on the target website - the data never flows back to the attacker via sendResponse, postMessage, fetch to attacker URL, or any attacker-accessible output path. Storage poisoning alone without retrieval path back to the attacker is not exploitable under the methodology.

---
