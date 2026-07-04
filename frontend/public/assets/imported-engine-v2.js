(function () {
  var names = ["Amira", "Daniel", "Leah", "Noah", "Priya", "Sam"];
  var materials = ["copper", "aluminium", "magnesium", "iron"];
  var places = ["Leeds", "Bristol", "York", "Norwich", "Exeter", "Derby"];

  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function choose(items) {
    return items[randomInt(0, items.length - 1)];
  }

  function simplifyPrompt(prompt) {
    return prompt
      .replace(/\bcalculate\b/gi, "work out")
      .replace(/\bdetermine\b/gi, "find")
      .replace(/\bevaluate\b/gi, "work out")
      .replace(/\bstate whether\b/gi, "say if")
      .replace(/\bexplain why\b/gi, "say why")
      .replace(/\btherefore\b/gi, "so")
      .replace(/\bapproximately\b/gi, "about")
      .replace(/\butilise\b/gi, "use")
      .replace(/\bdemonstrate\b/gi, "show")
      .replace(/\s+/g, " ")
      .trim();
  }

  function normalizeSubject(subject) {
    return subject === "maths" ? "mathematics" : subject;
  }

  function displaySubject(subject) {
    if (subject === "maths" || subject === "mathematics") return "Mathematics";
    return subject ? subject.charAt(0).toUpperCase() + subject.slice(1) : "Study";
  }

  function inferTopic(context) {
    var title = (context.title || "").toLowerCase();
    var subject = normalizeSubject(context.subject || "");

    if (subject === "mathematics") {
      if (title.includes("ratio")) return "Ratios";
      if (title.includes("algebra") || title.includes("equation")) return "Algebra";
      if (title.includes("probability")) return "Probability";
      if (title.includes("graph")) return "Graphs";
      if (title.includes("circle") || title.includes("area")) return "Geometry";
      return context.kind === "paper" ? "Exam Practice" : "Core Skills";
    }

    if (subject === "physics") {
      if (title.includes("electric")) return "Electricity";
      if (title.includes("force")) return "Forces";
      if (title.includes("wave")) return "Waves";
      if (title.includes("radioactivity")) return "Radioactivity";
      return context.kind === "paper" ? "Exam Practice" : "Physics Skills";
    }

    if (subject === "chemistry") {
      if (title.includes("bond")) return "Bonding";
      if (title.includes("rate")) return "Rates";
      if (title.includes("atom")) return "Atomic Structure";
      if (title.includes("equilibrium")) return "Equilibrium";
      return context.kind === "paper" ? "Exam Practice" : "Chemistry Skills";
    }

    return "Study Skills";
  }

  function createLineGraphDiagram(title, values) {
    return {
      type: "line-graph",
      title: title,
      values: values
    };
  }

  function mathsBlueprints(context) {
    var topic = inferTopic(context);
    return [
      {
        id: "imported-maths-numeric",
        topic: topic,
        generate: function () {
          if (topic === "Ratios") {
            var left = randomInt(2, 5);
            var right = randomInt(3, 7);
            var multiplier = randomInt(4, 8);
            var total = (left + right) * multiplier;
            return {
              prompt: "This imported route is about " + context.title + ". A prize of £" + total + " is shared in the ratio " + left + ":" + right + ". Work out how much the second person gets.",
              answer: "£" + (right * multiplier),
              workedSolution: [
                "Add the parts in the ratio: " + left + " + " + right + " = " + (left + right) + ".",
                "Find one part: £" + total + " ÷ " + (left + right) + " = £" + multiplier + ".",
                "Multiply by the second share: " + right + " × £" + multiplier + " = £" + (right * multiplier) + "."
              ],
              marks: 4
            };
          }

          if (topic === "Graphs") {
            var monthOne = randomInt(10, 12);
            var monthTwo = monthOne + randomInt(-1, 1);
            var monthThree = monthTwo + randomInt(2, 4);
            var monthFour = monthThree + randomInt(0, 2);
            var monthFive = monthFour + randomInt(-1, 1);
            var monthSix = monthFive + randomInt(2, 4);
            var values = [monthOne, monthTwo, monthThree, monthFour, monthFive, monthSix];
            var increase = monthThree - monthTwo;
            return {
              prompt: "Use the ideas from " + context.title + ". The line graph shows how many books a student read over 6 months. How many books were read in month 6, and what was the increase from month 2 to month 3?",
              answer: "Month 6: " + monthSix + " books. Increase: " + increase + " books.",
              workedSolution: [
                "Read the month 6 point on the graph: it is " + monthSix + ".",
                "Read months 2 and 3: " + monthTwo + " and " + monthThree + ".",
                "Work out the increase: " + monthThree + " - " + monthTwo + " = " + increase + "."
              ],
              marks: 6,
              diagram: createLineGraphDiagram("Number of Books Read", values)
            };
          }

          var x = randomInt(3, 12);
          var a = randomInt(2, 6);
          var b = randomInt(3, 15);
          var c = a * x + b;
          return {
            prompt: "Use the skill from " + context.title + ". Work out x in " + a + "x + " + b + " = " + c + ".",
            answer: "x = " + x,
            workedSolution: [
              "Subtract " + b + " from both sides to get " + a + "x = " + (c - b) + ".",
              "Divide both sides by " + a + ".",
              "So x = " + x + "."
            ],
            marks: 3
          };
        }
      },
      {
        id: "imported-maths-wordy",
        topic: "Exam Technique",
        generate: function () {
          var student = choose(names);
          return {
            prompt: student + ' is using the imported route "' + context.title + '" to revise. Explain how they should check whether a method is suitable before finishing an exam question.',
            answer: "A strong answer should choose the right method for the topic, show each step clearly, and check whether the final answer makes sense in the context of the question.",
            workedSolution: [
              "Name the method that fits the topic.",
              "Explain what evidence in the question tells you to use that method.",
              "Say how to check the answer at the end."
            ],
            marks: 4
          };
        }
      }
    ];
  }

  function physicsBlueprints(context) {
    var topic = inferTopic(context);
    return [
      {
        id: "imported-physics-numeric",
        topic: topic,
        generate: function () {
          var speed = randomInt(8, 20);
          var time = randomInt(5, 12);
          var distance = speed * time;
          return {
            prompt: "Use the ideas from " + context.title + ". An object travels " + distance + " m in " + time + " s. Work out its speed.",
            answer: speed + " m/s",
            workedSolution: [
              "Use speed = distance ÷ time.",
              distance + " ÷ " + time + " = " + speed + ".",
              "So the speed is " + speed + " m/s."
            ],
            marks: 3
          };
        }
      },
      {
        id: "imported-physics-wordy",
        topic: "Explain Your Thinking",
        generate: function () {
          var material = choose(materials);
          return {
            prompt: 'A student is revising "' + context.title + '" and tests a ' + material + " sample. Explain one physics idea they should mention to justify their answer.",
            answer: "A strong answer should name the relevant physics relationship, use the right key term, and connect it directly to the evidence in the question.",
            workedSolution: [
              "Name the correct law, formula, or process.",
              "Link that idea to the evidence or numbers in the question.",
              "Finish with a clear conclusion."
            ],
            marks: 4
          };
        }
      }
    ];
  }

  function chemistryBlueprints(context) {
    var topic = inferTopic(context);
    return [
      {
        id: "imported-chemistry-numeric",
        topic: topic,
        generate: function () {
          var mass = randomInt(12, 40);
          var mr = choose([12, 20, 24, 28, 40]);
          var moles = Number((mass / mr).toFixed(2));
          return {
            prompt: "Using the ideas from " + context.title + ", a sample has a mass of " + mass + " g and Mr " + mr + ". Work out the number of moles.",
            answer: moles + " mol",
            workedSolution: [
              "Use moles = mass ÷ Mr.",
              mass + " ÷ " + mr + " = " + moles + ".",
              "So the sample contains " + moles + " mol."
            ],
            marks: 3
          };
        }
      },
      {
        id: "imported-chemistry-wordy",
        topic: "Scientific Explanation",
        generate: function () {
          var place = choose(places);
          return {
            prompt: 'A class in ' + place + ' is revising "' + context.title + '". Explain one chemistry point that would make an answer clear and accurate.',
            answer: "A strong answer should use the correct chemistry term, explain what is happening at particle level where relevant, and link the science directly to the question.",
            workedSolution: [
              "Use the exact chemistry term you need.",
              "Add a short scientific reason.",
              "Link that reason back to the question."
            ],
            marks: 4
          };
        }
      }
    ];
  }

  function buildBlueprints(context) {
    var subject = normalizeSubject(context.subject || "");
    if (subject === "mathematics") return mathsBlueprints(context);
    if (subject === "physics") return physicsBlueprints(context);
    if (subject === "chemistry") return chemistryBlueprints(context);
    return [];
  }

  function describeContext(context) {
    return displaySubject(context.subject) + " · " + (context.board || "").toUpperCase() + " · " + (context.level || "").toUpperCase();
  }

  window.BoostAIImportedEngine = {
    simplifyPrompt: simplifyPrompt,
    normalizeSubject: normalizeSubject,
    displaySubject: displaySubject,
    inferTopic: inferTopic,
    buildBlueprints: buildBlueprints,
    describeContext: describeContext
  };
}());
