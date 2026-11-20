(function (globalScope) {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";

  function svgEl(tag, attrs, textContent) {
    var el = document.createElementNS(SVG_NS, tag);
    if (attrs) {
      var keys = Object.keys(attrs);
      for (var i = 0; i < keys.length; i += 1) {
        var k = keys[i];
        el.setAttribute(k, String(attrs[k]));
      }
    }
    if (textContent !== undefined && textContent !== null) {
      el.textContent = String(textContent).normalize("NFC");
    }
    return el;
  }

  function createConverter(bounds) {
    return {
      x: function (mx) {
        return (mx - bounds.minX) * bounds.scalePxPerMeter;
      },
      y: function (my) {
        return (bounds.maxY - my) * bounds.scalePxPerMeter;
      },
      w: function (mw) {
        return mw * bounds.scalePxPerMeter;
      },
      h: function (md) {
        return md * bounds.scalePxPerMeter;
      }
    };
  }

  function findPlace(data, id) {
    for (var i = 0; i < data.landmarks.length; i += 1) {
      if (data.landmarks[i].id === id) return data.landmarks[i];
    }
    return null;
  }

  function renderAtlasSvg(container, data, options) {
    if (!container || !data) return null;
    var opts = options || {};
    var bounds = data.bounds;
    var toSvg = createConverter(bounds);

    var svg = svgEl("svg", {
      "class": "atlas-svg",
      "viewBox": "0 0 " + bounds.svgWidth + " " + bounds.svgHeight,
      "role": "img",
      "aria-label": opts.ariaLabel || "Interactive map of Greenleaf Neighbourhood"
    });

    // Background archival paper & fine coordinate grid
    svg.appendChild(svgEl("rect", {
      x: 0, y: 0, width: bounds.svgWidth, height: bounds.svgHeight,
      fill: "#F6F4EE"
    }));

    var gridGroup = svgEl("g", { opacity: "0.55" });
    for (var gx = bounds.minX; gx <= bounds.maxX; gx += 2) {
      var sx = toSvg.x(gx);
      gridGroup.appendChild(svgEl("line", {
        x1: sx, y1: 0, x2: sx, y2: bounds.svgHeight,
        stroke: gx % 10 === 0 ? "#DED8CB" : "#EAE5DA",
        "stroke-width": gx % 10 === 0 ? "1" : "0.6"
      }));
    }
    for (var gy = bounds.minY; gy <= bounds.maxY; gy += 2) {
      var sy = toSvg.y(gy);
      gridGroup.appendChild(svgEl("line", {
        x1: 0, y1: sy, x2: bounds.svgWidth, y2: sy,
        stroke: gy % 10 === 0 ? "#DED8CB" : "#EAE5DA",
        "stroke-width": gy % 10 === 0 ? "1" : "0.6"
      }));
    }
    svg.appendChild(gridGroup);

    // Subtle river stream on far east edge (east of River Road corridor & hospital)
    svg.appendChild(svgEl("path", {
      d: "M 754 0 C 748 140, 762 280, 752 400 C 746 460, 756 495, 750 520 L 780 520 L 780 0 Z",
      fill: "#DCE7EE",
      stroke: "#B8CEDB",
      "stroke-width": "1"
    }));

    // Green north meadow apron behind School and Park
    svg.appendChild(svgEl("rect", {
      x: toSvg.x(-1.0),
      y: toSvg.y(13.2),
      width: toSvg.w(11.0),
      height: toSvg.h(5.2),
      rx: 10,
      fill: "#E7EFE8",
      stroke: "#CBDAC9",
      "stroke-width": "1"
    }));

    // Layer 1: Sidewalk corridors (3.6m wide)
    var sidewalkLayer = svgEl("g");
    for (var si = 0; si < data.streets.length; si += 1) {
      var st = data.streets[si];
      if (st.axis === "horizontal") {
        sidewalkLayer.appendChild(svgEl("rect", {
          x: toSvg.x(st.spanMin),
          y: toSvg.y(st.corridorMax),
          width: toSvg.w(st.spanMax - st.spanMin),
          height: toSvg.h(st.corridorWidth),
          rx: 4,
          fill: "#EDE9DE",
          stroke: "#D8D3C8",
          "stroke-width": "1"
        }));
      } else {
        sidewalkLayer.appendChild(svgEl("rect", {
          x: toSvg.x(st.corridorMin),
          y: toSvg.y(st.spanMax),
          width: toSvg.w(st.corridorWidth),
          height: toSvg.h(st.spanMax - st.spanMin),
          rx: 4,
          fill: "#EDE9DE",
          stroke: "#D8D3C8",
          "stroke-width": "1"
        }));
      }
    }
    svg.appendChild(sidewalkLayer);

    // Layer 2: Asphalt roadbeds (2.6m wide)
    var roadLayer = svgEl("g");
    for (var ri = 0; ri < data.streets.length; ri += 1) {
      var road = data.streets[ri];
      var halfR = road.roadWidth / 2;
      if (road.axis === "horizontal") {
        roadLayer.appendChild(svgEl("rect", {
          x: toSvg.x(road.spanMin),
          y: toSvg.y(road.centerCoord + halfR),
          width: toSvg.w(road.spanMax - road.spanMin),
          height: toSvg.h(road.roadWidth),
          fill: "#DDD7C9"
        }));
      } else {
        roadLayer.appendChild(svgEl("rect", {
          x: toSvg.x(road.centerCoord - halfR),
          y: toSvg.y(road.spanMax),
          width: toSvg.w(road.roadWidth),
          height: toSvg.h(road.spanMax - road.spanMin),
          fill: "#DDD7C9"
        }));
      }
    }
    svg.appendChild(roadLayer);

    // Dashed centerlines
    var dashLayer = svgEl("g", { opacity: "0.85" });
    dashLayer.appendChild(svgEl("line", {
      x1: toSvg.x(-15.5), y1: toSvg.y(6.0), x2: toSvg.x(18.5), y2: toSvg.y(6.0),
      stroke: "#FAF8F3", "stroke-width": "1.6", "stroke-dasharray": "9 7"
    }));
    dashLayer.appendChild(svgEl("line", {
      x1: toSvg.x(-15.5), y1: toSvg.y(-6.0), x2: toSvg.x(18.5), y2: toSvg.y(-6.0),
      stroke: "#FAF8F3", "stroke-width": "1.6", "stroke-dasharray": "9 7"
    }));
    dashLayer.appendChild(svgEl("line", {
      x1: toSvg.x(-2.0), y1: toSvg.y(13.5), x2: toSvg.x(-2.0), y2: toSvg.y(-10.5),
      stroke: "#FAF8F3", "stroke-width": "1.6", "stroke-dasharray": "9 7"
    }));
    dashLayer.appendChild(svgEl("line", {
      x1: toSvg.x(12.0), y1: toSvg.y(13.5), x2: toSvg.x(12.0), y2: toSvg.y(-10.5),
      stroke: "#FAF8F3", "stroke-width": "1.6", "stroke-dasharray": "9 7"
    }));
    svg.appendChild(dashLayer);

    // Street name labels positioned cleanly outside active route corridors and scale bar
    var streetLabels = svgEl("g");

    function addRoadSign(cx, cy, label, fillBg) {
      var w = Math.max(88, label.length * 7.2 + 16);
      streetLabels.appendChild(svgEl("rect", {
        x: cx - w / 2, y: cy - 10, width: w, height: 20, rx: 5,
        fill: fillBg || "rgba(255, 255, 255, 0.92)",
        stroke: "#D8D3C8",
        "stroke-width": "1"
      }));
      streetLabels.appendChild(svgEl("text", {
        x: cx, y: cy + 4, "text-anchor": "middle", "class": "atlas-street-label"
      }, label));
    }

    addRoadSign(toSvg.x(-9.5), toSvg.y(6.0), "OAK STREET");
    addRoadSign(toSvg.x(16.2), toSvg.y(6.0), "OAK STREET");
    addRoadSign(toSvg.x(-8.0), toSvg.y(-8.8), "MAPLE STREET");
    addRoadSign(toSvg.x(16.2), toSvg.y(-6.0), "MAPLE STREET");
    addRoadSign(toSvg.x(-2.0), toSvg.y(13.4), "PINE STREET (1st)");
    addRoadSign(toSvg.x(12.0), toSvg.y(13.4), "RIVER ROAD (2nd)");
    svg.appendChild(streetLabels);

    // Layer 3: 10 Landmarks
    var buildingLayer = svgEl("g");
    var buildingNodes = {};
    for (var bi = 0; bi < data.landmarks.length; bi += 1) {
      var place = data.landmarks[bi];
      var left = toSvg.x(place.x - place.width / 2);
      var top = toSvg.y(place.y + place.depth / 2);
      var rw = toSvg.w(place.width);
      var rh = toSvg.h(place.depth);
      var cx = toSvg.x(place.x);
      var cy = toSvg.y(place.y);

      var g = svgEl("g", {
        "class": "atlas-building" + (place.id === "park" ? " is-park" : ""),
        "data-place-id": place.id,
        "tabindex": opts.interactive ? "0" : "-1",
        "role": opts.interactive ? "button" : "group",
        "aria-label": place.name + " on " + place.street
      });

      // Soft architectural footprint shadow
      g.appendChild(svgEl("rect", {
        x: left + 3, y: top + 3, width: rw, height: rh, rx: 4,
        fill: "rgba(23, 28, 34, 0.10)"
      }));

      // Main footprint box
      g.appendChild(svgEl("rect", {
        x: left, y: top, width: rw, height: rh, rx: 4,
        "class": "atlas-building-box"
      }));

      // Subtle architectural roof or interior cue (kept clear of center label text)
      if (place.id === "park") {
        g.appendChild(svgEl("circle", { cx: cx - 30, cy: cy - 18, r: 8, fill: "#97C1A6", opacity: "0.75" }));
        g.appendChild(svgEl("circle", { cx: cx + 30, cy: cy + 18, r: 7, fill: "#97C1A6", opacity: "0.75" }));
        g.appendChild(svgEl("circle", { cx: cx + 31, cy: cy - 18, r: 4.5, fill: "#FFFFFF", stroke: "#8AB398", "stroke-width": "1.2" }));
      } else if (place.id === "hospital") {
        g.appendChild(svgEl("rect", { x: cx - 3, y: top + 9, width: 6, height: 14, fill: "#C84B31" }));
        g.appendChild(svgEl("rect", { x: cx - 7, y: top + 13, width: 14, height: 6, fill: "#C84B31" }));
      } else if (place.id !== "bus-stop") {
        g.appendChild(svgEl("line", {
          x1: left + 6, y1: top + 8, x2: left + rw - 6, y2: top + 8,
          stroke: "#D8D3C8", "stroke-width": "1.5"
        }));
      }

      // Entrance / facing door notch indicating which street it faces
      if (place.facing === "south") {
        g.appendChild(svgEl("rect", { x: cx - 7, y: top + rh - 4, width: 14, height: 5, rx: 1, fill: "#1B6B4A" }));
      } else if (place.facing === "west") {
        g.appendChild(svgEl("rect", { x: left - 1, y: cy - 7, width: 5, height: 14, rx: 1, fill: "#1B6B4A" }));
      } else if (place.facing === "east") {
        g.appendChild(svgEl("rect", { x: left + rw - 4, y: cy - 7, width: 5, height: 14, rx: 1, fill: "#1B6B4A" }));
      }

      // Label text cleanly sized for every parcel
      if (place.id === "bus-stop") {
        g.appendChild(svgEl("text", {
          x: cx, y: cy + 2.5,
          "text-anchor": "middle",
          "class": "atlas-building-label atlas-building-label-compact"
        }, "Bus Stop"));
      } else {
        g.appendChild(svgEl("text", {
          x: cx, y: cy - 2,
          "text-anchor": "middle",
          "class": "atlas-building-label",
          "font-size": "10.5"
        }, place.name));
        g.appendChild(svgEl("text", {
          x: cx, y: cy + 12,
          "text-anchor": "middle",
          "font-family": "Geist Mono, monospace",
          "font-size": "8.5",
          fill: "#4D5761"
        }, "#" + place.number));
      }

      if (opts.onSelectPlace) {
        (function (selectedId) {
          g.addEventListener("click", function () {
            opts.onSelectPlace(selectedId);
          });
          g.addEventListener("keydown", function (ev) {
            if (ev.key === "Enter" || ev.key === " ") {
              ev.preventDefault();
              opts.onSelectPlace(selectedId);
            }
          });
        })(place.id);
      }

      buildingNodes[place.id] = g;
      buildingLayer.appendChild(g);
    }
    svg.appendChild(buildingLayer);

    // Layer 4: Preposition / Relation overlay layer
    var relationLayer = svgEl("g", { "class": "atlas-relation-layer" });
    svg.appendChild(relationLayer);

    // Layer 5: Route overlay layer
    var routeLayer = svgEl("g", { "class": "atlas-route-layer" });
    svg.appendChild(routeLayer);

    // Compass rose in top-right (clear of Hospital and streets)
    var compassG = svgEl("g", { transform: "translate(728, 46)" });
    compassG.appendChild(svgEl("circle", { cx: 0, cy: 0, r: 22, fill: "#FFFFFF", stroke: "#B9B1A1", "stroke-width": "1.2" }));
    compassG.appendChild(svgEl("polygon", { points: "0,-15 4,-3 -4,-3", fill: "#C84B31" }));
    compassG.appendChild(svgEl("polygon", { points: "0,15 4,3 -4,3", fill: "#D8D3C8" }));
    compassG.appendChild(svgEl("text", { x: 0, y: -17, "text-anchor": "middle", "font-family": "Geist Mono, monospace", "font-size": "8.5", "font-weight": "700", fill: "#C84B31" }, "N"));
    compassG.appendChild(svgEl("text", { x: 0, y: 24, "text-anchor": "middle", "font-family": "Geist Mono, monospace", "font-size": "8", fill: "#4D5761" }, "S"));
    compassG.appendChild(svgEl("text", { x: 18, y: 3, "text-anchor": "middle", "font-family": "Geist Mono, monospace", "font-size": "8", fill: "#4D5761" }, "E"));
    compassG.appendChild(svgEl("text", { x: -18, y: 3, "text-anchor": "middle", "font-family": "Geist Mono, monospace", "font-size": "8", fill: "#4D5761" }, "W"));
    svg.appendChild(compassG);

    // Scale bar in bottom-left
    var scaleG = svgEl("g", { transform: "translate(20, 496)" });
    scaleG.appendChild(svgEl("rect", { x: 0, y: -14, width: 118, height: 22, rx: 4, fill: "rgba(255,255,255,0.9)", stroke: "#D8D3C8", "stroke-width": "1" }));
    scaleG.appendChild(svgEl("line", { x1: 10, y1: -2, x2: 70, y2: -2, stroke: "#171C22", "stroke-width": "2" }));
    scaleG.appendChild(svgEl("line", { x1: 10, y1: -6, x2: 10, y2: 2, stroke: "#171C22", "stroke-width": "1.5" }));
    scaleG.appendChild(svgEl("line", { x1: 70, y1: -6, x2: 70, y2: 2, stroke: "#171C22", "stroke-width": "1.5" }));
    scaleG.appendChild(svgEl("text", { x: 78, y: 1, "font-family": "Geist Mono, monospace", "font-size": "9", fill: "#4D5761" }, "3 m"));
    svg.appendChild(scaleG);

    container.innerHTML = "";
    container.appendChild(svg);

    function setSelected(placeId) {
      var ids = Object.keys(buildingNodes);
      for (var i = 0; i < ids.length; i += 1) {
        var id = ids[i];
        buildingNodes[id].classList.toggle("is-selected", id === placeId);
      }
    }

    function placeBox(place) {
      var hw = toSvg.w(place.width) / 2;
      var hh = toSvg.h(place.depth) / 2;
      var cx = toSvg.x(place.x);
      var cy = toSvg.y(place.y);
      return { cx: cx, cy: cy, left: cx - hw, right: cx + hw, top: cy - hh, bottom: cy + hh };
    }

    function addPill(cx, cy, text) {
      var tagW = Math.max(76, text.length * 7.8 + 18);
      relationLayer.appendChild(svgEl("rect", {
        x: cx - tagW / 2, y: cy - 11, width: tagW, height: 22, rx: 11, fill: "#1B6B4A"
      }));
      relationLayer.appendChild(svgEl("text", {
        x: cx, y: cy + 3.5, "text-anchor": "middle",
        "font-family": "Geist Mono, monospace", "font-size": "10.5", "font-weight": "700", fill: "#FFFFFF"
      }, text));
    }

    function addDot(x, y, isSubject) {
      relationLayer.appendChild(svgEl("circle", {
        cx: x, cy: y, r: isSubject ? 5.5 : 4.5,
        fill: isSubject ? "#C84B31" : "#1B6B4A",
        stroke: "#FFFFFF", "stroke-width": "1.5"
      }));
    }

    function highlightPreposition(prep) {
      relationLayer.innerHTML = "";
      var activeIds = {};
      activeIds[prep.subjectId] = true;
      for (var r = 0; r < prep.referenceIds.length; r += 1) {
        activeIds[prep.referenceIds[r]] = true;
      }

      var ids = Object.keys(buildingNodes);
      for (var i = 0; i < ids.length; i += 1) {
        var id = ids[i];
        var isActive = Boolean(activeIds[id]);
        buildingNodes[id].classList.toggle("is-selected", isActive);
        buildingNodes[id].classList.toggle("is-dimmed", !isActive);
      }

      var subj = findPlace(data, prep.subjectId);
      if (!subj) return;
      var sb = placeBox(subj);
      var refs = [];
      for (var j = 0; j < prep.referenceIds.length; j += 1) {
        var refObj = findPlace(data, prep.referenceIds[j]);
        if (refObj) refs.push(placeBox(refObj));
      }

      if (prep.id === "next-to" && refs[0]) {
        // Exterior top bracket clear of both labels
        var rb = refs[0];
        var yBr = Math.min(sb.top, rb.top) - 20;
        relationLayer.appendChild(svgEl("polyline", {
          points: sb.cx + "," + sb.top + " " + sb.cx + "," + yBr + " " + rb.cx + "," + yBr + " " + rb.cx + "," + rb.top,
          fill: "none", stroke: "#1B6B4A", "stroke-width": "2.4", "stroke-dasharray": "5 3"
        }));
        addDot(sb.cx, sb.top, true);
        addDot(rb.cx, rb.top, false);
        addPill((sb.cx + rb.cx) / 2, yBr, prep.label);
      } else if (prep.id === "opposite" && refs[0]) {
        // Facing street edges across River Road
        var refOpp = refs[0];
        var sxEdge = sb.cx > refOpp.cx ? sb.left : sb.right;
        var rxEdge = sb.cx > refOpp.cx ? refOpp.right : refOpp.left;
        var midX = (sxEdge + rxEdge) / 2;
        relationLayer.appendChild(svgEl("line", {
          x1: sxEdge, y1: sb.cy, x2: rxEdge, y2: refOpp.cy,
          stroke: "#1B6B4A", "stroke-width": "2.6", "stroke-dasharray": "5 4"
        }));
        relationLayer.appendChild(svgEl("line", {
          x1: midX, y1: sb.cy, x2: midX, y2: sb.cy - 54,
          stroke: "#1B6B4A", "stroke-width": "1.6"
        }));
        addDot(sxEdge, sb.cy, true);
        addDot(rxEdge, refOpp.cy, false);
        addPill(midX, sb.cy - 64, prep.label);
      } else if (prep.id === "between" && refs.length >= 2) {
        // Exterior top bracket linking Post Office, Restaurant, and Bookstore along top edges
        var leftB = refs[0];
        var rightB = refs[1];
        var yTopBr = Math.min(leftB.top, sb.top, rightB.top) - 20;
        relationLayer.appendChild(svgEl("polyline", {
          points: leftB.cx + "," + leftB.top + " " + leftB.cx + "," + yTopBr + " " + rightB.cx + "," + yTopBr + " " + rightB.cx + "," + rightB.top,
          fill: "none", stroke: "#1B6B4A", "stroke-width": "2.4", "stroke-dasharray": "5 3"
        }));
        relationLayer.appendChild(svgEl("line", {
          x1: sb.cx, y1: sb.top, x2: sb.cx, y2: yTopBr,
          stroke: "#C84B31", "stroke-width": "2.4"
        }));
        addDot(leftB.cx, leftB.top, false);
        addDot(rightB.cx, rightB.top, false);
        addDot(sb.cx, sb.top, true);
        addPill(sb.cx, yTopBr - 16, prep.label);
      } else if ((prep.id === "in-front-of" || prep.id === "behind") && refs[0]) {
        // Exterior right-side bracket in clear corridor east of Bookstore & Bus Stop
        var refPair = refs[0];
        var xSide = Math.max(sb.right, refPair.right) + 18;
        var yMid = (sb.cy + refPair.cy) / 2;
        var sEdgeX = sb.right + 4;
        var rEdgeX = refPair.right + 4;
        relationLayer.appendChild(svgEl("polyline", {
          points: sEdgeX + "," + sb.cy + " " + xSide + "," + sb.cy + " " + xSide + "," + refPair.cy + " " + rEdgeX + "," + refPair.cy,
          fill: "none", stroke: "#1B6B4A", "stroke-width": "2.4", "stroke-dasharray": "5 3"
        }));
        relationLayer.appendChild(svgEl("line", {
          x1: xSide, y1: yMid, x2: xSide + 14, y2: yMid,
          stroke: "#1B6B4A", "stroke-width": "1.6"
        }));
        addDot(sEdgeX, sb.cy, true);
        addDot(rEdgeX, refPair.cy, false);
        addPill(xSide + 54, yMid, prep.label);
      } else if (prep.id === "near" && refs[0]) {
        // Connect facing east/west edges across open gap between My House and School
        var refNear = refs[0];
        var xStart = sb.right;
        var xEnd = refNear.left;
        var midNearX = (xStart + xEnd) / 2;
        relationLayer.appendChild(svgEl("line", {
          x1: xStart, y1: sb.cy, x2: xEnd, y2: refNear.cy,
          stroke: "#1B6B4A", "stroke-width": "2.6", "stroke-dasharray": "5 4"
        }));
        addDot(xStart, sb.cy, true);
        addDot(xEnd, refNear.cy, false);
        addPill(midNearX, sb.cy - 22, prep.label);
      }
    }

    function drawRoute(route) {
      routeLayer.innerHTML = "";
      if (!route) return null;

      var ids = Object.keys(buildingNodes);
      for (var i = 0; i < ids.length; i += 1) {
        var id = ids[i];
        var isTarget = id === route.targetId;
        var isSecondary = route.secondaryIds && route.secondaryIds.indexOf(id) !== -1;
        buildingNodes[id].classList.toggle("is-route-target", isTarget);
        buildingNodes[id].classList.toggle("is-selected", isSecondary);
      }

      var pts = [];
      for (var w = 0; w < route.waypoints.length; w += 1) {
        var wp = route.waypoints[w];
        pts.push({ x: toSvg.x(wp.x), y: toSvg.y(wp.y), label: wp.label });
      }
      var targetSvg = { x: toSvg.x(route.targetPoint.x), y: toSvg.y(route.targetPoint.y) };
      var lastPt = pts[pts.length - 1];

      var pathD = "M " + pts[0].x + " " + pts[0].y;
      for (var p = 1; p < pts.length; p += 1) {
        pathD += " L " + pts[p].x + " " + pts[p].y;
      }

      // Soft halo underneath route path
      routeLayer.appendChild(svgEl("path", {
        d: pathD,
        fill: "none",
        stroke: "rgba(200, 75, 49, 0.22)",
        "stroke-width": "12",
        "stroke-linecap": "round",
        "stroke-linejoin": "round"
      }));

      // Main route path
      var routePath = svgEl("path", {
        d: pathD,
        "class": "atlas-route-line"
      });
      routeLayer.appendChild(routePath);

      // Final pointer leg stops cleanly at the target building edge (never crossing label text)
      var targetPlace = findPlace(data, route.targetId);
      var edgeX = targetSvg.x;
      var edgeY = targetSvg.y;
      if (targetPlace) {
        var halfW = toSvg.w(targetPlace.width) / 2;
        var halfH = toSvg.h(targetPlace.depth) / 2;
        var dx = targetSvg.x - lastPt.x;
        var dy = targetSvg.y - lastPt.y;
        if (Math.abs(dx) >= Math.abs(dy)) {
          edgeX = targetSvg.x - Math.sign(dx) * (halfW + 6);
          edgeY = targetSvg.y;
        } else {
          edgeX = targetSvg.x;
          edgeY = targetSvg.y - Math.sign(dy) * (halfH + 6);
        }
      }

      routeLayer.appendChild(svgEl("line", {
        x1: lastPt.x,
        y1: lastPt.y,
        x2: edgeX,
        y2: edgeY,
        stroke: "#C84B31",
        "stroke-width": "3",
        "stroke-dasharray": "4 4"
      }));

      var ptrAng = Math.atan2(edgeY - lastPt.y, edgeX - lastPt.x) * (180 / Math.PI);
      routeLayer.appendChild(svgEl("polygon", {
        points: "5,0 -5,-4.5 -5,4.5",
        fill: "#C84B31",
        transform: "translate(" + edgeX + " " + edgeY + ") rotate(" + ptrAng + ")"
      }));

      // Waypoint markers
      for (var m = 0; m < pts.length; m += 1) {
        routeLayer.appendChild(svgEl("circle", {
          cx: pts[m].x,
          cy: pts[m].y,
          r: m === 0 ? 7 : 5.5,
          fill: m === 0 ? "#1B6B4A" : "#C84B31",
          stroke: "#FFFFFF",
          "stroke-width": "2"
        }));
      }

      // Start badge
      routeLayer.appendChild(svgEl("rect", {
        x: pts[0].x - 22,
        y: pts[0].y + 12,
        width: 48,
        height: 18,
        rx: 9,
        fill: "#1B6B4A"
      }));
      routeLayer.appendChild(svgEl("text", {
        x: pts[0].x + 2,
        y: pts[0].y + 24,
        "text-anchor": "middle",
        "font-family": "Geist Mono, monospace",
        "font-size": "9.5",
        "font-weight": "700",
        fill: "#FFFFFF"
      }, "START"));

      // Animated directional walker beacon (placed at origin 0,0 and moved via transform)
      var walker = svgEl("g", { "class": "atlas-walker-group" });
      walker.appendChild(svgEl("circle", {
        cx: 0, cy: 0, r: 10,
        fill: "#C84B31",
        stroke: "#FFFFFF",
        "stroke-width": "2.4"
      }));
      walker.appendChild(svgEl("polygon", {
        points: "5,0 -3,-4 -1,0 -3,4",
        fill: "#FFFFFF"
      }));
      routeLayer.appendChild(walker);

      return {
        points: pts,
        walker: walker,
        routePath: routePath
      };
    }

    return {
      svg: svg,
      setSelected: setSelected,
      highlightPreposition: highlightPreposition,
      drawRoute: drawRoute
    };
  }

  globalScope.ATLAS_SVG = {
    renderAtlasSvg: renderAtlasSvg
  };
})(typeof window !== "undefined" ? window : globalThis);
