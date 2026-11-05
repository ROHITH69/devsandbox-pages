/* Simulated pipeline run for the hero. Pure vanilla JS, no dependencies. */
(function () {
  "use strict";

  var stages = [
    { id: "detect",   lines: ["$ devsandbox run checkout-api", "detected stack: FastAPI"] },
    { id: "scaffold", lines: ["wrote Dockerfile", "wrote k8s/deployment.yaml", "wrote Jenkinsfile"] },
    { id: "build",    lines: ["docker build -t checkout-api:1", "image built"] },
    { id: "push",     lines: ["pushing to localhost:5000", "push complete"] },
    { id: "deploy",   lines: ["namespace checkout-api ready", "deployment rolled out"] }
  ];

  var list = document.getElementById("stages");
  var log = document.getElementById("log");
  var status = document.getElementById("run-status");
  var replay = document.getElementById("replay");
  if (!list || !log || !status || !replay) { return; }

  var items = {};
  Array.prototype.forEach.call(list.children, function (li) { items[li.dataset.stage] = li; });

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var timer = null;

  function setStatus(text, cls) {
    status.textContent = text;
    status.className = "run-status" + (cls ? " " + cls : "");
  }

  function reset() {
    clearTimeout(timer);
    log.textContent = "";
    Object.keys(items).forEach(function (k) { items[k].className = ""; });
    replay.hidden = true;
    setStatus("Queued", "");
  }

  function finishAll() {
    stages.forEach(function (s) {
      items[s.id].className = "done";
      s.lines.forEach(function (l) { log.textContent += l + "\n"; });
    });
    log.scrollTop = log.scrollHeight;
    setStatus("Passed", "passed");
    replay.hidden = false;
  }

  function play() {
    reset();
    if (reduced) { finishAll(); return; }
    setStatus("Running", "running");
    var si = 0, li = 0;
    (function step() {
      if (si >= stages.length) { setStatus("Passed", "passed"); replay.hidden = false; return; }
      var s = stages[si];
      items[s.id].className = "active";
      log.textContent += s.lines[li] + "\n";
      log.scrollTop = log.scrollHeight;
      li += 1;
      if (li >= s.lines.length) {
        li = 0; si += 1;
        timer = setTimeout(function () { items[s.id].className = "done"; step(); }, 520);
      } else {
        timer = setTimeout(step, 380);
      }
    })();
  }

  replay.addEventListener("click", play);
  play();
})();
