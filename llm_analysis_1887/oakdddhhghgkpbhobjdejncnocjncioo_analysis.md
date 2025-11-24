# CoCo Analysis: oakdddhhghgkpbhobjdejncnocjncioo

## Summary

- **Overall Assessment:** FALSE POSITIVE
- **Total Sinks Detected:** 1

---

## Sink: document_body_innerText → chrome_storage_local_set_sink

**CoCo Trace:**
$FilePath$/home/teofanescu/cwsCoCo/extensions_local/oakdddhhghgkpbhobjdejncnocjncioo/opgen_generated_files/cs_4.js
Line 29    Document_element.prototype.innerText = new Object();
Line 492   course.canvas_name = $("title")[0].innerText.substring($("title")[0].innerText.indexOf("-") + 2);

**Code:**

```javascript
// cs_4.js - lines 478-524, 684-690
var course = {
  id_pid_to_canvasid: {},
  gradebook_save_ids: {}
};
var coursesStorage = [];

course.canvas_id = window.location.pathname.substring(9, 9 + window.location.pathname.substring(9).indexOf('/'));
course.canvas_name = $("title")[0].innerText.substring($("title")[0].innerText.indexOf("-") + 2); // Reading from document.title

//get stored data
chrome.storage.local.get(['courses'], function(storage) {
  courses = storage.courses;
  if (courses == undefined) {
    courses = [];
  }

  //find the course
  courseFound = false;
  for (var i in courses) {
    strCourse = courses[i];
    if (strCourse.canvas_id == course.canvas_id) {
      courseFound = true;
      course = strCourse;
      console.log("Course found in storage");
    }
  }
  if (courseFound == false) {
    // Course was not found
    courses.push(course); // Pushing course object (containing canvas_name from document.title)
  }
  coursesStorage = courses;

  //Swap id dictionaries
  Rcourse_id_pid_to_canvasid = swapDict(course["id_pid_to_canvasid"]);
  Rcourse_id_mlpid_to_pid = swapDict(course["id_mlpid_to_pid"]);
});

//Save data back to chrome storage
function storeData() {
  chrome.storage.local.set({
    courses: coursesStorage // Storing the courses array containing document.title data
  }, function() {
    console.log('Settings saved');
  });
}
```

**Classification:** FALSE POSITIVE

**Reason:** This is incomplete storage exploitation. The extension reads `document.title` (line 492) and stores it in `chrome.storage.local.set` (line 684-685), but there is no retrieval path where the attacker can access this stored data. The extension has no external message listeners (`chrome.runtime.onMessageExternal` or `window.addEventListener("message")`) or any mechanism for an attacker to retrieve the poisoned storage value. Storage poisoning alone without retrieval is not a vulnerability per the methodology.
