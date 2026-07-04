"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import styles from "./dashboard.module.css";

type SessionState = {
  email: string;
  name: string;
  returnTo: string;
};

type NavItem = {
  label: string;
  icon: string;
  active?: boolean;
  meta?: string;
};

type NavSection = {
  title: string;
  items: NavItem[];
};

const defaultSession: SessionState = {
  email: "anon@boostai.study",
  name: "Anon",
  returnTo: "/"
};

const navSections: NavSection[] = [
  {
    title: "Workspace",
    items: [
      { label: "Home", icon: "⌂", active: true },
      { label: "Revision Planner", icon: "↺", meta: "New" },
      { label: "Ask BoostAI", icon: "✦", meta: "Beta" }
    ]
  },
  {
    title: "Resources",
    items: [
      { label: "Question Bank", icon: "◫" },
      { label: "Lessons", icon: "▶" },
      { label: "Revision Guides", icon: "▣" },
      { label: "Flashcards", icon: "☰" },
      { label: "Past Papers", icon: "≡" }
    ]
  },
  {
    title: "Tools",
    items: [
      { label: "Mock Exam Builder", icon: "✎" },
      { label: "Essay Marker", icon: "⌁" },
      { label: "Predicted Grade", icon: "◎" },
      { label: "Settings", icon: "⚙" }
    ]
  }
];

const questItems = [
  "Try the Question Bank",
  "Open the revision guides",
  "Complete a lesson",
  "Build a mock exam",
  "Make a revision plan",
  "Ask BoostAI a question",
  "Mark an essay"
];

const paperCards = [
  {
    title: "GCSE Maths · November 2024\nPaper 1 · Non-Calculator · Foundation"
  },
  {
    title: "GCSE Maths · November 2024\nPaper 1 · Non-Calculator · Higher"
  }
];

function nameFromEmail(email: string) {
  const local = email.split("@")[0] || "anon";
  return local
    .replace(/[._-]+/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function timeGreeting() {
  const hour = new Date().getHours();

  if (hour < 5) return "Good late night";
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export function StudyDashboard() {
  const [session, setSession] = useState<SessionState>(defaultSession);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem("boostai-local-session");
      if (!raw) return;

      const parsed = JSON.parse(raw) as Partial<SessionState>;
      const email = parsed.email?.trim() || defaultSession.email;
      const name = parsed.name?.trim() || nameFromEmail(email) || defaultSession.name;
      const returnTo = parsed.returnTo?.trim() || defaultSession.returnTo;

      setSession({ email, name, returnTo });
    } catch {
      setSession(defaultSession);
    }
  }, []);

  return (
    <main className={styles.page}>
      <div className={styles.layout}>
        <aside className={styles.sidebar}>
          <Link className={styles.brand} href="/">
            <Image
              className={styles.brandMark}
              src="/logo.webp"
              alt="BoostAI logo"
              width={44}
              height={44}
              priority
            />
            <span className={styles.brandWord}>
              Boost<span>AI</span>
            </span>
          </Link>

          {navSections.map((section) => (
            <div className={styles.navGroup} key={section.title}>
              <span className={styles.groupTitle}>{section.title}</span>
              {section.items.map((item) => (
                <div
                  className={item.active ? styles.navItemActive : styles.navItem}
                  key={item.label}
                >
                  <span className={styles.navIcon}>{item.icon}</span>
                  <span>{item.label}</span>
                  {item.meta ? <span className={styles.navMeta}>{item.meta}</span> : null}
                </div>
              ))}
            </div>
          ))}

          <div className={styles.supportCard}>
            <strong>Preview mode is on</strong>
            <p>
              This dashboard is wired for demo access right now, so you can keep
              showing the product flow before real auth is finalised.
            </p>
          </div>
        </aside>

        <section className={styles.content}>
          <div className={styles.mobileTop}>
            <Link className={styles.brand} href="/">
              <Image
                className={styles.brandMark}
                src="/logo.webp"
                alt="BoostAI logo"
                width={40}
                height={40}
              />
              <span className={styles.brandWord}>
                Boost<span>AI</span>
              </span>
            </Link>
            <span className={styles.avatar}>{session.name.charAt(0).toUpperCase()}</span>
          </div>

          <div className={styles.topbar}>
            <div className={styles.searchRow}>
              <div className={styles.search}>Search topics, papers, or prompts…</div>
              <div className={styles.coursePicker}>
                <span>Find your course…</span>
                <span>⌄</span>
              </div>
            </div>

            <div className={styles.topActions}>
              <div className={styles.energyPill}>
                <span>⚡ ∞</span>
                <span className={styles.energyStatus}>Preview active</span>
              </div>
              <div className={styles.streakPill}>⚡ 14 / 15</div>
              <div className={styles.avatar}>{session.name.charAt(0).toUpperCase()}</div>
            </div>
          </div>

          <div className={styles.grid}>
            <div className={styles.mainColumn}>
              <section className={styles.heroPanel}>
                <span className={styles.eyebrow}>BoostAI Workspace</span>
                <h1>
                  {timeGreeting()}, <span>{session.name}</span>
                </h1>
                <p>
                  Your preview account is live. Start with a revision plan, open a
                  question bank, or jump back to the landing flow whenever you need.
                </p>
                <div className={styles.heroActions}>
                  <a className={styles.primaryCta} href="#">
                    Create my revision plan →
                  </a>
                  <a className={styles.secondaryCta} href={session.returnTo || "/"}>
                    Back to landing page
                  </a>
                </div>
              </section>

              <section className={styles.progressPanel}>
                <div className={styles.progressHeader}>
                  <div>
                    <h3>Momentum for this week</h3>
                    <p>
                      We’re keeping the dashboard lightweight for now, but the structure
                      is ready for real user progress later.
                    </p>
                  </div>
                  <div className={styles.progressBadge}>78%</div>
                </div>

                <div className={styles.progressGrid}>
                  <div className={styles.metric}>
                    <strong>12</strong>
                    <span>Questions solved</span>
                  </div>
                  <div className={styles.metric}>
                    <strong>4</strong>
                    <span>Topics revisited</span>
                  </div>
                  <div className={styles.metric}>
                    <strong>2h 18m</strong>
                    <span>Focused study time</span>
                  </div>
                </div>
              </section>

              <section>
                <div className={styles.sectionHeader}>
                  <div>
                    <h2>My subjects</h2>
                    <div className={styles.subtle}>Continue where your preview account left off.</div>
                  </div>
                  <a className={styles.addButton} href="#">
                    + Add subjects
                  </a>
                </div>

                <article className={styles.subjectCard}>
                  <div className={styles.subjectInner}>
                    <div className={styles.subjectCopy}>
                      <span>GCSE · Edexcel</span>
                      <h3>Maths</h3>
                      <p>
                        Step-by-step walkthroughs, similar-question generation, and
                        ready-to-open exam paper sets in the same BoostAI palette.
                      </p>
                      <a className={styles.subjectButton} href="#">
                        Open →
                      </a>
                    </div>

                    <div className={styles.subjectArt}>
                      <div className={styles.shapeOne} />
                      <div className={styles.shapeTwo} />
                      <div className={styles.shapeThree} />
                    </div>
                  </div>
                </article>
              </section>

              <section>
                <div className={styles.sectionHeader}>
                  <div>
                    <h2>Suggested past papers</h2>
                    <div className={styles.subtle}>Two starting points to make the workflow feel real.</div>
                  </div>
                </div>

                <div className={styles.paperGrid}>
                  {paperCards.map((card) => (
                    <article className={styles.paperCard} key={card.title}>
                      <div className={styles.paperTop}>
                        <h3>
                          {card.title.split("\n").map((line) => (
                            <span key={line}>
                              {line}
                              <br />
                            </span>
                          ))}
                        </h3>
                        <div className={styles.paperLinks}>
                          <span>
                            <span>Questions</span>
                            <span>›</span>
                          </span>
                          <span>
                            <span>Mark scheme</span>
                            <span>›</span>
                          </span>
                          <span>
                            <span>Solutions</span>
                            <span>›</span>
                          </span>
                        </div>
                      </div>
                      <div className={styles.paperFooter}>
                        <span>No attempts yet</span>
                        <a className={styles.logAttempt} href="#">
                          Log attempt
                        </a>
                      </div>
                    </article>
                  ))}
                </div>
              </section>
            </div>

            <aside className={styles.questPanel}>
              <h2>Quests</h2>
              <p>Use these starter actions to walk someone through the product after login.</p>
              <div className={styles.questList}>
                {questItems.map((item) => (
                  <div className={styles.questItem} key={item}>
                    <span className={styles.questCheck} />
                    <span>{item}</span>
                    <span className={styles.questReward}>+ ∞ ⚡</span>
                  </div>
                ))}
              </div>
            </aside>
          </div>
        </section>
      </div>
    </main>
  );
}
