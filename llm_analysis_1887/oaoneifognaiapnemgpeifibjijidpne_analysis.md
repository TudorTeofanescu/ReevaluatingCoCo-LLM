# CoCo Analysis: oaoneifognaiapnemgpeifibjijidpne

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (duplicate flows)

---

## Sink: document_body_innerText → XMLHttpRequest_url_sink

**CoCo Trace:**
```
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oaoneifognaiapnemgpeifibjijidpne/opgen_generated_files/cs_0.js
Line 535: var profName = names[profIndex].innerText;
Line 553: original = original.trim();
Line 559: var temp = /\w+(, )\w+/g.exec(original);
Line 561: if (temp[0].trim() in subs)
Line 564: return temp[0].replace(", ", "%2C+");
Line 539: url: "http://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Vanderbilt+University&schoolID=4002&query=" + convertName(profName)
```

**Code:**

```javascript
// Content script (cs_0.js) - runs only on Vanderbilt Class Search page
function searchForProfessor(profIndex) {
    var profName = names[profIndex].innerText; // Reading from Vanderbilt's own page DOM
    chrome.runtime.sendMessage({
        action: "searchForProfessor",
        method: "POST",
        url: "http://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=Vanderbilt+University&schoolID=4002&query=" + convertName(profName)
    }, function(response) {
        if (response.profLink != null) {
            getOverallScore(profIndex, profName, response.profLink);
        } else {
            names[profIndex].innerText += " - N/A";
        }
    });
}

function convertName(original) {
    original = original.trim();
    if (original in subs) {
        original = subs[original].replace(", ", "%2C+");
        return original;
    }
    var temp = /\w+(, )\w+/g.exec(original);
    if (temp[0].trim() in subs) {
        temp[0] = subs[temp[0].trim()];
    }
    return temp[0].replace(", ", "%2C+");
}
```

**Classification:** FALSE POSITIVE

**Reason:** The content script only runs on Vanderbilt's own Class Search page (`matches: ["https://webapp.mis.vanderbilt.edu/more/SearchClasses*"]`). The data read from `innerText` is professor names from Vanderbilt's legitimate class listing, which is the extension's intended functionality - to display RateMyProfessors ratings for courses on the Vanderbilt site. There is no external attacker trigger point; the extension reads data from the website it's designed to enhance, not from attacker-controlled DOM elements.
