import Image from "next/image";
import Link from "next/link";
import styles from "./boostai.module.css";
import { routeCards } from "./site-data";
import { StudyWorkspace } from "./StudyWorkspace";

export function HomeLanding() {
  return (
    <main className={styles.page}>
      <div className={styles.orbA} />
      <div className={styles.orbB} />
      <div className={styles.orbC} />

      <header className={styles.topbar}>
        <div className={styles.topbarInner}>
          <Link className={styles.brand} href="/" prefetch={false}>
            <Image
              src="/boostai/images/logo.webp"
              alt="BoostAI logo"
              width={54}
              height={36}
              sizes="54px"
            />
            <span className={styles.brandName}>
              Boost<span>AI</span>
            </span>
          </Link>

          <nav className={styles.nav}>
            <a href="#routes">Choose route</a>
            <a href="#workspace">Workspace</a>
            <Link href="/school" prefetch={false}>School</Link>
            <Link href="/uni" prefetch={false}>Uni</Link>
            <a href="/login.html?mode=login&returnTo=%2F">Login</a>
            <a href="#join" className={styles.navCta}>
              Get source-ready
            </a>
          </nav>
        </div>
      </header>

      <section className={styles.shell}>
        <div className={styles.hero}>
          <div className={styles.heroCopy}>
            <span className={styles.eyebrow}>Three-page React source</span>
            <h1>
              Where are you studying <span>right now?</span>
            </h1>
            <p>
              This homepage acts as the route chooser for BoostAI Study and includes
              a live question workspace preview so visitors can understand the product
              before they commit to school or university mode.
            </p>
            <div className={styles.heroActions}>
              <Link className={styles.primaryButton} href="/school" prefetch={false}>
                Go to school route
              </Link>
              <Link className={styles.secondaryButton} href="/uni" prefetch={false}>
                Go to university route
              </Link>
            </div>
          </div>

          <div className={styles.heroMediaWrap}>
            <Image
              className={styles.heroMedia}
              src="/boostai/images/hero-demo-image.webp"
              alt="BoostAI landing page preview"
              width={720}
              height={590}
              priority
              sizes="(max-width: 1080px) 100vw, 46vw"
            />
          </div>
        </div>

        <section className={styles.routeSection} id="routes">
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>Entry routes</span>
            <h2>Two focused paths, one shared product language</h2>
            <p>
              The homepage mirrors the live site intent: help visitors self-select the
              version of BoostAI that matches their study context.
            </p>
          </div>

          <div className={styles.routeGrid}>
            {routeCards.map((card) => (
              <Link
                key={card.href}
                className={`${styles.routeCard} ${
                  card.accent === "school" ? styles.routeCardSchool : styles.routeCardUni
                }`}
                href={card.href}
                prefetch={false}
              >
                <div className={styles.routeCardTop} />
                <div className={styles.routeCardBody}>
                  <span className={styles.routeLabel}>{card.label}</span>
                  <h3>{card.title}</h3>
                  <p>{card.description}</p>

                  <div className={styles.tagRow}>
                    {card.tags.map((tag) => (
                      <span key={tag} className={styles.tag}>
                        {tag}
                      </span>
                    ))}
                  </div>

                  <div className={styles.routePreview}>
                    <Image
                      src={card.image}
                      alt={`${card.label} preview`}
                      width={655}
                      height={381}
                      sizes="(max-width: 1080px) 100vw, 31vw"
                    />
                  </div>

                  <span className={styles.routeCta}>{card.cta}</span>
                </div>
              </Link>
            ))}
          </div>
        </section>

        <StudyWorkspace />

        <section className={styles.summaryGrid} id="join">
          <article className={styles.summaryCard}>
            <h3>Clean handoff for development</h3>
            <p>
              The project is built as editable Next.js source code rather than a static
              export bundle, so a client team can develop on top of it immediately.
            </p>
          </article>
          <article className={styles.summaryCard}>
            <h3>Reusable components</h3>
            <p>
              Shared layout, route cards, CTA styles, and section blocks keep the three
              pages consistent without duplicating code.
            </p>
          </article>
          <article className={styles.summaryCard}>
            <h3>Local assets included</h3>
            <p>
              Fonts, logo, and preview imagery live in the project&apos;s `public`
              folder, so the landing pages work without depending on third-party CDNs.
            </p>
          </article>
        </section>
      </section>
    </main>
  );
}
