(function (globalScope) {
  "use strict";

  var ATLAS_DATA = {
    meta: {
      title: "My Neighbourhood: Let's Find the Way!",
      neighbourhoodName: "Greenleaf Neighbourhood",
      grade: "Grade 6 English Project",
      deadline: "29/11/2026"
    },
    bounds: {
      minX: -18,
      maxX: 21,
      minY: -11,
      maxY: 15,
      scalePxPerMeter: 20,
      svgWidth: 780,
      svgHeight: 520
    },
    streets: [
      {
        id: "oak-street",
        name: "Oak Street",
        ordinalLabel: "North E-W Street",
        axis: "horizontal",
        centerCoord: 6.0,
        roadWidth: 2.6,
        corridorWidth: 3.6,
        corridorMin: 4.2,
        corridorMax: 7.8,
        spanMin: -16.0,
        spanMax: 19.0
      },
      {
        id: "maple-street",
        name: "Maple Street",
        ordinalLabel: "South Main Street",
        axis: "horizontal",
        centerCoord: -6.0,
        roadWidth: 2.6,
        corridorWidth: 3.6,
        corridorMin: -7.8,
        corridorMax: -4.2,
        spanMin: -16.0,
        spanMax: 19.0
      },
      {
        id: "pine-street",
        name: "Pine Street",
        ordinalLabel: "1st Cross Street",
        axis: "vertical",
        centerCoord: -2.0,
        roadWidth: 2.6,
        corridorWidth: 3.6,
        corridorMin: -3.8,
        corridorMax: -0.2,
        spanMin: -11.0,
        spanMax: 14.0
      },
      {
        id: "river-road",
        name: "River Road",
        ordinalLabel: "2nd Cross Street",
        axis: "vertical",
        centerCoord: 12.0,
        roadWidth: 2.6,
        corridorWidth: 3.6,
        corridorMin: 10.2,
        corridorMax: 13.8,
        spanMin: -11.0,
        spanMax: 14.0
      }
    ],
    landmarks: [
      {
        id: "my-house",
        number: 1,
        name: "My House",
        ipa: "/maɪ ˈhaʊs/",
        x: -9.5,
        y: 10.5,
        width: 4.0,
        depth: 3.4,
        facing: "south",
        street: "Oak Street",
        icon: "home",
        image: "assets/blender/my-house.png",
        sentence: "My house is on Oak Street, near the school.",
        detail: "A warm family home with a pitched terracotta roof and front porch facing Oak Street.",
        dioramaPinPct: { x: 25.98, y: 40.59 }
      },
      {
        id: "school",
        number: 2,
        name: "School",
        ipa: "/skuːl/",
        x: 2.2,
        y: 10.5,
        width: 4.2,
        depth: 3.6,
        facing: "south",
        street: "Oak Street",
        icon: "school",
        image: "assets/blender/school.png",
        sentence: "We study English here every day. It is next to the park.",
        detail: "Greenleaf Secondary School has a clock gable, flag mast, and arched entrance on Oak Street.",
        dioramaPinPct: { x: 45.0, y: 33.68 }
      },
      {
        id: "park",
        number: 3,
        name: "Park",
        ipa: "/pɑːk/",
        x: 7.5,
        y: 10.5,
        width: 4.8,
        depth: 3.6,
        facing: "south",
        street: "Oak Street",
        icon: "trees",
        image: "assets/blender/park.png",
        sentence: "Our favourite place! We play sports and relax under the trees.",
        detail: "A sunlit community garden with stone paths, wooden benches, a central fountain, and shade trees.",
        dioramaPinPct: { x: 52.94, y: 30.79 }
      },
      {
        id: "post-office",
        number: 4,
        name: "Post Office",
        ipa: "/ˈpəʊst ˌɒf.ɪs/",
        x: -13.0,
        y: -1.5,
        width: 3.2,
        depth: 3.0,
        facing: "south",
        street: "Maple Street",
        icon: "mail",
        image: "assets/blender/post-office.png",
        sentence: "People send letters and parcels here on Maple Street.",
        detail: "Brick-trimmed neighbourhood post office with a corner letterbox and parcel awning.",
        dioramaPinPct: { x: 25.19, y: 62.99 }
      },
      {
        id: "restaurant",
        number: 5,
        name: "Restaurant",
        ipa: "/ˈres.tər.ɒnt/",
        x: -9.2,
        y: -1.5,
        width: 3.4,
        depth: 3.0,
        facing: "south",
        street: "Maple Street",
        icon: "utensils",
        image: "assets/blender/restaurant.png",
        sentence: "The restaurant is between the post office and the bookstore.",
        detail: "A cosy family bistro with a striped awning and warm outdoor seating facing Maple Street.",
        dioramaPinPct: { x: 32.73, y: 59.77 }
      },
      {
        id: "bookstore",
        number: 6,
        name: "Bookstore",
        ipa: "/ˈbʊk.stɔː/",
        x: -5.6,
        y: -1.5,
        width: 2.8,
        depth: 3.0,
        facing: "south",
        street: "Maple Street",
        icon: "book-open",
        image: "assets/blender/bookstore.png",
        sentence: "We buy notebooks and English storybooks behind the bus stop.",
        detail: "Corner timber-framed bookstore with large display windows and roof signage.",
        dioramaPinPct: { x: 39.58, y: 55.6 }
      },
      {
        id: "bus-stop",
        number: 7,
        name: "Bus Stop",
        ipa: "/ˈbʌs stɒp/",
        x: -5.6,
        y: -4.3,
        width: 2.2,
        depth: 1.1,
        facing: "south",
        street: "Maple Street",
        icon: "bus",
        image: "assets/blender/bus-stop.png",
        sentence: "The bus stop is in front of the bookstore on Maple Street.",
        detail: "Covered glass-and-timber transit shelter with bench, route board, and waiting shuttle.",
        dioramaPinPct: { x: 41.54, y: 63.1 }
      },
      {
        id: "market",
        number: 8,
        name: "Market",
        ipa: "/ˈmɑː.kɪt/",
        x: 2.5,
        y: 0.0,
        width: 4.2,
        depth: 4.6,
        facing: "west",
        street: "Pine Street",
        icon: "store",
        image: "assets/blender/market.png",
        sentence: "Fresh fruit and flowers are sold here on Pine Street.",
        detail: "Open-air pitched market hall with fabric canopies facing west onto Pine Street.",
        dioramaPinPct: { x: 52.83, y: 48.27 }
      },
      {
        id: "supermarket",
        number: 9,
        name: "Supermarket",
        ipa: "/ˈsuː.pəˌmɑː.kɪt/",
        x: 7.6,
        y: 0.0,
        width: 4.2,
        depth: 4.6,
        facing: "east",
        street: "River Road",
        icon: "shopping-cart",
        image: "assets/blender/supermarket.png",
        sentence: "The supermarket is opposite the hospital on River Road.",
        detail: "Modern neighbourhood grocery store with broad glazed entrance facing east onto River Road.",
        dioramaPinPct: { x: 61.19, y: 44.78 }
      },
      {
        id: "hospital",
        number: 10,
        name: "Hospital",
        ipa: "/ˈhɒs.pɪ.təl/",
        x: 16.2,
        y: 0.0,
        width: 4.4,
        depth: 4.8,
        facing: "west",
        street: "River Road",
        icon: "hospital",
        image: "assets/blender/hospital.png",
        sentence: "Doctors care for patients here, opposite the supermarket.",
        detail: "Two-storey clinic with vermilion cross emblem and covered ambulance bay on River Road.",
        dioramaPinPct: { x: 74.35, y: 39.28 }
      }
    ],
    prepositions: [
      {
        id: "next-to",
        label: "next to",
        ipa: "/ˈnekst tuː/",
        meaningVi: "bên cạnh",
        subjectId: "school",
        referenceIds: ["park"],
        sentence: "The school is next to the park.",
        qaTab: "Where is the school?",
        qaAnswer: "It is on Oak Street, right next to the park.",
        relationNote: "Side-by-side along the north block of Oak Street (0.8m path between them)."
      },
      {
        id: "opposite",
        label: "opposite",
        ipa: "/ˈɒp.ə.zɪt/",
        meaningVi: "đối diện",
        subjectId: "hospital",
        referenceIds: ["supermarket"],
        sentence: "The hospital is opposite the supermarket.",
        qaTab: "Where is the hospital?",
        qaAnswer: "It is on River Road, directly opposite the supermarket.",
        relationNote: "Facing each other across River Road at y = 0.0m."
      },
      {
        id: "between",
        label: "between",
        ipa: "/bɪˈtwiːn/",
        meaningVi: "ở giữa",
        subjectId: "restaurant",
        referenceIds: ["post-office", "bookstore"],
        sentence: "The restaurant is between the post office and the bookstore.",
        qaTab: "Where is the restaurant?",
        qaAnswer: "It stands between the post office and the bookstore on Maple Street.",
        relationNote: "Centred at x = -9.2m between Post Office (-13.0m) and Bookstore (-5.6m)."
      },
      {
        id: "in-front-of",
        label: "in front of",
        ipa: "/ɪn ˈfrʌnt əv/",
        meaningVi: "ở phía trước",
        subjectId: "bus-stop",
        referenceIds: ["bookstore"],
        sentence: "The bus stop is in front of the bookstore.",
        qaTab: "Where is the bus stop?",
        qaAnswer: "It is on the Maple Street pavement in front of the bookstore.",
        relationNote: "Bus Stop sits at y = -4.3m directly south of Bookstore's front door."
      },
      {
        id: "behind",
        label: "behind",
        ipa: "/bɪˈhaɪnd/",
        meaningVi: "ở phía sau",
        subjectId: "bookstore",
        referenceIds: ["bus-stop"],
        sentence: "The bookstore is behind the bus stop.",
        qaTab: "Is the bookstore near the bus stop?",
        qaAnswer: "Yes! Looking from Maple Street, the bookstore is right behind the bus stop.",
        relationNote: "Bookstore stands at y = -1.5m directly north behind the Bus Stop."
      },
      {
        id: "near",
        label: "near",
        ipa: "/nɪə/",
        meaningVi: "ở gần",
        subjectId: "my-house",
        referenceIds: ["school"],
        sentence: "My house is near the school.",
        qaTab: "Is my house far from school?",
        qaAnswer: "No, my house is very near the school along Oak Street.",
        relationNote: "Both sit on the north side of Oak Street, a short walk apart."
      }
    ],
    qaPrompts: [
      {
        id: "qa-places",
        prompt: "What places are there in your neighbourhood?",
        answer: "There are ten places: my house, a school, a park, a post office, a restaurant, a bookstore, a bus stop, a market, a supermarket, and a hospital."
      },
      {
        id: "qa-where",
        prompt: "Where is the market?",
        answer: "The market is on Pine Street, behind the supermarket block and south of the school."
      },
      {
        id: "qa-near-far",
        prompt: "Is your house near or far from the hospital?",
        answer: "My house is near the school on Oak Street, and a little far from the hospital on River Road."
      }
    ],
    routes: [
      {
        id: "route-market",
        slideNumber: 6,
        targetId: "market",
        secondaryIds: [],
        title: "Asking for the Market",
        asker: "Gia Khanh",
        giver: "Phước",
        startLabel: "West Maple St",
        startFacing: "East",
        waypoints: [
          { x: -15.0, y: -6.0, label: "Start on Maple Street (facing East)" },
          { x: -2.0, y: -6.0, label: "1st junction: turn LEFT onto Pine Street" },
          { x: -2.0, y: 0.0, label: "Arrive beside Market on your RIGHT" }
        ],
        targetPoint: { x: 2.5, y: 0.0, side: "right" },
        steps: [
          "Start on Maple Street facing East.",
          "Go straight ahead to the first street (Pine Street).",
          "Turn left onto Pine Street and walk north.",
          "The market is on your right."
        ],
        dialogue: [
          {
            speaker: "Gia Khanh",
            role: "Visitor",
            line: "Excuse me. Could you tell me the way to the market, please?"
          },
          {
            speaker: "Phước",
            role: "Local guide",
            line: "Go straight ahead and turn left at the first street. The market is on your right."
          },
          {
            speaker: "Gia Khanh",
            role: "Visitor",
            line: "Thank you very much!"
          },
          {
            speaker: "Phước",
            role: "Local guide",
            line: "You're welcome!"
          }
        ]
      },
      {
        id: "route-hospital",
        slideNumber: 7,
        targetId: "hospital",
        secondaryIds: ["supermarket"],
        title: "Asking for the Hospital",
        asker: "Yến Nhi",
        giver: "Anh Thi",
        startLabel: "West Maple St",
        startFacing: "East",
        waypoints: [
          { x: -15.0, y: -6.0, label: "Start on Maple Street (facing East)" },
          { x: -2.0, y: -6.0, label: "Pass 1st street (Pine Street)" },
          { x: 12.0, y: -6.0, label: "2nd junction: turn LEFT onto River Road" },
          { x: 12.0, y: 0.0, label: "Arrive beside Hospital on your RIGHT" }
        ],
        targetPoint: { x: 16.2, y: 0.0, side: "right" },
        steps: [
          "Go straight ahead on Maple Street past Pine Street.",
          "Reach the second cross street (River Road).",
          "Take the second turning on the left.",
          "The hospital is on your right, opposite the supermarket."
        ],
        dialogue: [
          {
            speaker: "Yến Nhi",
            role: "Visitor",
            line: "How can I get to the hospital?"
          },
          {
            speaker: "Anh Thi",
            role: "Local guide",
            line: "Go straight ahead, then take the second turning on the left onto River Road. The hospital is on your right, opposite the supermarket."
          },
          {
            speaker: "Yến Nhi",
            role: "Visitor",
            line: "Is it far from here?"
          },
          {
            speaker: "Anh Thi",
            role: "Local guide",
            line: "No, it's about a five-minute walk!"
          }
        ]
      },
      {
        id: "route-park",
        slideNumber: 8,
        targetId: "park",
        secondaryIds: ["school"],
        title: "Asking for the Park",
        asker: "Tùng Lâm",
        giver: "Tuấn Anh",
        startLabel: "Market Gate (Pine St)",
        startFacing: "North",
        waypoints: [
          { x: -2.0, y: 0.0, label: "Start outside Market on Pine Street (facing North)" },
          { x: -2.0, y: 6.0, label: "Junction with Oak Street: turn RIGHT" },
          { x: 7.5, y: 6.0, label: "Walk east past School; Park is on your LEFT" }
        ],
        targetPoint: { x: 7.5, y: 10.5, side: "left" },
        steps: [
          "Start outside the market on Pine Street facing North.",
          "Go straight ahead to Oak Street.",
          "Turn right onto Oak Street and walk past the school.",
          "The park is on your left, next to the school."
        ],
        dialogue: [
          {
            speaker: "Tùng Lâm",
            role: "Visitor",
            line: "Excuse me. How can I get to the park from the market?"
          },
          {
            speaker: "Tuấn Anh",
            role: "Local guide",
            line: "Go straight ahead to Oak Street, then turn right. Walk past the school. The park is on your left, next to the school."
          },
          {
            speaker: "Tùng Lâm",
            role: "Visitor",
            line: "Thank you so much!"
          },
          {
            speaker: "Tuấn Anh",
            role: "Local guide",
            line: "No problem!"
          }
        ]
      }
    ],
    directionsVocab: [
      { id: "straight", phrase: "go straight ahead", ipa: "/ɡəʊ streɪt əˈhed/", meaningVi: "đi thẳng về phía trước", icon: "arrow-up" },
      { id: "left", phrase: "turn left", ipa: "/tɜːn ˈleft/", meaningVi: "rẽ trái", icon: "corner-up-left" },
      { id: "right", phrase: "turn right", ipa: "/tɜːn ˈraɪt/", meaningVi: "rẽ phải", icon: "corner-up-right" },
      { id: "side", phrase: "on your left / right", ipa: "/ɒn jɔː ˈleft/ | /ɒn jɔː ˈraɪt/", meaningVi: "ở bên trái / phải của bạn", icon: "navigation" }
    ],
    students: [
      {
        id: "gia-khanh",
        name: "Gia Khanh",
        nameVi: "Gia Khanh",
        role: "Group Leader and MC",
        tasks: "Project plan, member tracking, opening welcome, Pair 1 asking directions",
        speakingSlides: "Slides 1, 2, 6, 10",
        contribution: "Led rehearsals and prepared the contribution ledger"
      },
      {
        id: "phuoc",
        name: "Phước",
        displayEn: "Phuoc",
        nameVi: "Phước",
        role: "Content and Pair 1 Guide",
        tasks: "Drafted 10-place sentences, gave directions to the Market",
        speakingSlides: "Slides 3, 4, 6",
        contribution: "Completed script and Market direction turn"
      },
      {
        id: "yen-nhi",
        name: "Yến Nhi",
        displayEn: "Yen Nhi",
        nameVi: "Yến Nhi",
        role: "Content and Pair 2 Asker",
        tasks: "Wrote introduction lines, led 6 preposition examples, asked the way to the Hospital",
        speakingSlides: "Slides 2, 5, 7",
        contribution: "Verified preposition pairs and Q&A lines"
      },
      {
        id: "anh-thi",
        name: "Anh Thi",
        displayEn: "Anh Thi",
        nameVi: "Anh Thi",
        role: "Pronunciation Checker and Pair 2 Guide",
        tasks: "Checked IPA pronunciation, gave directions to the Hospital, reviewed vocabulary",
        speakingSlides: "Slides 4, 5, 7, 9",
        contribution: "Coached team pronunciation and River Road route"
      },
      {
        id: "tung-lam",
        name: "Tùng Lâm",
        displayEn: "Tung Lam",
        nameVi: "Tùng Lâm",
        role: "Map Decorator and Pair 3 Asker",
        tasks: "Checked street layout and signs, asked the way to the Park, presented favourite place",
        speakingSlides: "Slides 3, 8, 11",
        contribution: "Verified street signs and Park closing"
      },
      {
        id: "tuan-anh",
        name: "Tuấn Anh",
        displayEn: "Tuan Anh",
        nameVi: "Tuấn Anh",
        role: "Slide Designer and Pair 3 Guide",
        tasks: "Designed interactive atlas and slides, gave directions to the Park, led Q&A map jump",
        speakingSlides: "Slides 8, 11, 12",
        contribution: "Built visual deck and 3D map integration"
      }
    ],
    presenterNotes: {
      1: {
        title: "Slide 1: Cover Plate",
        speakers: "Gia Khanh (Group Leader)",
        englishScript: "Good morning, teacher and classmates! We are Group Greenleaf: Gia Khanh, Phước, Yến Nhi, Anh Thi, Tùng Lâm, and Tuấn Anh. Today we present our map, My Neighbourhood: Let's Find the Way!",
        vietnameseTips: "Gia Khanh dẫn dắt tự tin, nhấn rõ tên khu phố Greenleaf Neighbourhood và mời lần lượt 5 bạn còn lại giơ tay chào theo tên trên màn hình."
      },
      2: {
        title: "Slide 2: Introduction",
        speakers: "Gia Khanh & Yến Nhi",
        englishScript: "Hello everyone! Welcome to our neighbourhood. This is an imagined neighbourhood that our group designed together. This is our map. It shows some interesting places in our neighbourhood. Let's have a look!",
        vietnameseTips: "Yến Nhi nói chậm rãi câu mở đầu gợi ý từ hướng dẫn của cô. Chú ý phát âm rõ âm cuối từ 'places' (/ˈpleɪ.sɪz/) và 'neighbourhood' (/ˈneɪ.bə.hʊd/)."
      },
      3: {
        title: "Slide 3: Interactive Neighbourhood Atlas",
        speakers: "Phước & Tùng Lâm",
        englishScript: "Our map has four streets: Oak Street, Maple Street, Pine Street, and River Road. You can see ten places here, from My House and School in the north to the Market, Supermarket, and Hospital.",
        vietnameseTips: "Phước bấm đổi qua lại giữa chế độ Street Atlas và 3D Diorama, bấm thử 2 đến 3 địa điểm (ví dụ My House, Park, Hospital) để lớp thấy hình 3D và câu mô tả."
      },
      4: {
        title: "Slide 4: Places in Our Neighbourhood",
        speakers: "Phước & Anh Thi",
        englishScript: "Let's look closely at all ten places in Greenleaf Neighbourhood: My House, School, Park, Post Office, Restaurant, Bookstore, Bus Stop, Market, Supermarket, and Hospital.",
        vietnameseTips: "Có thể bấm vào 1 hoặc 2 thẻ bất kỳ (ví dụ Restaurant hoặc Post Office) để mở hộp thoại xem mô hình 3D phóng lớn và đọc lại câu ví dụ."
      },
      5: {
        title: "Slide 5: Describing Locations",
        speakers: "Yến Nhi & Anh Thi",
        englishScript: "Where are the places? The school is next to the park. The hospital is opposite the supermarket. The restaurant is between the post office and the bookstore. The bus stop is in front of the bookstore, and the bookstore is behind the bus stop. My house is near the school.",
        vietnameseTips: "Bấm lần lượt từng nút giới từ (next to, opposite, between, in front of, behind, near) để khung xanh sáng đúng cặp công trình trên bản đồ và thử 3 tab câu hỏi Q&A."
      },
      6: {
        title: "Slide 6: Pair 1 Directions (Market)",
        speakers: "Gia Khanh & Phước",
        englishScript: "Gia Khanh: Excuse me. Could you tell me the way to the market, please? Phước: Go straight ahead and turn left at the first street. The market is on your right. Gia Khanh: Thank you very much! Phước: You're welcome!",
        vietnameseTips: "Bấm Play route hoặc Next step đúng nhịp đọc của Gia Khanh và Phước: đi thẳng đường Maple Street về hướng Đông, rẽ trái tại ngã rẽ đầu tiên (Pine Street), chợ nằm bên tay phải."
      },
      7: {
        title: "Slide 7: Pair 2 Directions (Hospital)",
        speakers: "Yến Nhi & Anh Thi",
        englishScript: "Yến Nhi: How can I get to the hospital? Anh Thi: Go straight ahead, then take the second turning on the left onto River Road. The hospital is on your right, opposite the supermarket. Yến Nhi: Is it far from here? Anh Thi: No, it's about a five-minute walk!",
        vietnameseTips: "Nhấn mạnh cụm 'second turning on the left' (ngã rẽ thứ hai bên trái, đi qua Pine Street tới River Road). Kiểm tra âm /ˈhɒs.pɪ.təl/."
      },
      8: {
        title: "Slide 8: Pair 3 Directions (Park)",
        speakers: "Tùng Lâm & Tuấn Anh",
        englishScript: "Tùng Lâm: Excuse me. How can I get to the park from the market? Tuấn Anh: Go straight ahead to Oak Street, then turn right. Walk past the school. The park is on your left, next to the school.",
        vietnameseTips: "Bắt đầu từ cổng Market trên Pine Street nhìn lên hướng Bắc, đi thẳng lên Oak Street, rẽ phải đi ngang qua School, công viên nằm bên tay trái."
      },
      9: {
        title: "Slide 9: Key Vocabulary & Prepositions",
        speakers: "Anh Thi",
        englishScript: "Here are the key words from our project: ten neighbourhood places, six prepositions of place, and four useful direction phrases.",
        vietnameseTips: "Anh Thi ôn nhanh từ khóa cho cả lớp: next to, opposite, between, in front of, behind, near và go straight ahead / turn left / turn right."
      },
      10: {
        title: "Slide 10: Teamwork & Contribution Ledger",
        speakers: "Gia Khanh (Group Leader)",
        englishScript: "As group leader, I tracked everyone's contribution. All six members shared tasks equally, designed the map and slides, and practised speaking English together.",
        vietnameseTips: "Bảng tổng kết nhiệm vụ và đóng góp đầy đủ của 6 thành viên (Gia Khanh, Phước, Yến Nhi, Anh Thi, Tùng Lâm, Tuấn Anh) theo đúng yêu cầu chấm điểm."
      },
      11: {
        title: "Slide 11: Conclusion & Favourite Place",
        speakers: "Tùng Lâm & Tuấn Anh",
        englishScript: "Our neighbourhood has many useful and interesting places. Our favourite place is the park, because we can play sports, read books, and relax with our friends. That is our neighbourhood map. We hope you like it. Thank you for listening!",
        vietnameseTips: "Tùng Lâm đọc phần lý do thích Park; cả nhóm đồng thanh đọc câu kết 'Thank you for listening!'."
      },
      12: {
        title: "Slide 12: Thank You & Live Q&A",
        speakers: "Tuấn Anh & Cả nhóm",
        englishScript: "Thank you for your attention! If you have any questions about our map, we are happy to show you any route live.",
        vietnameseTips: "Khi cô giáo hoặc các bạn hỏi đường bất kỳ trên bản đồ, bấm nút 'Jump to Interactive Map' để quay ngay về Slide 3 thao tác trực tiếp."
      }
    }
  };

  globalScope.ATLAS_DATA = ATLAS_DATA;
  if (typeof module !== "undefined" && module.exports) {
    module.exports = ATLAS_DATA;
  }
})(typeof window !== "undefined" ? window : globalThis);
