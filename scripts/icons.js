(function (globalScope) {
  "use strict";

  var ICON_KEY_MAP = {
    "compass": "Compass",
    "map-pin": "MapPin",
    "route": "Route",
    "navigation": "Navigation",
    "arrow-up": "ArrowUp",
    "corner-up-left": "CornerUpLeft",
    "corner-up-right": "CornerUpRight",
    "home": "Home",
    "school": "School",
    "trees": "Trees",
    "store": "Store",
    "shopping-cart": "ShoppingCart",
    "hospital": "Hospital",
    "cross": "Cross",
    "utensils": "Utensils",
    "mail": "Mail",
    "book-open": "BookOpen",
    "bus": "Bus",
    "users": "Users",
    "message-circle": "MessageCircle",
    "play": "Play",
    "pause": "Pause",
    "rotate-ccw": "RotateCcw",
    "chevron-left": "ChevronLeft",
    "chevron-right": "ChevronRight",
    "grid": "LayoutGrid",
    "layout-grid": "LayoutGrid",
    "file-text": "FileText",
    "maximize-2": "Maximize2",
    "x": "X",
    "volume-2": "Volume2",
    "check-circle": "CircleCheck",
    "circle-check": "CircleCheck",
    "map": "Map"
  };

  function createIconSvg(name, extraClass) {
    var cls = "icon" + (extraClass ? " " + extraClass : "");
    var lucideLib = globalScope.lucide;
    var pascalName = ICON_KEY_MAP[name];

    if (lucideLib && lucideLib.icons && pascalName && lucideLib.icons[pascalName] && typeof lucideLib.createElement === "function") {
      var el = lucideLib.createElement(lucideLib.icons[pascalName], {
        "class": cls,
        "aria-hidden": "true"
      });
      return el;
    }

    // Fallback to offline SVG sprite reference
    var svgNS = "http://www.w3.org/2000/svg";
    var svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("class", cls);
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    var use = document.createElementNS(svgNS, "use");
    use.setAttribute("href", "assets/icons/sprite.svg#" + name);
    svg.appendChild(use);
    return svg;
  }

  function hydrateIcons(root) {
    var scope = root || document;
    var placeholders = scope.querySelectorAll("[data-icon]");
    for (var i = 0; i < placeholders.length; i += 1) {
      var node = placeholders[i];
      var name = node.getAttribute("data-icon");
      var extraClass = node.getAttribute("data-icon-class") || "";
      var svg = createIconSvg(name, extraClass);
      node.replaceWith(svg);
    }
  }

  globalScope.ATLAS_ICONS = {
    createIconSvg: createIconSvg,
    hydrateIcons: hydrateIcons
  };
})(typeof window !== "undefined" ? window : globalThis);
