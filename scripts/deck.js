(function (globalScope) {
  "use strict";

  var DATA = globalScope.ATLAS_DATA;
  var ICONS = globalScope.ATLAS_ICONS;
  var SVG_ATLAS = globalScope.ATLAS_SVG;

  if (!DATA) return;

  var TOTAL_SLIDES = 12;
  var currentSlide = 1;
  var routePlayers = {};
  var atlasController = null;
  var prepController = null;
  var supportsDisplayTransitionCache;

  function prefersReducedMotion() {
    return Boolean(globalScope.matchMedia && globalScope.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }

  function nfc(text) {
    return String(text || "").normalize("NFC");
  }

  function segmentGraphemes(text) {
    var normalized = nfc(text);
    if (typeof Intl !== "undefined" && typeof Intl.Segmenter === "function") {
      var seg = new Intl.Segmenter("vi", { granularity: "grapheme" });
      var out = [];
      var iter = seg.segment(normalized);
      for (var item of iter) {
        out.push(item.segment);
      }
      return out;
    }
    return Array.from(normalized);
  }

  function findPlace(id) {
    for (var i = 0; i < DATA.landmarks.length; i += 1) {
      if (DATA.landmarks[i].id === id) return DATA.landmarks[i];
    }
    return DATA.landmarks[0];
  }

  function formatCoord(x, y) {
    var sx = (x >= 0 ? "+" : "") + x.toFixed(1) + "m";
    var sy = (y >= 0 ? "+" : "") + y.toFixed(1) + "m";
    return "(" + sx + ", " + sy + ")";
  }

  /* Top-layer discrete display probe & exit fallback per modern-web-guidance */
  function canTransitionDisplay() {
    if (supportsDisplayTransitionCache !== undefined) return supportsDisplayTransitionCache;
    if (!globalScope.CSS || typeof globalScope.CSS.supports !== "function" || !globalScope.CSS.supports("transition-behavior", "allow-discrete") || !document.body) {
      supportsDisplayTransitionCache = false;
      return false;
    }
    var probe = document.createElement("div");
    probe.style.cssText = "transition: display 1s allow-discrete !important; display: block;";
    document.body.appendChild(probe);
    globalScope.getComputedStyle(probe).display;
    probe.style.display = "none";
    supportsDisplayTransitionCache = globalScope.getComputedStyle(probe).display === "block";
    probe.remove();
    return supportsDisplayTransitionCache;
  }

  function supportsTopLayerExit() {
    return Boolean(globalScope.CSS && typeof globalScope.CSS.supports === "function" && globalScope.CSS.supports("overlay", "auto") && canTransitionDisplay());
  }

  function closeTopLayerDialog(dialog) {
    if (!dialog || !dialog.open) return Promise.resolve();
    if (!supportsTopLayerExit() && typeof dialog.getAnimations === "function") {
      dialog.setAttribute("data-closing", "");
      var anims = dialog.getAnimations({ subtree: true });
      if (anims.length > 0) {
        return Promise.race([
          Promise.allSettled(anims.map(function (a) { return a.finished; })),
          new Promise(function (resolve) { setTimeout(resolve, 600); })
        ]).then(function () {
          if (dialog.hasAttribute("data-closing")) {
            dialog.removeAttribute("data-closing");
            dialog.close();
          }
        });
      }
      dialog.removeAttribute("data-closing");
    }
    dialog.close();
    return Promise.resolve();
  }

  function setupDialogFallbacks() {
    var modalDialogs = document.querySelectorAll('dialog[closedby="any"]');
    var hasClosedBy = "closedBy" in HTMLDialogElement.prototype;

    for (var i = 0; i < modalDialogs.length; i += 1) {
      (function (dlg) {
        dlg.addEventListener("close", function () {
          dlg.removeAttribute("data-closing");
          dlg.returnValue = "";
        });

        dlg.addEventListener("cancel", function (ev) {
          if (!supportsTopLayerExit()) {
            ev.preventDefault();
            closeTopLayerDialog(dlg);
          }
        });

        if (!hasClosedBy) {
          var pressedOutside = false;
          var isOutside = function (ev) {
            var r = dlg.getBoundingClientRect();
            return ev.clientX < r.left || ev.clientX > r.right || ev.clientY < r.top || ev.clientY > r.bottom;
          };
          dlg.addEventListener("pointerdown", function (ev) {
            pressedOutside = isOutside(ev);
          });
          dlg.addEventListener("pointerup", function (ev) {
            if (pressedOutside && isOutside(ev)) {
              closeTopLayerDialog(dlg);
            }
          });
        }
      })(modalDialogs[i]);
    }

    // Progressive enhancement for Invoker Commands (`command` / `commandfor`) when absent
    if (!("commandForElement" in HTMLButtonElement.prototype)) {
      document.addEventListener("click", function (ev) {
        var btn = ev.target && ev.target.closest ? ev.target.closest("button[commandfor][command]") : null;
        if (!btn) return;
        var targetId = btn.getAttribute("commandfor");
        var cmd = btn.getAttribute("command");
        var target = document.getElementById(targetId);
        if (!target) return;

        if (cmd === "show-modal" && typeof target.showModal === "function") {
          target.showModal();
        } else if (cmd === "close" && typeof target.close === "function") {
          closeTopLayerDialog(target);
        } else if (cmd === "toggle-popover") {
          if (target.matches(":popover-open") || target.classList.contains(":popover-open")) {
            hidePopoverSafe(target);
          } else {
            showPopoverSafe(target);
          }
        } else if (cmd === "show-popover") {
          showPopoverSafe(target);
        } else if (cmd === "hide-popover") {
          hidePopoverSafe(target);
          var notesInv = document.getElementById("notes-toggle-btn");
          if (notesInv && target.id === "presenter-notes") notesInv.focus();
        }
      });
    }

    // Ensure closing popover from inside returns focus to trigger cleanly
    var notesCloseBtn = document.getElementById("notes-close-btn");
    var notesToggleBtn = document.getElementById("notes-toggle-btn");
    var notesDrawer = document.getElementById("presenter-notes");
    if (notesCloseBtn && notesToggleBtn && notesDrawer) {
      notesCloseBtn.addEventListener("click", function () {
        setTimeout(function () {
          notesToggleBtn.focus();
        }, 0);
      });
    }
  }

  function showPopoverSafe(el) {
    if (typeof el.showPopover === "function") {
      el.showPopover();
    } else {
      el.setAttribute("open", "");
      el.classList.add(":popover-open");
    }
  }

  function hidePopoverSafe(el) {
    if (typeof el.hidePopover === "function") {
      el.hidePopover();
    } else {
      el.removeAttribute("open");
      el.classList.remove(":popover-open");
    }
  }

  /* Slide 1 & Slide 10 & Slide 12 student renders */
  function populateMembers() {
    var roster = document.getElementById("cover-roster");
    if (roster) {
      roster.innerHTML = "";
      for (var i = 0; i < DATA.students.length; i += 1) {
        var st = DATA.students[i];
        var pill = document.createElement("div");
        pill.className = "member-pill";
        var nameStrong = document.createElement("strong");
        nameStrong.textContent = nfc(st.name);
        var roleSpan = document.createElement("span");
        roleSpan.className = "member-role-note";
        roleSpan.textContent = st.id === "gia-khanh" ? "Leader" : "Speaker";
        pill.appendChild(nameStrong);
        pill.appendChild(roleSpan);
        roster.appendChild(pill);
      }
    }

    var ledgerBody = document.getElementById("teamwork-ledger-body");
    if (ledgerBody) {
      ledgerBody.innerHTML = "";
      for (var j = 0; j < DATA.students.length; j += 1) {
        var member = DATA.students[j];
        var tr = document.createElement("tr");

        var tdName = document.createElement("td");
        tdName.className = "student-name-cell";
        tdName.textContent = nfc(member.name);

        var tdRole = document.createElement("td");
        tdRole.textContent = nfc(member.role);

        var tdTasks = document.createElement("td");
        tdTasks.textContent = nfc(member.tasks);

        var tdSlides = document.createElement("td");
        tdSlides.className = "slides-mono-cell";
        tdSlides.textContent = nfc(member.speakingSlides);

        var tdContrib = document.createElement("td");
        tdContrib.textContent = nfc(member.contribution);

        tr.appendChild(tdName);
        tr.appendChild(tdRole);
        tr.appendChild(tdTasks);
        tr.appendChild(tdSlides);
        tr.appendChild(tdContrib);
        ledgerBody.appendChild(tr);
      }
    }

    var credits = document.getElementById("closing-credits");
    if (credits) {
      credits.innerHTML = "";
      for (var k = 0; k < DATA.students.length; k += 1) {
        var c = DATA.students[k];
        var badge = document.createElement("div");
        badge.className = "credit-badge";
        badge.textContent = nfc(c.name) + " (" + c.speakingSlides + ")";
        credits.appendChild(badge);
      }
    }
  }

  /* Slide 3: Interactive Atlas + Diorama Pin Overlay */
  function initSlide3Atlas() {
    var svgWrap = document.getElementById("atlas-svg-container");
    var dioramaWrap = document.getElementById("atlas-diorama-container");
    var pinLayer = document.getElementById("diorama-pin-layer");
    var quickList = document.getElementById("atlas-quick-pins");
    var modeSvgBtn = document.getElementById("mode-svg-btn");
    var modeDioramaBtn = document.getElementById("mode-diorama-btn");

    var inspImg = document.getElementById("atlas-inspector-img");
    var inspName = document.getElementById("atlas-inspector-name");
    var inspIpa = document.getElementById("atlas-inspector-ipa");
    var inspCoords = document.getElementById("atlas-inspector-coords");
    var inspSentence = document.getElementById("atlas-inspector-sentence");
    var inspDetail = document.getElementById("atlas-inspector-detail");

    var activePlaceId = "my-house";

    function selectPlace(placeId) {
      activePlaceId = placeId;
      var place = findPlace(placeId);
      if (atlasController) atlasController.setSelected(placeId);

      if (inspImg) {
        inspImg.src = place.image;
        inspImg.alt = place.name + " 3D model";
      }
      if (inspName) inspName.textContent = "#" + place.number + " " + place.name;
      if (inspIpa) inspIpa.textContent = place.ipa;
      if (inspCoords) inspCoords.textContent = place.street + " | " + formatCoord(place.x, place.y);
      if (inspSentence) inspSentence.textContent = '"' + place.sentence + '"';
      if (inspDetail) inspDetail.textContent = place.detail;

      var allPins = document.querySelectorAll("[data-atlas-pin]");
      for (var p = 0; p < allPins.length; p += 1) {
        var isMatch = allPins[p].getAttribute("data-atlas-pin") === placeId;
        allPins[p].setAttribute("aria-pressed", isMatch ? "true" : "false");
      }
    }

    if (svgWrap && SVG_ATLAS) {
      atlasController = SVG_ATLAS.renderAtlasSvg(svgWrap, DATA, {
        interactive: true,
        ariaLabel: "Interactive Greenleaf Neighbourhood Street Atlas with 10 places",
        onSelectPlace: selectPlace
      });
    }

    if (pinLayer && quickList) {
      pinLayer.innerHTML = "";
      quickList.innerHTML = "";

      for (var i = 0; i < DATA.landmarks.length; i += 1) {
        (function (place) {
          var pin = document.createElement("button");
          pin.type = "button";
          pin.className = "diorama-pin";
          pin.setAttribute("data-atlas-pin", place.id);
          pin.setAttribute("aria-pressed", place.id === activePlaceId ? "true" : "false");
          pin.setAttribute("aria-label", place.number + ". " + place.name);
          pin.style.left = place.dioramaPinPct.x + "%";
          pin.style.top = place.dioramaPinPct.y + "%";
          var pinNum = document.createElement("span");
          pinNum.textContent = String(place.number);
          var pinLbl = document.createElement("span");
          pinLbl.className = "diorama-pin-label";
          pinLbl.textContent = place.name;
          pin.appendChild(pinNum);
          pin.appendChild(pinLbl);
          pin.addEventListener("click", function () { selectPlace(place.id); });
          pinLayer.appendChild(pin);

          var qbtn = document.createElement("button");
          qbtn.type = "button";
          qbtn.className = "quick-pin-btn";
          qbtn.setAttribute("data-atlas-pin", place.id);
          qbtn.setAttribute("aria-pressed", place.id === activePlaceId ? "true" : "false");
          qbtn.textContent = place.name;
          qbtn.addEventListener("click", function () { selectPlace(place.id); });
          quickList.appendChild(qbtn);
        })(DATA.landmarks[i]);
      }
    }

    function setAtlasMode(mode) {
      var isSvg = mode === "svg";
      if (svgWrap) svgWrap.hidden = !isSvg;
      if (dioramaWrap) dioramaWrap.hidden = isSvg;
      if (modeSvgBtn) modeSvgBtn.setAttribute("aria-pressed", isSvg ? "true" : "false");
      if (modeDioramaBtn) modeDioramaBtn.setAttribute("aria-pressed", !isSvg ? "true" : "false");
    }

    if (modeSvgBtn) modeSvgBtn.addEventListener("click", function () { setAtlasMode("svg"); });
    if (modeDioramaBtn) modeDioramaBtn.addEventListener("click", function () { setAtlasMode("diorama"); });

    selectPlace(activePlaceId);
  }

  /* Slide 4: 5x2 Specimen Grid + Modal Lightbox */
  function initSlide4Specimens() {
    var grid = document.getElementById("places-specimen-grid");
    var lightbox = document.getElementById("place-lightbox");
    var lbTitle = document.getElementById("lightbox-title");
    var lbImg = document.getElementById("lightbox-img");
    var lbIpa = document.getElementById("lightbox-ipa");
    var lbStreet = document.getElementById("lightbox-street");
    var lbSentence = document.getElementById("lightbox-sentence");
    var lbDetail = document.getElementById("lightbox-detail");
    var lbClose = document.getElementById("lightbox-close-btn");

    if (!grid) return;
    grid.innerHTML = "";

    for (var i = 0; i < DATA.landmarks.length; i += 1) {
      (function (place) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "specimen-card";
        btn.setAttribute("aria-label", "Inspect " + place.name + " 3D model");

        var thumb = document.createElement("div");
        thumb.className = "specimen-thumb";
        var img = document.createElement("img");
        img.src = place.image;
        img.alt = place.name;
        img.loading = "eager";
        thumb.appendChild(img);

        var head = document.createElement("div");
        head.className = "specimen-head";
        var nameEl = document.createElement("span");
        nameEl.className = "specimen-name";
        nameEl.textContent = place.name;
        var numEl = document.createElement("span");
        numEl.className = "specimen-num";
        numEl.textContent = "#" + place.number;
        head.appendChild(nameEl);
        head.appendChild(numEl);

        var ipaEl = document.createElement("span");
        ipaEl.className = "specimen-ipa";
        ipaEl.textContent = place.ipa;

        var sentEl = document.createElement("p");
        sentEl.className = "specimen-sentence";
        sentEl.textContent = place.sentence;

        btn.appendChild(thumb);
        btn.appendChild(head);
        btn.appendChild(ipaEl);
        btn.appendChild(sentEl);

        btn.addEventListener("click", function () {
          if (!lightbox) return;
          if (lbTitle) lbTitle.textContent = "#" + place.number + " " + place.name;
          if (lbImg) {
            lbImg.src = place.image;
            lbImg.alt = place.name + " 3D specimen";
          }
          if (lbIpa) lbIpa.textContent = place.ipa;
          if (lbStreet) lbStreet.textContent = place.street + " | " + formatCoord(place.x, place.y);
          if (lbSentence) lbSentence.textContent = '"' + place.sentence + '"';
          if (lbDetail) lbDetail.textContent = place.detail;
          lightbox.showModal();
        });

        grid.appendChild(btn);
      })(DATA.landmarks[i]);
    }

    if (lbClose && lightbox && (!("commandForElement" in HTMLButtonElement.prototype) || !supportsTopLayerExit())) {
      lbClose.addEventListener("click", function (ev) {
        ev.preventDefault();
        closeTopLayerDialog(lightbox);
      });
    }
  }

  /* Slide 5: Describing Locations (6 Prepositions + 3 Q&A Prompts) */
  function initSlide5Prepositions() {
    var prepGrid = document.getElementById("prep-pill-grid");
    var prepMapWrap = document.getElementById("prep-svg-container");
    var prepSentence = document.getElementById("prep-sentence-text");
    var prepNote = document.getElementById("prep-note-text");
    var pairStrip = document.getElementById("prep-pair-strip");
    var qaRow = document.getElementById("qa-tab-row");
    var qaAnswer = document.getElementById("qa-answer-box");

    if (prepMapWrap && SVG_ATLAS) {
      prepController = SVG_ATLAS.renderAtlasSvg(prepMapWrap, DATA, {
        interactive: false,
        ariaLabel: "Location prepositions map of Greenleaf Neighbourhood"
      });
    }

    function selectPrep(prepId) {
      var activePrep = DATA.prepositions[0];
      for (var i = 0; i < DATA.prepositions.length; i += 1) {
        if (DATA.prepositions[i].id === prepId) {
          activePrep = DATA.prepositions[i];
          break;
        }
      }

      var btns = prepGrid ? prepGrid.querySelectorAll(".prep-btn") : [];
      for (var b = 0; b < btns.length; b += 1) {
        var on = btns[b].getAttribute("data-prep-id") === activePrep.id;
        btns[b].setAttribute("aria-pressed", on ? "true" : "false");
      }

      if (prepSentence) prepSentence.textContent = '"' + activePrep.sentence + '"';
      if (prepNote) prepNote.textContent = nfc(activePrep.meaningVi) + " | " + activePrep.relationNote;
      if (prepController) prepController.highlightPreposition(activePrep);

      if (pairStrip) {
        pairStrip.innerHTML = "";
        var ids = [activePrep.subjectId].concat(activePrep.referenceIds);
        for (var k = 0; k < ids.length; k += 1) {
          var place = findPlace(ids[k]);
          var chip = document.createElement("div");
          chip.className = "mini-thumb-chip";
          var img = document.createElement("img");
          img.src = place.image;
          img.alt = place.name;
          var lbl = document.createElement("span");
          lbl.textContent = place.name;
          chip.appendChild(img);
          chip.appendChild(lbl);
          pairStrip.appendChild(chip);
        }
      }
    }

    if (prepGrid) {
      prepGrid.innerHTML = "";
      for (var p = 0; p < DATA.prepositions.length; p += 1) {
        (function (prep) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "prep-btn";
          btn.setAttribute("data-prep-id", prep.id);
          btn.setAttribute("aria-pressed", "false");

          var lbl = document.createElement("span");
          lbl.textContent = prep.label;
          var vi = document.createElement("span");
          vi.style.fontSize = "0.75rem";
          vi.style.opacity = "0.82";
          vi.textContent = nfc(prep.meaningVi);
          btn.appendChild(lbl);
          btn.appendChild(vi);
          btn.addEventListener("click", function () { selectPrep(prep.id); });
          prepGrid.appendChild(btn);
        })(DATA.prepositions[p]);
      }
    }

    function selectQa(qaId) {
      var activeQa = DATA.qaPrompts[0];
      for (var i = 0; i < DATA.qaPrompts.length; i += 1) {
        if (DATA.qaPrompts[i].id === qaId) {
          activeQa = DATA.qaPrompts[i];
          break;
        }
      }
      var tabs = qaRow ? qaRow.querySelectorAll(".qa-tab-btn") : [];
      for (var t = 0; t < tabs.length; t += 1) {
        tabs[t].setAttribute("aria-pressed", tabs[t].getAttribute("data-qa-id") === activeQa.id ? "true" : "false");
      }
      if (qaAnswer) {
        qaAnswer.innerHTML = "";
        var strong = document.createElement("strong");
        strong.textContent = activeQa.prompt;
        var p = document.createElement("span");
        p.textContent = activeQa.answer;
        qaAnswer.appendChild(strong);
        qaAnswer.appendChild(p);
      }
    }

    if (qaRow) {
      qaRow.innerHTML = "";
      for (var q = 0; q < DATA.qaPrompts.length; q += 1) {
        (function (item) {
          var tbtn = document.createElement("button");
          tbtn.type = "button";
          tbtn.className = "qa-tab-btn";
          tbtn.setAttribute("data-qa-id", item.id);
          tbtn.setAttribute("aria-pressed", "false");
          tbtn.textContent = item.prompt.split("?")[0] + "?";
          tbtn.addEventListener("click", function () { selectQa(item.id); });
          qaRow.appendChild(tbtn);
        })(DATA.qaPrompts[q]);
      }
    }

    selectPrep(DATA.prepositions[0].id);
    selectQa(DATA.qaPrompts[0].id);
  }

  /* Slides 6, 7, 8: GSAP Direction Route Players */
  function initRouteSlides() {
    for (var r = 0; r < DATA.routes.length; r += 1) {
      (function (route) {
        var slideNum = route.slideNumber;
        var dlgList = document.getElementById("route-dialogue-" + slideNum);
        var mapWrap = document.getElementById("route-map-" + slideNum);
        var stepStrip = document.getElementById("route-steps-" + slideNum);
        var playBtn = document.getElementById("route-play-" + slideNum);
        var replayBtn = document.getElementById("route-replay-" + slideNum);
        var nextStepBtn = document.getElementById("route-next-step-" + slideNum);

        if (dlgList) {
          dlgList.innerHTML = "";
          for (var d = 0; d < route.dialogue.length; d += 1) {
            var turn = route.dialogue[d];
            var box = document.createElement("div");
            box.className = "dialogue-turn" + (turn.speaker === route.giver ? " turn-giver" : "");
            var sp = document.createElement("span");
            sp.className = "turn-speaker";
            sp.textContent = turn.speaker + " (" + turn.role + ")";
            var ln = document.createElement("p");
            ln.className = "turn-line";
            ln.textContent = '"' + turn.line + '"';
            box.appendChild(sp);
            box.appendChild(ln);
            dlgList.appendChild(box);
          }
        }

        if (stepStrip) {
          stepStrip.innerHTML = "";
          for (var s = 0; s < route.steps.length; s += 1) {
            var pill = document.createElement("div");
            pill.className = "route-step-pill";
            pill.setAttribute("data-step-idx", String(s));
            pill.textContent = (s + 1) + ". " + route.steps[s];
            stepStrip.appendChild(pill);
          }
        }

        if (!mapWrap || !SVG_ATLAS) return;
        var controller = SVG_ATLAS.renderAtlasSvg(mapWrap, DATA, {
          interactive: false,
          ariaLabel: "Direction route map: " + route.title
        });
        var renderedRoute = controller.drawRoute(route);
        if (!renderedRoute) return;

        var pts = renderedRoute.points;
        var walker = renderedRoute.walker;
        var currentStep = 0;
        var tl = null;

        function setActiveStep(idx) {
          currentStep = idx;
          if (!stepStrip) return;
          var pills = stepStrip.querySelectorAll(".route-step-pill");
          for (var i = 0; i < pills.length; i += 1) {
            pills[i].classList.toggle("is-active", i === idx);
          }
        }

        function setPlayLabel(isPlaying) {
          if (!playBtn) return;
          // WCAG 2.2.2: Never combine toggling Play/Pause label with aria-pressed
          var labelText = isPlaying ? "Pause route" : "Play route";
          var span = playBtn.querySelector(".route-play-label");
          if (span) span.textContent = labelText;
          var oldSvg = playBtn.querySelector("svg.icon");
          if (oldSvg && ICONS && typeof ICONS.createIconSvg === "function") {
            oldSvg.replaceWith(ICONS.createIconSvg(isPlaying ? "pause" : "play", "icon-sm"));
          }
          playBtn.setAttribute("aria-label", labelText + " for " + route.title);
        }

        function angleDeg(p0, p1) {
          return Math.atan2(p1.y - p0.y, p1.x - p0.x) * (180 / Math.PI);
        }

        function placeWalkerStaticEnd() {
          var lastIdx = pts.length - 1;
          var prevIdx = Math.max(0, lastIdx - 1);
          var ang = angleDeg(pts[prevIdx], pts[lastIdx]);
          if (globalScope.gsap) {
            globalScope.gsap.set(walker, { x: pts[lastIdx].x, y: pts[lastIdx].y, rotation: ang });
          } else {
            walker.setAttribute("transform", "translate(" + pts[lastIdx].x + " " + pts[lastIdx].y + ") rotate(" + ang + ")");
          }
          setActiveStep(route.steps.length - 1);
          setPlayLabel(false);
        }

        function buildTimeline() {
          if (!globalScope.gsap || prefersReducedMotion()) {
            placeWalkerStaticEnd();
            return null;
          }
          var gsap = globalScope.gsap;
          var timeline = gsap.timeline({
            paused: true,
            onComplete: function () {
              setActiveStep(route.steps.length - 1);
              setPlayLabel(false);
            }
          });

          var initAng = angleDeg(pts[0], pts[1]);
          timeline.set(walker, { x: pts[0].x, y: pts[0].y, rotation: initAng });
          timeline.call(function () { setActiveStep(0); });

          for (var i = 1; i < pts.length; i += 1) {
            (function (segIdx) {
              var segAngle = angleDeg(pts[segIdx - 1], pts[segIdx]);
              var dist = Math.hypot(pts[segIdx].x - pts[segIdx - 1].x, pts[segIdx].y - pts[segIdx - 1].y);
              var dur = Math.max(0.65, Math.min(1.35, dist / 220));
              timeline.to(walker, { rotation: segAngle, duration: 0.18, ease: "power1.out" });
              timeline.call(function () {
                setActiveStep(Math.min(segIdx, route.steps.length - 1));
              });
              timeline.to(walker, {
                x: pts[segIdx].x,
                y: pts[segIdx].y,
                duration: dur,
                ease: "power1.inOut"
              });
            })(i);
          }
          return timeline;
        }

        tl = buildTimeline();
        placeWalkerStaticEnd();

        if (playBtn) {
          playBtn.addEventListener("click", function () {
            if (prefersReducedMotion() || !tl) {
              placeWalkerStaticEnd();
              return;
            }
            if (tl.isActive()) {
              tl.pause();
              setPlayLabel(false);
            } else {
              if (tl.progress() >= 0.99) tl.restart();
              else tl.play();
              setPlayLabel(true);
            }
          });
        }

        if (replayBtn) {
          replayBtn.addEventListener("click", function () {
            if (prefersReducedMotion() || !tl) {
              placeWalkerStaticEnd();
              return;
            }
            tl.restart();
            setPlayLabel(true);
          });
        }

        if (nextStepBtn) {
          nextStepBtn.addEventListener("click", function () {
            if (tl && tl.isActive()) {
              tl.pause();
              setPlayLabel(false);
            }
            var nextIdx = (currentStep + 1) % route.steps.length;
            var ptIdx = Math.min(nextIdx, pts.length - 1);
            var ang = ptIdx > 0 ? angleDeg(pts[ptIdx - 1], pts[ptIdx]) : angleDeg(pts[0], pts[1]);
            if (globalScope.gsap) {
              globalScope.gsap.to(walker, {
                x: pts[ptIdx].x,
                y: pts[ptIdx].y,
                rotation: ang,
                duration: prefersReducedMotion() ? 0 : 0.35,
                ease: "power2.out"
              });
            } else {
              walker.setAttribute("transform", "translate(" + pts[ptIdx].x + " " + pts[ptIdx].y + ") rotate(" + ang + ")");
            }
            setActiveStep(nextIdx);
          });
        }

        routePlayers[slideNum] = {
          pause: function () {
            if (tl && tl.isActive()) {
              tl.pause();
              setPlayLabel(false);
            }
          },
          activate: function () {
            if (prefersReducedMotion() || !tl) {
              placeWalkerStaticEnd();
            } else {
              tl.restart();
              setPlayLabel(true);
            }
          }
        };
      })(DATA.routes[r]);
    }
  }

  /* Slide 9: Vocabulary Strip & Geometric Preposition SVG Diagrams */
  function initSlide9Vocab() {
    var placesList = document.getElementById("vocab-places-list");
    var prepDiagrams = document.getElementById("vocab-prep-diagrams");
    var dirStrip = document.getElementById("vocab-direction-strip");

    if (placesList) {
      placesList.innerHTML = "";
      for (var i = 0; i < DATA.landmarks.length; i += 1) {
        var place = DATA.landmarks[i];
        var item = document.createElement("div");
        item.className = "vocab-place-item";
        var iconSpan = document.createElement("span");
        iconSpan.setAttribute("data-icon", place.icon);
        iconSpan.setAttribute("data-icon-class", "icon-sm");
        var textDiv = document.createElement("div");
        var title = document.createElement("strong");
        title.textContent = place.name;
        var ipa = document.createElement("span");
        ipa.textContent = place.ipa;
        textDiv.appendChild(title);
        textDiv.appendChild(ipa);
        item.appendChild(iconSpan);
        item.appendChild(textDiv);
        placesList.appendChild(item);
      }
    }

    var svgSchemas = {
      "next-to": '<rect x="18" y="14" width="38" height="28" rx="4" fill="#1B6B4A"/><rect x="64" y="14" width="38" height="28" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/>',
      "opposite": '<rect x="18" y="14" width="34" height="28" rx="4" fill="#1B6B4A"/><line x1="60" y1="8" x2="60" y2="48" stroke="#D8D3C8" stroke-width="8"/><line x1="60" y1="10" x2="60" y2="46" stroke="#FFFFFF" stroke-width="1.5" stroke-dasharray="4 3"/><rect x="68" y="14" width="34" height="28" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/>',
      "between": '<rect x="10" y="16" width="26" height="24" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/><rect x="47" y="14" width="26" height="28" rx="4" fill="#1B6B4A"/><rect x="84" y="16" width="26" height="24" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/>',
      "in-front-of": '<rect x="34" y="8" width="52" height="22" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/><rect x="44" y="34" width="32" height="14" rx="3" fill="#1B6B4A"/>',
      "behind": '<rect x="34" y="8" width="52" height="22" rx="4" fill="#1B6B4A"/><rect x="44" y="34" width="32" height="14" rx="3" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/>',
      "near": '<rect x="16" y="15" width="30" height="26" rx="4" fill="#1B6B4A"/><line x1="50" y1="28" x2="70" y2="28" stroke="#C84B31" stroke-width="2" stroke-dasharray="3 3"/><rect x="74" y="15" width="30" height="26" rx="4" fill="#EDE9DE" stroke="#171C22" stroke-width="1.5"/>'
    };

    if (prepDiagrams) {
      prepDiagrams.innerHTML = "";
      for (var p = 0; p < DATA.prepositions.length; p += 1) {
        var prep = DATA.prepositions[p];
        var card = document.createElement("div");
        card.className = "prep-diagram-card";
        card.innerHTML =
          '<svg class="prep-diagram-svg" viewBox="0 0 120 56" aria-hidden="true">' +
          (svgSchemas[prep.id] || "") +
          "</svg>" +
          "<strong>" + prep.label + "</strong>" +
          "<span>" + nfc(prep.meaningVi) + "</span>";
        prepDiagrams.appendChild(card);
      }
    }

    if (dirStrip) {
      dirStrip.innerHTML = "";
      for (var d = 0; d < DATA.directionsVocab.length; d += 1) {
        var dv = DATA.directionsVocab[d];
        var chip = document.createElement("div");
        chip.className = "dir-phrase-chip";
        var ic = document.createElement("span");
        ic.setAttribute("data-icon", dv.icon);
        ic.setAttribute("data-icon-class", "icon-sm");
        var txt = document.createElement("div");
        var phr = document.createElement("strong");
        phr.textContent = dv.phrase;
        phr.style.display = "block";
        var sub = document.createElement("span");
        sub.style.fontSize = "0.74rem";
        sub.style.color = "var(--ink-slate)";
        sub.textContent = nfc(dv.meaningVi);
        txt.appendChild(phr);
        txt.appendChild(sub);
        chip.appendChild(ic);
        chip.appendChild(txt);
        dirStrip.appendChild(chip);
      }
    }
  }

  /* Slide Navigation & View Transitions */
  function updatePresenterNotes(slideNum) {
    var note = DATA.presenterNotes[slideNum];
    if (!note) return;
    var titleEl = document.getElementById("notes-slide-title");
    var speakerEl = document.getElementById("notes-speakers");
    var enEl = document.getElementById("notes-english-script");
    var viEl = document.getElementById("notes-vietnamese-tips");

    if (titleEl) titleEl.textContent = nfc(note.title);
    if (speakerEl) speakerEl.textContent = nfc(note.speakers);
    if (enEl) enEl.textContent = nfc(note.englishScript);
    if (viEl) viEl.textContent = nfc(note.vietnameseTips);
  }

  function buildChromeSelectors() {
    var dotStrip = document.getElementById("dot-strip");
    var overviewGrid = document.getElementById("overview-grid");

    if (dotStrip) {
      dotStrip.innerHTML = "";
      for (var i = 1; i <= TOTAL_SLIDES; i += 1) {
        (function (num) {
          var btn = document.createElement("button");
          btn.type = "button";
          btn.className = "dot-btn";
          btn.setAttribute("aria-label", "Go to slide " + num);
          btn.setAttribute("data-dot-slide", String(num));
          var pip = document.createElement("span");
          pip.className = "dot-pip";
          btn.appendChild(pip);
          btn.addEventListener("click", function () { goToSlide(num); });
          dotStrip.appendChild(btn);
        })(i);
      }
    }

    if (overviewGrid) {
      overviewGrid.innerHTML = "";
      var overviewDlg = document.getElementById("slide-overview-dialog");
      for (var j = 1; j <= TOTAL_SLIDES; j += 1) {
        (function (num) {
          var note = DATA.presenterNotes[num] || { title: "Slide " + num, speakers: "" };
          var tile = document.createElement("button");
          tile.type = "button";
          tile.className = "overview-tile";
          tile.setAttribute("data-overview-slide", String(num));

          var numSpan = document.createElement("span");
          numSpan.className = "overview-tile-num";
          numSpan.textContent = (num < 10 ? "0" : "") + num;

          var titleSpan = document.createElement("span");
          titleSpan.className = "overview-tile-title";
          titleSpan.textContent = nfc(note.title.replace(/^Slide \d+:\s*/, ""));

          var spSpan = document.createElement("span");
          spSpan.className = "overview-tile-speakers";
          spSpan.textContent = nfc(note.speakers);

          tile.appendChild(numSpan);
          tile.appendChild(titleSpan);
          tile.appendChild(spSpan);

          tile.addEventListener("click", function () {
            if (overviewDlg) closeTopLayerDialog(overviewDlg);
            goToSlide(num);
          });
          overviewGrid.appendChild(tile);
        })(j);
      }
    }
  }

  function applySlideState(targetNum) {
    var prevNum = currentSlide;
    if (routePlayers[prevNum]) routePlayers[prevNum].pause();

    currentSlide = targetNum;
    var slides = document.querySelectorAll(".slide[data-slide]");
    for (var i = 0; i < slides.length; i += 1) {
      var n = Number(slides[i].getAttribute("data-slide"));
      slides[i].hidden = n !== targetNum;
    }

    var counter = document.getElementById("slide-counter");
    if (counter) {
      counter.textContent = (targetNum < 10 ? "0" : "") + targetNum + " / " + TOTAL_SLIDES;
    }

    var prevBtn = document.getElementById("prev-slide-btn");
    var nextBtn = document.getElementById("next-slide-btn");
    if (prevBtn) prevBtn.disabled = targetNum <= 1;
    if (nextBtn) nextBtn.disabled = targetNum >= TOTAL_SLIDES;

    var dots = document.querySelectorAll("[data-dot-slide]");
    for (var d = 0; d < dots.length; d += 1) {
      var dNum = Number(dots[d].getAttribute("data-dot-slide"));
      if (dNum === targetNum) dots[d].setAttribute("aria-current", "step");
      else dots[d].removeAttribute("aria-current");
    }

    var tiles = document.querySelectorAll("[data-overview-slide]");
    for (var t = 0; t < tiles.length; t += 1) {
      var tNum = Number(tiles[t].getAttribute("data-overview-slide"));
      if (tNum === targetNum) tiles[t].setAttribute("aria-current", "step");
      else tiles[t].removeAttribute("aria-current");
    }

    updatePresenterNotes(targetNum);

    var announcer = document.getElementById("slide-live-announcer");
    if (announcer && DATA.presenterNotes[targetNum]) {
      announcer.textContent = nfc(DATA.presenterNotes[targetNum].title) + " (" + targetNum + " of " + TOTAL_SLIDES + ")";
    }

    if (globalScope.history && typeof globalScope.history.replaceState === "function") {
      globalScope.history.replaceState(null, "", "#slide-" + targetNum);
    }

    if (routePlayers[targetNum]) {
      routePlayers[targetNum].activate();
    }
  }

  function goToSlide(targetNum, skipTransition) {
    var clamped = Math.max(1, Math.min(TOTAL_SLIDES, Number(targetNum) || 1));
    if (clamped === currentSlide) return;

    var direction = clamped > currentSlide ? "forward" : "backward";

    if (!skipTransition && typeof document.startViewTransition === "function" && !prefersReducedMotion()) {
      document.startViewTransition({
        update: function () { applySlideState(clamped); },
        types: [direction]
      });
    } else {
      applySlideState(clamped);
    }
  }

  function bindGlobalControls() {
    var prevBtn = document.getElementById("prev-slide-btn");
    var nextBtn = document.getElementById("next-slide-btn");
    var overviewClose = document.getElementById("overview-close-btn");
    var overviewDlg = document.getElementById("slide-overview-dialog");
    var jumpBtns = document.querySelectorAll("[data-jump-slide]");

    if (prevBtn) prevBtn.addEventListener("click", function () { goToSlide(currentSlide - 1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { goToSlide(currentSlide + 1); });
    if (overviewClose && overviewDlg && (!("commandForElement" in HTMLButtonElement.prototype) || !supportsTopLayerExit())) {
      overviewClose.addEventListener("click", function (ev) {
        ev.preventDefault();
        closeTopLayerDialog(overviewDlg);
      });
    }

    for (var j = 0; j < jumpBtns.length; j += 1) {
      (function (btn) {
        btn.addEventListener("click", function () {
          var target = Number(btn.getAttribute("data-jump-slide"));
          goToSlide(target);
        });
      })(jumpBtns[j]);
    }

    document.addEventListener("keydown", function (ev) {
      var openModal = document.querySelector("dialog[open]");
      if (openModal) return;

      var tag = ev.target && ev.target.tagName ? ev.target.tagName.toLowerCase() : "";
      var isInteractive = tag === "button" || tag === "a" || tag === "input" || tag === "textarea" || (ev.target && ev.target.getAttribute && ev.target.getAttribute("role") === "button");

      if (ev.key === "ArrowRight" || ev.key === "PageDown") {
        ev.preventDefault();
        goToSlide(currentSlide + 1);
      } else if (ev.key === "ArrowLeft" || ev.key === "PageUp") {
        ev.preventDefault();
        goToSlide(currentSlide - 1);
      } else if (ev.key === " " && !isInteractive) {
        ev.preventDefault();
        goToSlide(currentSlide + 1);
      } else if (ev.key === "Home" || ev.key === "Escape") {
        var notesDlg = document.getElementById("presenter-notes");
        if (ev.key === "Escape" && notesDlg && (notesDlg.matches(":popover-open") || notesDlg.classList.contains(":popover-open"))) {
          hidePopoverSafe(notesDlg);
          return;
        }
        ev.preventDefault();
        goToSlide(1);
      } else if (ev.key === "End") {
        ev.preventDefault();
        goToSlide(TOTAL_SLIDES);
      } else if (ev.key === "g" || ev.key === "G") {
        if (overviewDlg && !overviewDlg.open) overviewDlg.showModal();
      } else if (ev.key === "n" || ev.key === "N") {
        var notesPopover = document.getElementById("presenter-notes");
        if (notesPopover) {
          if (notesPopover.matches(":popover-open") || notesPopover.classList.contains(":popover-open")) hidePopoverSafe(notesPopover);
          else showPopoverSafe(notesPopover);
        }
      }
    });
  }

  function init() {
    populateMembers();
    initSlide3Atlas();
    initSlide4Specimens();
    initSlide5Prepositions();
    initRouteSlides();
    initSlide9Vocab();
    buildChromeSelectors();
    setupDialogFallbacks();
    bindGlobalControls();

    if (ICONS && typeof ICONS.hydrateIcons === "function") {
      ICONS.hydrateIcons(document);
    }

    var initialHashMatch = globalScope.location && globalScope.location.hash ? globalScope.location.hash.match(/^#slide-(\d+)$/) : null;
    var startSlide = initialHashMatch ? Math.max(1, Math.min(TOTAL_SLIDES, Number(initialHashMatch[1]))) : 1;
    applySlideState(startSlide);

    globalScope.__ATLAS_DECK = {
      goToSlide: goToSlide,
      getCurrentSlide: function () { return currentSlide; },
      segmentGraphemes: segmentGraphemes
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})(typeof window !== "undefined" ? window : globalThis);
