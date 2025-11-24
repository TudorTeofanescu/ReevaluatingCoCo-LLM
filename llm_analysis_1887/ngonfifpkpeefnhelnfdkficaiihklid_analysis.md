# CoCo Analysis: ngonfifpkpeefnhelnfdkficaiihklid

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 3 (all duplicate flows)

---

## Sink: document_eventListener_DOMNodeInserted → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ngonfifpkpeefnhelnfdkficaiihklid/opgen_generated_files/cs_1.js
Line 540-550: DOMNodeInserted event listener extracts dataset attributes (dsBundleid, dsPackageid, dsAppid)
Line 552-557: Sends appID via chrome.runtime.sendMessage

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ngonfifpkpeefnhelnfdkficaiihklid/opgen_generated_files/bg.js
Line 971: Constructs URL with attacker-controlled appID: `"https://www.protondb.com/api/v1/reports/summaries/" + req.appID + ".json"`
Line 974: fetch(href) - Fetches from constructed URL

**Code:**

```javascript
// Content script - cs_1.js
document.addEventListener('DOMNodeInserted', onPageChange);

function onPageChange(event) {
    if (event.srcElement == null || event.srcElement.classList == null) {
        return;
    }
    if (event.srcElement.classList[0] == "search_result_row") {
        var newItem = event.srcElement;
        var id = newItem.dataset.dsBundleid; // ← attacker-controlled via DOM
        if(id == null)
            id = newItem.dataset.dsPackageid;
        if (id== null)
            id = newItem.dataset.dsAppid;

        chrome.runtime.sendMessage({
            contentScriptQuery: "queryProtonRating",
            appID: id // ← attacker-controlled data
        }, processResult);
    }
}

// Background script - bg.js
chrome.runtime.onMessage.addListener(function(req, from, sendRes) {
    if (req.contentScriptQuery == "queryProtonRating") {
        var href = "https://www.protondb.com/api/v1/reports/summaries/" + req.appID + ".json";
        fetch(href) // ← Fetch to hardcoded protondb.com domain
            .then(res => {
                if (!res.ok) {
                    if (res.status == 404) {
                        sendRes(["pending", req.appID]);
                        return true;
                    }
                    throw Error(res.status);
                }
                return res.json();
            })
            .then(data => {sendRes([data.tier, req.appID]);})
            .catch(error => console.log(error))
        return true;
    }
});
```

**Classification:** FALSE POSITIVE

**Reason:** The fetch request goes to a hardcoded backend URL (https://www.protondb.com/api/v1/reports/summaries/). While the attacker can control the appID parameter, the destination domain is the developer's trusted infrastructure. Hardcoded backend URLs are considered trusted infrastructure per the methodology.
