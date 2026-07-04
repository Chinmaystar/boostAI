(function () {
  var host = document.getElementById("boostai-imported-ai");
  var contextNode = document.getElementById("boostai-imported-context");
  var engine = window.BoostAIImportedEngine;

  if (!host || !contextNode || !engine) {
    return;
  }

  var context = JSON.parse(contextNode.textContent);
  var blueprints = engine.buildBlueprints(context);
  var state = {
    questions: blueprints.map(buildQuestion)
  };

  function buildQuestion(blueprint) {
    var generated = blueprint.generate();
    return {
      id: blueprint.id,
      title: blueprint.title,
      topic: blueprint.topic,
      format: blueprint.format,
      difficulty: blueprint.difficulty,
      prompt: generated.prompt,
      simplifiedPrompt: engine.simplifyPrompt(generated.prompt),
      answer: generated.answer,
      workedSolution: generated.workedSolution
    };
  }

  function regenerate(questionId) {
    state.questions = state.questions.map(function (question, index) {
      var blueprint = blueprints[index];
      if (question.id !== questionId || !blueprint) return question;
      return buildQuestion(blueprint);
    });
    render();
  }

  function simplify(questionId) {
    state.questions.forEach(function (question) {
      if (question.id === questionId) {
        question.simplifiedPrompt = engine.simplifyPrompt(question.prompt);
      }
    });
    render();
  }

  function render() {
    host.innerHTML =
      '<div class="question-stack">' +
      state.questions.map(function (question) {
        var simpleHidden = question.simplifiedPrompt === question.prompt ? " hidden" : "";
        return (
          '<article class="card">' +
            '<div class="chip-row" style="margin:0 0 14px;">' +
              '<span class="chip">' + engine.displaySubject(context.subject) + '</span>' +
              '<span class="chip">' + question.topic + '</span>' +
              '<span class="chip">' + question.format + '</span>' +
            '</div>' +
            '<h2 style="margin-bottom:10px;">' + question.title + '</h2>' +
            '<p class="prompt">' + question.prompt + '</p>' +
            '<div id="simple-' + question.id + '" class="simple' + simpleHidden + '">' +
              '<p class="helper" style="margin-top:14px;">Simple version</p>' +
              '<p class="prompt">' + question.simplifiedPrompt + '</p>' +
            '</div>' +
            '<div class="action-row">' +
              '<button type="button" class="btn" data-generate="' + question.id + '">Generate similar</button>' +
              '<button type="button" class="btn-soft" data-simplify="' + question.id + '">Simplify wording</button>' +
              '<button type="button" class="btn-ghost" data-toggle="' + question.id + '">Show answer</button>' +
            '</div>' +
            '<div id="answer-' + question.id + '" class="answer-block hidden">' +
              '<p class="helper" style="margin-top:16px;">Answer</p>' +
              '<p class="prompt"><strong>' + question.answer + '</strong></p>' +
              '<ul class="steps">' +
                question.workedSolution.map(function (step) {
                  return '<li>' + step + '</li>';
                }).join("") +
              '</ul>' +
            '</div>' +
          '</article>'
        );
      }).join("") +
      '</div>' +
      '<div class="action-row">' +
        '<a class="btn" href="' + context.studyHref + '">Open full study workspace</a>' +
      '</div>';

    Array.prototype.slice.call(host.querySelectorAll("[data-generate]")).forEach(function (button) {
      button.addEventListener("click", function () {
        regenerate(button.getAttribute("data-generate"));
      });
    });

    Array.prototype.slice.call(host.querySelectorAll("[data-simplify]")).forEach(function (button) {
      button.addEventListener("click", function () {
        simplify(button.getAttribute("data-simplify"));
      });
    });

    Array.prototype.slice.call(host.querySelectorAll("[data-toggle]")).forEach(function (button) {
      button.addEventListener("click", function () {
        var questionId = button.getAttribute("data-toggle");
        var answer = document.getElementById("answer-" + questionId);
        if (!answer) return;
        answer.classList.toggle("hidden");
        button.textContent = answer.classList.contains("hidden") ? "Show answer" : "Hide answer";
      });
    });
  }

  render();
}());
