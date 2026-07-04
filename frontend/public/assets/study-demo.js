(function () {
  var importedEngine = window.BoostAIImportedEngine;
  var subjects = [
    {
      slug: "mathematics",
      name: "Mathematics",
      icon: "📐",
      description: "Algebra, ratios, graphs, and exam-style numerical reasoning.",
      topics: ["Algebra", "Geometry", "Ratios"]
    },
    {
      slug: "physics",
      name: "Physics",
      icon: "⚡",
      description: "Motion, energy, circuits, and clear step-by-step calculations.",
      topics: ["Speed", "Forces", "Electricity"]
    },
    {
      slug: "chemistry",
      name: "Chemistry",
      icon: "⚗️",
      description: "Moles, formulas, bonding, and reaction calculations.",
      topics: ["Moles", "Formula Mass", "Rates"]
    },
    {
      slug: "biology",
      name: "Biology",
      icon: "🧬",
      description: "Processes, data interpretation, and simple science explanations.",
      topics: ["Cells", "Osmosis", "Enzymes"]
    },
    {
      slug: "english",
      name: "English",
      icon: "📝",
      description: "Readable literature analysis and clear writing prompts.",
      topics: ["Language Analysis", "Structure", "Comparison"]
    },
    {
      slug: "history",
      name: "History",
      icon: "🏛️",
      description: "Cause, consequence, interpretation, and evidence-based answers.",
      topics: ["Causation", "Interpretations", "Change and Continuity"]
    },
    {
      slug: "geography",
      name: "Geography",
      icon: "🌍",
      description: "Fieldwork, data analysis, ecosystems, and human geography.",
      topics: ["Fieldwork", "Coasts", "Development"]
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
        title: "Solve a linear equation",
        topic: "Algebra",
        format: "numeric",
        difficulty: "standard",
        generate: function () {
          var x = randomInt(3, 12);
          var a = randomInt(2, 6);
          var b = randomInt(3, 15);
          var c = a * x + b;
          return {
            prompt: "Work out x: " + a + "x + " + b + " = " + c + ".",
            answer: "x = " + x,
            workedSolution: [
              "Subtract " + b + " from both sides: " + a + "x = " + (c - b) + ".",
              "Divide both sides by " + a + ": x = " + ((c - b) / a) + "."
            ]
          };
        }
      },
      {
        id: "maths-ratio-sharing",
        title: "Share in a ratio",
        topic: "Ratios",
        format: "numeric",
        difficulty: "standard",
        generate: function () {
          var left = randomInt(2, 5);
          var right = randomInt(3, 7);
          var multiplier = randomInt(8, 14);
          var total = (left + right) * multiplier;
          return {
            prompt: "A prize of £" + total + " is shared in the ratio " + left + ":" + right + ". How much does the second person get?",
            answer: "£" + (right * multiplier),
            workedSolution: [
              "Add the ratio parts: " + left + " + " + right + " = " + (left + right) + ".",
              "One part is £" + total + " ÷ " + (left + right) + " = £" + multiplier + ".",
              "The second person gets " + right + " parts, so " + right + " × £" + multiplier + " = £" + (right * multiplier) + "."
            ]
          };
        }
      }
    ],
    physics: [
      {
        id: "physics-speed",
        title: "Use the speed formula",
        topic: "Speed",
        format: "numeric",
        difficulty: "standard",
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
              "So the speed is " + speed + " m/s."
            ]
          };
        }
      },
      {
        id: "physics-density",
        title: "Calculate density",
        topic: "Forces",
        format: "numeric",
        difficulty: "stretch",
        generate: function () {
          var density = randomInt(2, 9);
          var volume = randomInt(3, 10);
          var mass = density * volume;
          var material = choose(materials);
          return {
            prompt: "A block of " + material + " has a mass of " + mass + " g and a volume of " + volume + " cm³. Find its density.",
            answer: density + " g/cm³",
            workedSolution: [
              "Use density = mass ÷ volume.",
              mass + " ÷ " + volume + " = " + density + ".",
              "So the density is " + density + " g/cm³."
            ]
          };
        }
      }
    ],
    chemistry: [
      {
        id: "chemistry-moles",
        title: "Find moles from mass",
        topic: "Moles",
        format: "numeric",
        difficulty: "standard",
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
            ]
          };
        }
      },
      {
        id: "chemistry-formula-mass",
        title: "Calculate relative formula mass",
        topic: "Formula Mass",
        format: "numeric",
        difficulty: "foundation",
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
            ]
          };
        }
      }
    ],
    biology: [
      {
        id: "biology-osmosis",
        title: "Explain osmosis simply",
        topic: "Osmosis",
        format: "wordy",
        difficulty: "standard",
        generate: function () {
          var student = choose(names);
          var liquid = choose(["pure water", "a concentrated sugar solution"]);
          return {
            prompt: student + " places potato pieces into " + liquid + ". Explain what happens to the potato cells and why.",
            answer: "Water moves across the partially permeable cell membrane by osmosis. If the solution outside is more dilute, water moves into the cells and they become firmer. If the solution outside is more concentrated, water leaves the cells and they become less firm.",
            workedSolution: [
              "Mention osmosis: water moves through a partially permeable membrane.",
              "Compare the concentration inside and outside the cell.",
              "Say whether water moves into the cell or out of it and link that to the potato becoming firmer or softer."
            ]
          };
        }
      },
      {
        id: "biology-enzyme-graph",
        title: "Interpret enzyme data",
        topic: "Enzymes",
        format: "wordy",
        difficulty: "stretch",
        generate: function () {
          var temperature = choose([20, 30, 40, 50]);
          return {
            prompt: "A graph shows enzyme activity rising up to " + temperature + "°C and then falling sharply. Explain the pattern shown on the graph.",
            answer: "As temperature rises, particles have more energy, so there are more successful collisions and the rate increases. After the optimum temperature, the enzyme changes shape. The active site no longer fits the substrate well, so the rate falls quickly.",
            workedSolution: [
              "Explain the increase first: particles move faster and collide more often.",
              "Name the optimum temperature.",
              "Explain the drop: the enzyme is denatured and the active site changes shape."
            ]
          };
        }
      }
    ],
    english: [
      {
        id: "english-language-analysis",
        title: "Analyse language in a short extract",
        topic: "Language Analysis",
        format: "wordy",
        difficulty: "standard",
        generate: function () {
          var source = choose(texts);
          var adjective = choose(["restless", "silent", "fragile", "uneasy"]);
          return {
            prompt: "In " + source + ", the writer describes the atmosphere as \"" + adjective + "\". Explain how this word helps the reader understand the mood.",
            answer: "The word suggests a clear feeling and shapes the mood straight away. A strong answer should explain what the word makes the reader imagine or feel, then link that to the atmosphere of the scene.",
            workedSolution: [
              "Pick out the word and say what it suggests.",
              "Explain the feeling or image it creates for the reader.",
              "Link that effect back to the mood of the whole scene."
            ]
          };
        }
      },
      {
        id: "english-comparison",
        title: "Compare two viewpoints",
        topic: "Comparison",
        format: "wordy",
        difficulty: "stretch",
        generate: function () {
          var first = choose(["hopeful", "critical", "nervous"]);
          var second = choose(["optimistic", "angry", "uncertain"]);
          return {
            prompt: "Compare how Writer A and Writer B present their viewpoints if Writer A sounds " + first + " and Writer B sounds " + second + ".",
            answer: "A strong answer should identify the difference in tone, support it with language choices, and explain how each writer wants the reader to react.",
            workedSolution: [
              "State the main difference in viewpoint.",
              "Use a short quotation or language point for each writer.",
              "Explain the effect of each tone on the reader."
            ]
          };
        }
      }
    ],
    history: [
      {
        id: "history-causation",
        title: "Explain the main cause",
        topic: "Causation",
        format: "wordy",
        difficulty: "standard",
        generate: function () {
          var event = choose(["a protest growing quickly", "support for a ruler falling", "a reform movement becoming popular"]);
          return {
            prompt: "Write a short explanation of why " + event + ". Which cause would you say mattered most, and why?",
            answer: "A strong answer should name one clear cause, explain how it led to the event, and then justify why it mattered more than other causes. The key is using a chain of reasoning, not just listing factors.",
            workedSolution: [
              "Name the factor you think mattered most.",
              "Explain how that factor changed people, decisions, or events.",
              "Compare it briefly with another factor to justify your judgement."
            ]
          };
        }
      },
      {
        id: "history-interpretation",
        title: "Use an interpretation",
        topic: "Interpretations",
        format: "wordy",
        difficulty: "stretch",
        generate: function () {
          return {
            prompt: "A historian says a leader stayed popular because of strong public image. Explain one reason why this interpretation could be convincing.",
            answer: "A strong answer should support the interpretation with relevant knowledge, then explain how that evidence backs the historian's view.",
            workedSolution: [
              "Pick one detail that supports the interpretation.",
              "Explain what that detail shows.",
              "Link it clearly back to why the interpretation seems convincing."
            ]
          };
        }
      }
    ],
    geography: [
      {
        id: "geography-fieldwork",
        title: "Improve a fieldwork method",
        topic: "Fieldwork",
        format: "wordy",
        difficulty: "standard",
        generate: function () {
          var river = choose(rivers);
          var town = choose(places);
          return {
            prompt: "A student is investigating traffic levels near " + river + " in " + town + ". Suggest one way to improve the reliability of the data collection.",
            answer: "A strong answer should suggest repeating the method, collecting data at more than one time, or increasing the sample size. Then it should explain how that makes the results more trustworthy.",
            workedSolution: [
              "Suggest one practical change to the method.",
              "Explain how that change reduces bias or random error.",
              "Link the improvement to more reliable results."
            ]
          };
        }
      },
      {
        id: "geography-development",
        title: "Explain a development gap",
        topic: "Development",
        format: "wordy",
        difficulty: "stretch",
        generate: function () {
          var place = choose(places);
          return {
            prompt: "Explain one reason why some areas around " + place + " may develop faster than others.",
            answer: "A strong answer should choose one factor, such as transport, investment, or jobs, and explain how it helps one area attract more growth than another.",
            workedSolution: [
              "Name the factor that gives one area an advantage.",
              "Explain how that factor improves growth or opportunity.",
              "Link it to why the gap between places can increase."
            ]
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

  function getSubject(slug) {
    return subjects.find(function (subject) { return subject.slug === slug; });
  }

  function buildQuestion(subjectSlug, blueprint) {
    var generated = blueprint.generate();
    return {
      id: blueprint.id,
      subjectSlug: subjectSlug,
      title: blueprint.title,
      topic: blueprint.topic,
      difficulty: blueprint.difficulty,
      format: blueprint.format,
      prompt: generated.prompt,
      simplifiedPrompt: simplifyPrompt(generated.prompt),
      answer: generated.answer,
      workedSolution: generated.workedSolution
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
    var next = list.map(function (question) {
      if (question.id !== questionId) return question;

      if (state.importedContext && importedEngine && subjectSlug === importedEngine.normalizeSubject(state.importedContext.subject)) {
        var importedBlueprint = importedEngine.buildBlueprints(state.importedContext).find(function (item) {
          return item.id === questionId;
        });
        return importedBlueprint ? buildQuestion(subjectSlug, importedBlueprint) : question;
      }

      var blueprint = (blueprintMap[subjectSlug] || []).find(function (item) { return item.id === questionId; });
      return blueprint ? buildQuestion(subjectSlug, blueprint) : question;
    });
    state.questions[subjectSlug] = next;
    renderQuestions();
    status.textContent = "A new similar version was generated by changing the values or scenario while keeping the same skill.";
  }

  function simplifyQuestion(subjectSlug, questionId) {
    var list = state.questions[subjectSlug] || [];
    list.forEach(function (question) {
      if (question.id === questionId) {
        question.simplifiedPrompt = simplifyPrompt(question.prompt);
      }
    });
    renderQuestions();
    status.textContent = "That question was rewritten in simpler wording.";
  }

  function toggleAnswer(questionId) {
    var block = document.getElementById("answer-" + questionId);
    if (!block) return;
    block.classList.toggle("hidden");
  }

  function renderSubjectButtons() {
    var subjectMarkup = subjects.map(function (subject) {
      var active = subject.slug === state.subject ? " active" : "";
      return '<button type="button" class="subject-pill' + active + '" data-subject="' + subject.slug + '">' +
        '<span>' + subject.icon + '</span>' +
        '<span>' + subject.name + '</span>' +
      '</button>';
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
      workspaceDescription.textContent = "BoostAI is generating practice from the imported " + state.importedContext.kind + " route for " + importedEngine.describeContext(state.importedContext) + ". Use Generate similar to create fresh versions and Simplify wording to make prompts easier to read.";
    } else {
      workspaceTitle.textContent = subject.name + " study workspace";
      workspaceDescription.textContent = subject.description + " Use the controls on each question to simplify wording or generate a fresh practice version.";
    }

    questionList.innerHTML = questions.map(function (question) {
      var simpleSection = question.simplifiedPrompt === question.prompt ? " hidden" : "";
      return (
        '<article class="question">' +
          '<div class="question-top">' +
            '<div>' +
              '<div class="meta-row">' +
                '<span class="meta">' + (subject ? subject.name : question.subjectSlug) + '</span>' +
                '<span class="meta">' + question.topic + '</span>' +
                '<span class="meta">' + question.format + '</span>' +
              '</div>' +
              '<h3>' + question.title + '</h3>' +
            '</div>' +
            '<div class="actions">' +
              '<button type="button" class="btn" data-generate="' + question.id + '">Generate similar</button>' +
              '<button type="button" class="btn-soft" data-simplify="' + question.id + '">Simplify wording</button>' +
              '<button type="button" class="btn-ghost" data-answer-toggle="' + question.id + '">Show answer</button>' +
            '</div>' +
          '</div>' +
          '<div class="question-grid">' +
            '<div class="card">' +
              '<p class="card-title">Question</p>' +
              '<p class="prompt">' + question.prompt + '</p>' +
              '<div id="simple-' + question.id + '" class="simple' + simpleSection + '">' +
                '<p class="card-title">Simple version</p>' +
                '<p class="prompt">' + question.simplifiedPrompt + '</p>' +
              '</div>' +
            '</div>' +
            '<div id="answer-' + question.id + '" class="card answer-block hidden">' +
              '<p class="card-title">Answer</p>' +
              '<p class="answer-text">' + question.answer + '</p>' +
              '<p class="card-title">Worked steps</p>' +
              '<ul class="steps">' +
                question.workedSolution.map(function (step, index) {
                  return '<li><span class="step-index">' + (index + 1) + '</span><span>' + step + '</span></li>';
                }).join("") +
              '</ul>' +
            '</div>' +
          '</div>' +
        '</article>'
      );
    }).join("");

    Array.prototype.slice.call(document.querySelectorAll("[data-generate]")).forEach(function (button) {
      button.addEventListener("click", function () {
        regenerateQuestion(state.subject, button.getAttribute("data-generate"));
      });
    });

    Array.prototype.slice.call(document.querySelectorAll("[data-simplify]")).forEach(function (button) {
      button.addEventListener("click", function () {
        simplifyQuestion(state.subject, button.getAttribute("data-simplify"));
      });
    });

    Array.prototype.slice.call(document.querySelectorAll("[data-answer-toggle]")).forEach(function (button) {
      button.addEventListener("click", function () {
        var questionId = button.getAttribute("data-answer-toggle");
        toggleAnswer(questionId);
        var block = document.getElementById("answer-" + questionId);
        button.textContent = block && !block.classList.contains("hidden") ? "Hide answer" : "Show answer";
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
      status.textContent = "Showing original seeded content for " + (getSubject(state.subject) ? getSubject(state.subject).name : state.subject) + ".";
    }
  }

  render();
}());
