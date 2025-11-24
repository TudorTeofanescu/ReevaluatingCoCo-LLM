# CoCo Analysis: hfemgdpfoemphmhakjpcbepaggjmhjci

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 2 (both are the same pattern)

---

## Sink 1 & 2: fetch_source → fetch_resource_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/hfemgdpfoemphmhakjpcbepaggjmhjci/opgen_generated_files/bg.js
Line 265: var responseText = 'data_from_fetch';
Line 977: var doc = parser.parseFromString(html, "text/html");
Line 980: var rtLink = doc.getElementsByClassName("yuRUbf")[0].children[0].href;
Line 1014: url2 = "https://" + res[1];
(Line 1018: fetch(url2) - sink)

**Code:**

```javascript
// Background script (bg.js)
chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
  // request is a Google search URL from content script
  fetch(request) // ← Fetches Google search results
    .then(function (response) {
      return response.text();
    })
    .then(function (html) {
      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html"); // ← Parse Google results

      // Extract Rotten Tomatoes link from Google search results
      var rtLink = doc.getElementsByClassName("yuRUbf")[0].children[0].href; // ← Data from Google

      if (rtLink.includes("rottentomatoes.com")) {
        var res = rtLink.split("www.");
        url2 = "https://" + res[1]; // ← Construct URL from Google results

        // Second fetch to Rotten Tomatoes
        fetch(url2) // ← Sink: fetch with URL from Google results
          .then(function (response) {
            return response.text();
          })
          // ... parse RT data and send to content script
      }
    });
});

// Content script (contentscript.js) - runs only on Amazon/Prime Video domains
window.addEventListener('load', (event) => {
  document.addEventListener('mousemove', function (e) {
    // ... checks cursor position and DOM elements ...
  });
});

function sliderGoogleUrl() {
  // Reads data FROM Amazon Prime Video DOM
  var titleYear = sliderParentElement.getElementsByClassName('_1f30jM')[0].innerText; // ← Amazon DOM
  var titleOfMedia = sliderParentElement.getElementsByClassName('_2MiS8F tst-hover-title')[0].innerText; // ← Amazon DOM

  // Constructs Google search URL
  var formattedTitle = titleOfMedia.split(' ').join('%20');
  url = 'https://google.com/search?q=Rotten%20Tomatoes%20' + formattedTitle + '%20' + '(' + titleYear + ')' + '%20';
  return url;
}

function search(url, RTspan, RTParentElem) {
  chrome.runtime.sendMessage(url, function (response) {
    // ... handle response ...
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** The data source is Amazon Prime Video's DOM content (trusted infrastructure). The content script:
1. Runs ONLY on amazon.com and primevideo.com domains (per manifest.json)
2. Reads movie titles and years from Amazon's own page DOM elements
3. Constructs a Google search URL and sends it to background script
4. Background script fetches from Google (trusted), parses results, extracts rottentomatoes.com link, and fetches that

For an attacker to exploit this, they would need to inject malicious content into Amazon Prime Video's DOM or create a malicious page on amazon.com/primevideo.com. This requires compromising Amazon's infrastructure, which is out of scope. The extension trusts Amazon's page content as legitimate. There is no external attacker trigger available - the mousemove listener only checks cursor position and does not accept attacker-controlled data from postMessage or DOM events dispatched by the webpage. No exploitable vulnerability exists.
