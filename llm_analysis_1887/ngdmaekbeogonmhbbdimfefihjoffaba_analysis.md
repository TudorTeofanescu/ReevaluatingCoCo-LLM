# CoCo Analysis: ngdmaekbeogonmhbbdimfefihjoffaba

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 12 (XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink)

---

## Sink: XMLHttpRequest_responseText_source → XMLHttpRequest_url_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ngdmaekbeogonmhbbdimfefihjoffaba/opgen_generated_files/bg.js
Line 332: XMLHttpRequest.prototype.responseText = 'sensitive_responseText';
Line 991: sendResponse({ JSONresponse: JSON.parse(xhr.responseText) });

$FilePath$/home/teofanescu/cwsCoCo/extensions_local/ngdmaekbeogonmhbbdimfefihjoffaba/opgen_generated_files/cs_0.js
Line 740: let numFound = resp.response.numFound;
Line 743: let profID = resp.response.docs[0].pk_id;
Line 751: let allprofRatingsURL = "https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" + profID + "&page=0&max=20";

**Code:**

```javascript
// Content script - Build initial URL (cs_0.js:721-726)
function createCellAndTooltip(fullName, newCell){
    // Hardcoded backend URL - trusted infrastructure
    let myurl = "https://search-production.ratemyprofessors.com/solr/rmp/select/?solrformat=true&rows=2&wt=json&q=";
    let splitName = fullName.split(",");
    let lastName = splitName[0].trim();
    let firstName = splitName[1].trim();
    myurl1 = myurl + firstName + "+" + lastName + "+AND+schoolid_s%" + getSchoolRMPId();
    getProfessorRating(myurl1, newCell);
}

// Content script - Send message to background (cs_0.js:735-738)
chrome.runtime.sendMessage({
    url: myurl1,  // Hardcoded RateMyProfessors URL
    type: "profRating"
}, function(response) {
    let resp = response.JSONresponse;
    let numFound = resp.response.numFound;
    if (numFound > 0) {
        let profID = resp.response.docs[0].pk_id;  // From hardcoded backend response
        // Use profID to construct another RateMyProfessors URL
        let allprofRatingsURL = "https://www.ratemyprofessors.com/paginate/professors/ratings?tid=" + profID + "&page=0&max=20";
        addTooltip(newCell, allprofRatingsURL, realFirstName, realLastName);
    }
});

// Background script - Proxy XHR request (bg.js:985-994)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.type === "profRating") {
        let xhr = new XMLHttpRequest();
        xhr.open("GET", request.url, true);  // URL from content script
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                // Send hardcoded backend response back to content script
                sendResponse({ JSONresponse: JSON.parse(xhr.responseText) });
            }
        };
        xhr.send();
    }
    return true;
});
```

**Classification:** FALSE POSITIVE

**Reason:** Data originates from hardcoded backend URLs (search-production.ratemyprofessors.com and www.ratemyprofessors.com). The response from these trusted RateMyProfessors API endpoints is used to construct subsequent requests to the same trusted domain. This is developer-trusted infrastructure, not attacker-controlled sources.
