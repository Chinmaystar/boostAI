"use client";

import { useState } from "react";
import styles from "./boostai.module.css";
import { workspaceExamples } from "./site-data";

export function StudyWorkspace() {
  const [exampleIndex, setExampleIndex] = useState(0);
  const [variationIndex, setVariationIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);

  const current = workspaceExamples[exampleIndex];
  const currentVariant = current.variants[variationIndex];

  const switchExample = (index: number) => {
    setExampleIndex(index);
    setVariationIndex(0);
    setShowAnswer(false);
  };

  const cycleVariant = () => {
    setVariationIndex((value) => (value + 1) % current.variants.length);
    setShowAnswer(false);
  };

  return (
    <section className={styles.workspaceSection} id="workspace">
      <div className={styles.sectionHeading}>
        <span className={styles.eyebrow}>Built-in workspace</span>
        <h2>Preview the question flow directly on the main landing page</h2>
        <p>
          This source project ships with a lightweight interactive workspace so the
          homepage demonstrates the product instead of only describing it.
        </p>
      </div>

      <div className={styles.workspaceShell}>
        <div className={styles.workspaceTabs}>
          {workspaceExamples.map((example, index) => (
            <button
              key={example.id}
              className={`${styles.workspaceTab} ${
                index === exampleIndex ? styles.workspaceTabActive : ""
              }`}
              onClick={() => switchExample(index)}
              type="button"
            >
              <span>{example.subject}</span>
              <small>{example.level}</small>
            </button>
          ))}
        </div>

        <div className={styles.workspaceCard}>
          <div className={styles.workspaceMeta}>
            <div>
              <span className={styles.metaPill}>{current.marks}</span>
              <span className={styles.metaPillMuted}>{current.topic}</span>
            </div>
            <span className={styles.workspaceStatus}>BoostAI Active</span>
          </div>

          <p className={styles.workspacePrompt}>{current.prompt}</p>

          <div className={styles.workspaceActions}>
            <button
              className={styles.primaryButton}
              onClick={() => setShowAnswer(true)}
              type="button"
            >
              Show me how
            </button>
            <button
              className={styles.secondaryButton}
              onClick={cycleVariant}
              type="button"
            >
              Generate similar
            </button>
          </div>

          <div className={styles.workspaceGrid}>
            <div className={styles.workspacePanel}>
              <h3>Reasoning steps</h3>
              <ol className={styles.reasoningList}>
                {current.reasoning.map((step) => (
                  <li key={step}>{step}</li>
                ))}
              </ol>
            </div>

            <div className={styles.workspacePanel}>
              <h3>Fresh variation</h3>
              <p className={styles.workspaceVariant}>{currentVariant}</p>
              <div className={styles.answerBox}>
                <span>Answer</span>
                <strong>{showAnswer ? current.answer : "Tap “Show me how” to reveal it."}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

