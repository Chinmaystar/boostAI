(function () {
  var importedEngine = window.BoostAIImportedEngine;
  var subjects = [
    {
      slug: "mathematics",
      name: "Mathematics",
      icon: "📐",
      description: "Algebra, ratios, graphs, and exam-style numerical reasoning."
    },
    {
      slug: "physics",
      name: "Physics",
      icon: "⚡",
      description: "Motion, energy, circuits, and clear step-by-step calculations."
    },
    {
      slug: "chemistry",
      name: "Chemistry",
      icon: "⚗️",
      description: "Moles, formulas, bonding, and reaction calculations."
    },
    {
      slug: "biology",
      name: "Biology",
      icon: "🧬",
      description: "Processes, data interpretation, and simple science explanations."
    },
    {
      slug: "english",
      name: "English",
      icon: "📝",
      description: "Readable literature analysis and clear writing prompts."
    },
    {
      slug: "history",
      name: "History",
      icon: "🏛️",
      description: "Cause, consequence, interpretation, and evidence-based answers."
    },
    {
      slug: "geography",
      name: "Geography",
      icon: "🌍",
      description: "Fieldwork, data analysis, ecosystems, and human geography."
    }
  ];

  var names = ["Amira", "Daniel", "Leah", "Noah", "Priya", "Sam"];
  var places = ["Leeds", "Bristol", "York", "Norwich", "Exeter", "Derby"];
  var materials = ["copper", "aluminium", "iron", "glass"];
  var rivers = ["the River Tees", "the River Mersey", "the River Severn"];
  var texts = ["the extract", "the poem", "the opening paragraph"];

  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  function choose(items) {
    return items[randomInt(0, items.length - 1)];
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function simplifyPrompt(prompt) {
    if (importedEngine) {
      return importedEngine.simplifyPrompt(prompt);
    }

    return prompt
      .replace(/\bcalculate\b/gi, "work out")
      .replace(/\bdetermine\b/gi, "find")
      .replace(/\bevaluate\b/gi, "work out")
      .replace(/\bstate whether\b/gi, "say if")
      .replace(/\bexplain why\b/gi, "say why")
      .replace(/\btherefore\b/gi, "so")
      .replace(/\bconsequently\b/gi, "so")
      .replace(/\bapproximately\b/gi, "about")
      .replace(/\butilise\b/gi, "use")
      .replace(/\bdemonstrate\b/gi, "show")
      .replace(/\s+/g, " ")
      .trim();
  }

  function markLabel(marks) {
    return marks === 1 ? "mark" : "marks";
  }

  function createLineGraphDiagram(title, values) {
    return {
      type: "line-graph",
      title: title,
      values: values
    };
  }

  function graphDiagramMarkup(diagram) {
    var values = diagram.values || [];
    if (!values.length) return "";

    var width = 620;
    var height = 340;
    var left = 70;
    var right = 26;
    var top = 28;
    var bottom = 44;
    var plotWidth = width - left - right;
    var plotHeight = height - top - bottom;
    var yMin = Math.max(0, Math.min.apply(null, values) - 1);
    var yMax = Math.max.apply(null, values) + 1;
    var yRange = Math.max(1, yMax - yMin);
    var xStep = values.length > 1 ? plotWidth / (values.length - 1) : plotWidth;
    var polyline = values.map(function (value, index) {
      var x = left + index * xStep;
      var y = top + ((yMax - value) / yRange) * plotHeight;
      return x.toFixed(1) + "," + y.toFixed(1);
    }).join(" ");

    var yLabels = [];
    for (var yValue = yMin; yValue <= yMax; yValue += 1) {
      var yPosition = top + ((yMax - yValue) / yRange) * plotHeight;
      yLabels.push(
        '<text x="' + (left - 24) + '" y="' + (yPosition + 6).toFixed(1) + '" font-size="16" fill="#111319" text-anchor="end">' +
          escapeHtml(yValue) +
        "</text>"
      );
    }

    var xLabels = values.map(function (_, index) {
      var x = left + index * xStep;
      return '<text x="' + x.toFixed(1) + '" y="' + (height - 12) + '" font-size="16" fill="#111319" text-anchor="middle">' +
        escapeHtml(index + 1) +
      "</text>";
    }).join("");

    return (
      '<svg viewBox="0 0 620 340" role="img" aria-label="' + escapeHtml(diagram.title || "Line graph") + '">' +
        '<rect x="1" y="1" width="618" height="338" rx="20" fill="#f7faff" stroke="rgba(47, 104, 255, 0.10)"/>' +
        '<text x="46" y="56" font-size="18" font-weight="700" fill="#111319">' + escapeHtml(diagram.title || "Line graph") + "</text>" +
        '<line x1="' + left + '" y1="' + top + '" x2="' + left + '" y2="' + (height - bottom) + '" stroke="#111319" stroke-width="3"/>' +
        '<line x1="' + left + '" y1="' + (height - bottom) + '" x2="' + (width - right) + '" y2="' + (height - bottom) + '" stroke="#111319" stroke-width="3"/>' +
        yLabels.join("") +
        xLabels +
        '<polyline points="' + polyline + '" fill="none" stroke="#111319" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>' +
      "</svg>"
    );
  }

  function renderDiagram(diagram) {
    if (!diagram) return "";
    if (diagram.type === "line-graph") {
      return graphDiagramMarkup(diagram);
    }
    return "";
  }

  function parseImportedContext() {
    var params = new URLSearchParams(window.location.search);
    var title = params.get("title");
    var subject = params.get("subject");
    if (!title || !subject) {
      return null;
    }

    return {
      title: title,
      subject: subject,
      level: params.get("level") || "",
      board: params.get("board") || "",
      kind: params.get("kind") || "paper",
      route: params.get("route") || ""
    };
  }

  var blueprintMap = {
    mathematics: [
      {
        id: "maths-linear-equation",
        topic: "Algebra",
        generate: function () {
          var x = randomInt(3, 12);
          var a = randomInt(2, 6);
          var b = randomInt(3, 15);
          var c = a * x + b;
          return {
            prompt: "Solve for x: " + a + "x + " + b + " = " + c + ".",
            answer: "x = " + x,
            workedSolution: [
              "Subtract " + b + " from both sides to leave " + a + "x = " + (c - b) + ".",
              "Divide both sides by " + a + ".",
              "So x = " + x + "."
            ],
            marks: 3
          };
        }
      },
      {
        id: "maths-ratio-sharing",
        topic: "Ratios",
        generate: function () {
          var left = randomInt(2, 5);
          var right = randomInt(3, 7);
          var multiplier = randomInt(4, 8);
          var total = (left + right) * multiplier;
          return {
            prompt: "A teacher has " + total + " pencils. She wants to distribute them between two students, Alice and Ben, in a ratio of " + left + ":" + right + ". How many pencils does each student receive?",
            answer: "Alice receives " + (left * multiplier) + " pencils and Ben receives " + (right * multiplier) + " pencils.",
            workedSolution: [
              "Add the ratio parts: " + left + " + " + right + " = " + (left + right) + ".",
              "One part is " + total + " ÷ " + (left + right) + " = " + multiplier + ".",
              "Alice gets " + left + " parts, so " + left + " × " + multiplier + " = " + (left * multiplier) + ".",
              "Ben gets " + right + " parts, so " + right + " × " + multiplier + " = " + (right * multiplier) + "."
            ],
            marks: 4
          };
        }
      },
      {
        id: "maths-sale-price",
        topic: "Percentages",
        generate: function () {
          var original = choose([40, 60, 80, 100, 120]);
          var discount = choose([10, 15, 20, 25, 30]);
          var saving = original * (discount / 100);
          var salePrice = original - saving;
          return {
            prompt: "A pair of shoes costs £" + original + ". If there is a " + discount + "% discount, what is the sale price of the shoes?",
            answer: "£" + salePrice,
            workedSolution: [
              "Find the discount amount: " + discount + "% of £" + original + " = £" + saving + ".",
              "Subtract the discount from the original price: £" + original + " - £" + saving + ".",
              "The sale price is £" + salePrice + "."
            ],
            marks: 3
          };
        }
      },
      {
        id: "maths-line-graph",
        topic: "Graphs",
        generate: function () {
          var monthOne = randomInt(10, 12);
          var monthTwo = monthOne + randomInt(-1, 1);
          var monthThree = monthTwo + randomInt(2, 4);
          var monthFour = monthThree + randomInt(0, 2);
          var monthFive = monthFour + randomInt(-1, 1);
          var monthSix = monthFive + randomInt(2, 4);
          var values = [monthOne, monthTwo, monthThree, monthFour, monthFive, monthSix];
          var increase = monthThree - monthTwo;
          return {
            prompt: "The line graph shows how many books a student read over 6 months. How many books were read in month 6, and how many more books were read in month 3 than in month 2?",
            answer: "Month 6: " + monthSix + " books. Increase from month 2 to month 3: " + increase + " books.",
            workedSolution: [
              "Read the value at month 6 on the graph. The point is at " + monthSix + " books.",
              "Read the values at months 2 and 3: month 2 is " + monthTwo + " and month 3 is " + monthThree + ".",
              "Find the increase: " + monthThree + " - " + monthTwo + " = " + increase + "."
            ],
            marks: 6,
            diagram: createLineGraphDiagram("Number of Books Read", values)
          };
        }
      }
    ],
    physics: [
      {
        id: "physics-speed",
        topic: "Speed",
        generate: function () {
          var speed = randomInt(8, 20);
          var time = randomInt(5, 12);
          var distance = speed * time;
          return {
            prompt: "A cyclist travels " + distance + " metres in " + time + " seconds. Work out the cyclist's speed in m/s.",
            answer: speed + " m/s",
            workedSolution: [
              "Use speed = distance ÷ time.",
              distance + " ÷ " + time + " = " + speed + ".",
              "So the cyclist's speed is " + speed + " m/s."
            ],
            marks: 3
          };
        }
      },
      {
        id: "physics-density",
        topic: "Density",
        generate: function () {
          var density = randomInt(2, 9);
          var volume = randomInt(3, 10);
          var mass = density * volume;
          var material = choose(materials);
          return {
            prompt: "A block of " + material + " has a mass of " + mass + " g and a volume of " + volume + " cm^3. Find its density.",
            answer: density + " g/cm^3",
            workedSolution: [
              "Use density = mass ÷ volume.",
              mass + " ÷ " + volume + " = " + density + ".",
              "So the density is " + density + " g/cm^3."
            ],
            marks: 3
          };
        }
      }
    ],
    chemistry: [
      {
        id: "chemistry-moles",
        topic: "Moles",
        generate: function () {
          var mass = randomInt(12, 40);
          var mr = choose([12, 20, 24, 28, 40]);
          var moles = Number((mass / mr).toFixed(2));
          return {
            prompt: "A sample has a mass of " + mass + " g and a relative formula mass of " + mr + ". Work out the number of moles.",
            answer: moles + " mol",
            workedSolution: [
              "Use moles = mass ÷ relative formula mass.",
              mass + " ÷ " + mr + " = " + moles + ".",
              "So the amount of substance is " + moles + " mol."
            ],
            marks: 3
          };
        }
      },
      {
        id: "chemistry-formula-mass",
        topic: "Formula Mass",
        generate: function () {
          var carbonCount = randomInt(1, 4);
          var hydrogenCount = randomInt(2, 10);
          var oxygenCount = randomInt(1, 4);
          var total = carbonCount * 12 + hydrogenCount + oxygenCount * 16;
          return {
            prompt: "Find the relative formula mass of C" + carbonCount + "H" + hydrogenCount + "O" + oxygenCount + ". Use C = 12, H = 1 and O = 16.",
            answer: String(total),
            workedSolution: [
              carbonCount + " × 12 = " + (carbonCount * 12),
              hydrogenCount + " × 1 = " + hydrogenCount,
              oxygenCount + " × 16 = " + (oxygenCount * 16),
              "Add them: " + (carbonCount * 12) + " + " + hydrogenCount + " + " + (oxygenCount * 16) + " = " + total + "."
            ],
            marks: 4
          };
        }
      }
    ],
    biology: [
      {
        id: "biology-osmosis",
        topic: "Osmosis",
        generate: function () {
          var student = choose(names);
          var liquid = choose(["pure water", "a concentrated sugar solution"]);
          return {
            prompt: student + " places potato pieces into " + liquid + ". Explain what happens to the potato cells and why.",
            answer: "Water moves across the partially permeable cell membrane by osmosis. In a dilute solution water enters the cells, and in a concentrated solution water leaves the cells.",
            workedSolution: [
              "State that water moves by osmosis through a partially permeable membrane.",
              "Compare the concentration inside and outside the cells.",
              "Explain whether water moves in or out and link that to the potato becoming firmer or softer."
            ],
            marks: 4
          };
        }
      },
      {
        id: "biology-enzyme-graph",
        topic: "Enzymes",
        generate: function () {
          var temperature = choose([20, 30, 40, 50]);
          return {
            prompt: "A graph shows enzyme activity rising up to " + temperature + "°C and then falling sharply. Explain the pattern shown on the graph.",
            answer: "As temperature rises there are more successful collisions, so the rate increases. After the optimum temperature the enzyme denatures, so the rate falls quickly.",
            workedSolution: [
              "Explain the rise first: particles have more energy and collide more often.",
              "Name the optimum temperature where the rate is highest.",
              "Explain the fall: the enzyme changes shape and the active site no longer matches the substrate."
            ],
            marks: 4
          };
        }
      }
    ],
    english: [
      {
        id: "english-language-analysis",
        topic: "Language Analysis",
        generate: function () {
          var source = choose(texts);
          var adjective = choose(["restless", "silent", "fragile", "uneasy"]);
          return {
            prompt: "In " + source + ', the writer describes the atmosphere as "' + adjective + '". Explain how this word helps the reader understand the mood.',
            answer: "The word creates a clear feeling and shapes the mood straight away. A strong answer explains what the word makes the reader imagine or feel, then links that to the scene.",
            workedSolution: [
              "Pick out the word and say what it suggests.",
              "Explain the feeling or image it creates for the reader.",
              "Link that effect back to the mood of the whole scene."
            ],
            marks: 4
          };
        }
      },
      {
        id: "english-comparison",
        topic: "Comparison",
        generate: function () {
          var first = choose(["hopeful", "critical", "nervous"]);
          var second = choose(["optimistic", "angry", "uncertain"]);
          return {
            prompt: "Compare how Writer A and Writer B present their viewpoints if Writer A sounds " + first + " and Writer B sounds " + second + ".",
            answer: "A strong answer identifies the difference in tone, supports it with language choices, and explains how each writer wants the reader to react.",
            workedSolution: [
              "State the main difference in viewpoint.",
              "Use one language point for each writer.",
              "Explain the effect of each tone on the reader."
            ],
            marks: 4
          };
        }
      }
    ],
    history: [
      {
        id: "history-causation",
        topic: "Causation",
        generate: function () {
          var event = choose(["a protest growing quickly", "support for a ruler falling", "a reform movement becoming popular"]);
          return {
            prompt: "Write a short explanation of why " + event + ". Which cause would you say mattered most, and why?",
            answer: "A strong answer names one clear cause, explains how it led to the event, and justifies why it mattered more than other causes.",
            workedSolution: [
              "Name the factor you think mattered most.",
              "Explain how that factor changed people, decisions, or events.",
              "Compare it briefly with another factor to justify your judgement."
            ],
            marks: 6
          };
        }
      },
      {
        id: "history-interpretation",
        topic: "Interpretations",
        generate: function () {
          return {
            prompt: "A historian says a leader stayed popular because of strong public image. Explain one reason why this interpretation could be convincing.",
            answer: "A strong answer supports the interpretation with relevant knowledge, then explains how that evidence backs the historian's view.",
            workedSolution: [
              "Pick one detail that supports the interpretation.",
              "Explain what that detail shows.",
              "Link it clearly back to why the interpretation seems convincing."
            ],
            marks: 4
          };
        }
      }
    ],
    geography: [
      {
        id: "geography-fieldwork",
        topic: "Fieldwork",
        generate: function () {
          var river = choose(rivers);
          var town = choose(places);
          return {
            prompt: "A student is investigating traffic levels near " + river + " in " + town + ". Suggest one way to improve the reliability of the data collection.",
            answer: "A strong answer should suggest repeating the method, collecting data at more than one time, or increasing the sample size, then explain how that makes the results more trustworthy.",
            workedSolution: [
              "Suggest one practical change to the method.",
              "Explain how that change reduces bias or random error.",
              "Link the improvement to more reliable results."
            ],
            marks: 4
          };
        }
      },
      {
        id: "geography-development",
        topic: "Development",
        generate: function () {
          var place = choose(places);
          return {
            prompt: "Explain one reason why some areas around " + place + " may develop faster than others.",
            answer: "A strong answer chooses one factor, such as transport, investment, or jobs, and explains how it helps one area attract more growth than another.",
            workedSolution: [
              "Name the factor that gives one area an advantage.",
              "Explain how that factor improves growth or opportunity.",
              "Link it to why the gap between places can increase."
            ],
            marks: 4
          };
        }
      }
    ]
  };

  var importedContext = parseImportedContext();
  var importedSubject = importedContext && importedEngine
    ? importedEngine.normalizeSubject(importedContext.subject)
    : null;
  var state = {
    subject: importedSubject || localStorage.getItem("boostai-study-subject") || "mathematics",
    questions: {},
    importedContext: importedContext
  };

  var subjectList = document.getElementById("subject-list");
  var subjectHeroGrid = document.getElementById("subject-hero-grid");
  var questionList = document.getElementById("question-list");
  var status = document.getElementById("status");
  var workspaceTitle = document.getElementById("workspace-title");
  var workspaceDescription = document.getElementById("workspace-description");
  var downloadButton = document.getElementById("download-pdf");

  function getSubject(slug) {
    return subjects.find(function (subject) { return subject.slug === slug; });
  }

  function buildQuestion(subjectSlug, blueprint) {
    var generated = blueprint.generate();
    return {
      id: blueprint.id,
      subjectSlug: subjectSlug,
      topic: blueprint.topic,
      prompt: generated.prompt,
      simplifiedPrompt: simplifyPrompt(generated.prompt),
      answer: generated.answer,
      workedSolution: generated.workedSolution,
      marks: generated.marks || 4,
      diagram: generated.diagram || null,
      showSolution: false
    };
  }

  function buildQuestionsForSubject(subjectSlug) {
    return (blueprintMap[subjectSlug] || []).map(function (blueprint) {
      return buildQuestion(subjectSlug, blueprint);
    });
  }

  function buildImportedQuestions(context) {
    if (!importedEngine) {
      return [];
    }

    return importedEngine.buildBlueprints(context).map(function (blueprint) {
      return buildQuestion(importedEngine.normalizeSubject(context.subject), blueprint);
    });
  }

  function refreshActiveQuestions() {
    if (state.importedContext && importedEngine && state.subject === importedEngine.normalizeSubject(state.importedContext.subject)) {
      state.questions[state.subject] = buildImportedQuestions(state.importedContext);
      return;
    }

    state.questions[state.subject] = buildQuestionsForSubject(state.subject);
  }

  function setSubject(subjectSlug) {
    state.subject = subjectSlug;
    if (state.importedContext && importedEngine && subjectSlug !== importedEngine.normalizeSubject(state.importedContext.subject)) {
      state.importedContext = null;
    }
    refreshActiveQuestions();
    localStorage.setItem("boostai-study-subject", subjectSlug);
    render();
  }

  function regenerateQuestion(subjectSlug, questionId) {
    var list = state.questions[subjectSlug] || [];
    state.questions[subjectSlug] = list.map(function (question) {
      if (question.id !== questionId) return question;

      if (state.importedContext && importedEngine && subjectSlug === importedEngine.normalizeSubject(state.importedContext.subject)) {
        var importedBlueprint = importedEngine.buildBlueprints(state.importedContext).find(function (item) {
          return item.id === questionId;
        });
        return importedBlueprint ? buildQuestion(subjectSlug, importedBlueprint) : question;
      }

      var blueprint = (blueprintMap[subjectSlug] || []).find(function (item) {
        return item.id === questionId;
      });
      return blueprint ? buildQuestion(subjectSlug, blueprint) : question;
    });
    renderQuestions();
    status.textContent = "New similar question generated by AI.";
  }

  function toggleSolution(subjectSlug, questionId) {
    var list = state.questions[subjectSlug] || [];
    list.forEach(function (question) {
      if (question.id === questionId) {
        question.showSolution = !question.showSolution;
      }
    });
    renderQuestions();
    status.textContent = "Simple worked solution updated.";
  }

  function renderSubjectButtons() {
    var subjectMarkup = subjects.map(function (subject) {
      var active = subject.slug === state.subject ? " active" : "";
      return '<button type="button" class="subject-pill' + active + '" data-subject="' + subject.slug + '">' +
        '<span class="subject-icon">' + escapeHtml(subject.icon) + "</span>" +
        "<span>" + escapeHtml(subject.name) + "</span>" +
      "</button>";
    }).join("");

    subjectList.innerHTML = subjectMarkup;
    subjectHeroGrid.innerHTML = subjectMarkup;

    Array.prototype.slice.call(document.querySelectorAll("[data-subject]")).forEach(function (button) {
      button.addEventListener("click", function () {
        setSubject(button.getAttribute("data-subject"));
      });
    });
  }

  function renderQuestions() {
    var subject = getSubject(state.subject);
    var questions = state.questions[state.subject] || [];
    var isImportedMode = !!(state.importedContext && importedEngine && state.subject === importedEngine.normalizeSubject(state.importedContext.subject));

    if (isImportedMode) {
      workspaceTitle.textContent = state.importedContext.title;
      workspaceDescription.textContent = "Open generated practice for this imported " + state.importedContext.kind + " route. Each card can solve the question simply or generate a fresh similar version.";
    } else {
      workspaceTitle.textContent = subject.name + " study workspace";
      workspaceDescription.textContent = subject.description + " Use the controls on each question to reveal the simple solution or generate a fresh version with new values.";
    }

    questionList.innerHTML = questions.map(function (question, index) {
      return (
        '<article class="question">' +
          '<div class="question-head">' +
            '<div class="question-number">' + (index + 1) + "</div>" +
            '<div class="question-tools">' +
              '<button type="button" class="question-action question-action-outline" data-generate="' + question.id + '">' +
                '<span>↺</span><span>Generate similar</span>' +
              "</button>" +
              '<button type="button" class="question-action question-action-solid" data-solve="' + question.id + '">' +
                "<span>⚡</span><span>" + (question.showSolution ? "Hide solution" : "Solve") + "</span>" +
              "</button>" +
            "</div>" +
          "</div>" +
          '<div class="question-content">' +
            '<p class="question-title">' + escapeHtml((subject ? subject.name : question.subjectSlug) + " • " + question.topic) + "</p>" +
            (question.diagram ? '<div class="question-diagram">' + renderDiagram(question.diagram) + "</div>" : "") +
            '<p class="question-prompt">' + escapeHtml(question.prompt) + "</p>" +
            '<div class="answer-line-wrap"><div class="answer-line"></div></div>' +
            '<div class="question-solution' + (question.showSolution ? "" : " hidden") + '">' +
              "<h3>Simple solution</h3>" +
              '<ol class="solution-steps">' +
                question.workedSolution.map(function (step) {
                  return "<li>" + escapeHtml(step) + "</li>";
                }).join("") +
              "</ol>" +
              '<p class="solution-answer">Answer: ' + escapeHtml(question.answer) + "</p>" +
            "</div>" +
          "</div>" +
          '<div class="question-footer">(Total for Question ' + (index + 1) + " is " + question.marks + " " + markLabel(question.marks) + ")</div>" +
        "</article>"
      );
    }).join("");

    Array.prototype.slice.call(document.querySelectorAll("[data-generate]")).forEach(function (button) {
      button.addEventListener("click", function () {
        regenerateQuestion(state.subject, button.getAttribute("data-generate"));
      });
    });

    Array.prototype.slice.call(document.querySelectorAll("[data-solve]")).forEach(function (button) {
      button.addEventListener("click", function () {
        toggleSolution(state.subject, button.getAttribute("data-solve"));
      });
    });
  }

  function render() {
    if (!state.questions[state.subject]) {
      refreshActiveQuestions();
    }
    renderSubjectButtons();
    renderQuestions();

    if (state.importedContext && importedEngine && state.subject === importedEngine.normalizeSubject(state.importedContext.subject)) {
      status.textContent = "Showing BoostAI practice for imported route: " + state.importedContext.title + ".";
    } else {
      status.textContent = "Choose a question below and use Solve or Generate similar.";
    }
  }

  if (downloadButton) {
    downloadButton.addEventListener("click", function () {
      window.print();
    });
  }

  render();
}());
