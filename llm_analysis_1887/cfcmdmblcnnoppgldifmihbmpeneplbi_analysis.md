# CoCo Analysis: cfcmdmblcnnoppgldifmihbmpeneplbi

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 15 (all same type)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/cfcmdmblcnnoppgldifmihbmpeneplbi/opgen_generated_files/bg.js
Line 332: CoCo framework code (XMLHttpRequest.prototype.responseText mock)
Line 995: `var doc = parser.parseFromString(xhr.responseText,'text/html');`
Line 997: `var listing = doc.querySelector(".listing.PROFESSOR");`
Line 999: `var el = listing.firstElementChild.getAttribute('href');`
Line 1022: `url = "https://www.ratemyprofessors.com" + page`

**Code:**

```javascript
// Content script extracts professor names from spire.umass.edu page
// cs_0.js - Lines 480-494
for(var i = 0; iframe.contentDocument.getElementById('MTG_INSTR$'+i); i++){
    element = iframe.contentDocument.getElementById('MTG_INSTR$'+i);
    if(element.innerHTML !== 'Staff' && element.innerHTML !== 'TBA'){
        var names = element.innerHTML.split(/,\s<br>/);
        for(var j = 0; j < names.length; j++){
            var prof = element;
            prof.name = names[j]; // Data from page DOM
            port.postMessage({prof:prof, index:i, lastIndex: names.length-1, name:prof.name});
        }
    }
}

// Background script - Lines 982-1018
function findProfRating(prof, index, lastIndex, name, callback){
    var url = 'https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=teacherName&schoolName=University+of+Massachusetts&schoolID=1513&query=' + encodeName(name);
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url , true);
    xhr.onload = function(){
        var parser = new DOMParser();
        var doc = parser.parseFromString(xhr.responseText,'text/html'); // Response from hardcoded site
        var listing = doc.querySelector(".listing.PROFESSOR");
        if(listing){
            var el = listing.firstElementChild.getAttribute('href'); // Extract link from response
            if(el)
                callback(prof, index, lastIndex, name, el); // el is used to construct next URL
        }
    }
    xhr.send(null);
}

// Lines 1021-1043
function findProfRatingCallback(prof, index, lastIndex, name, page){
    var url = "https://www.ratemyprofessors.com" + page; // Hardcoded backend + parsed data
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true); // Request to hardcoded backend
    // ... fetch and parse rating data
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is a FALSE POSITIVE due to hardcoded backend URLs (trusted infrastructure). The flow is: content script extracts professor names from spire.umass.edu page → background script fetches from hardcoded ratemyprofessors.com → parses response → makes another request to the same hardcoded ratemyprofessors.com domain. All requests go to the trusted backend (ratemyprofessors.com), which is part of the extension's intended functionality. The developer trusts their own backend infrastructure. Compromising ratemyprofessors.com is an infrastructure issue, not an extension vulnerability.
