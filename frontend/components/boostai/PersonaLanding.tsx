import Image from "next/image";
import Link from "next/link";
import styles from "./boostai.module.css";
import type { PersonaLandingData } from "./site-data";

type PersonaLandingProps = {
  page: PersonaLandingData;
};

export function PersonaLanding({ page }: PersonaLandingProps) {
  const sectionStyle = {
    ["--accent" as string]: page.palette.accent,
    ["--accent-strong" as string]: page.palette.accentStrong,
    ["--accent-soft" as string]: page.palette.accentSoft
  };

  return (
    <main className={styles.page} style={sectionStyle}>
      <div className={styles.orbA} />
      <div className={styles.orbB} />

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
            <Link href="/" prefetch={false}>Home</Link>
            <a href="#features">Features</a>
            <a href="#flow">Workflow</a>
            <a href="#faq">FAQ</a>
            <a href="/login.html">Login</a>
            <a href="#cta" className={styles.navCta}>
              Open route
            </a>
          </nav>
        </div>
      </header>

      <section className={styles.shell}>
        <div className={styles.hero}>
          <div className={styles.heroCopy}>
            <span className={styles.eyebrow}>{page.eyebrow}</span>
            <h1>
              {page.title.replace(page.accentWord, "")}
              <span>{page.accentWord}</span>
            </h1>
            <p>{page.description}</p>
            <div className={styles.heroActions}>
              <a className={styles.primaryButton} href={page.primaryCta.href}>
                {page.primaryCta.label}
              </a>
              <Link
                className={styles.secondaryButton}
                href={page.secondaryCta.href}
                prefetch={false}
              >
                {page.secondaryCta.label}
              </Link>
            </div>
            <div className={styles.tagRow}>
              {page.stats.map((item) => (
                <span key={item} className={styles.tag}>
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className={styles.previewCard}>
            <Image
              src={page.image}
              alt={page.imageAlt}
              width={720}
              height={560}
              priority
              sizes="(max-width: 1080px) 100vw, 46vw"
            />
            <div className={styles.previewCaption}>
              <strong>Built for a fast first impression.</strong>
              <span>
                The route keeps the interface calm, visual, and ready to extend with
                real product logic later.
              </span>
            </div>
          </div>
        </div>

        <section className={styles.featureSection} id="features">
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>What this route emphasises</span>
            <h2>Designed around how this audience actually studies</h2>
            <p>
              Each landing page is distinct, but both still belong to the same BoostAI
              family and reuse the same front-end system.
            </p>
          </div>

          <div className={styles.featureGrid}>
            {page.featureCards.map((feature) => (
              <article key={feature.title} className={styles.featureCard}>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.flowSection} id="flow">
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>Workflow</span>
            <h2>A study flow that moves from input to momentum</h2>
          </div>

          <div className={styles.stepGrid}>
            {page.steps.map((step, index) => (
              <article key={step.title} className={styles.stepCard}>
                <span className={styles.stepNumber}>0{index + 1}</span>
                <h3>{step.title}</h3>
                <p>{step.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.proofStrip}>
          {page.proof.map((item) => (
            <article key={item.label} className={styles.proofCard}>
              <strong>{item.value}</strong>
              <span>{item.label}</span>
            </article>
          ))}
        </section>

        <section className={styles.workspaceHighlights}>
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>Workspace highlights</span>
            <h2>What the interface should signal at a glance</h2>
          </div>

          <div className={styles.highlightRow}>
            {page.workspaceHighlights.map((item) => (
              <div key={item} className={styles.highlightChip}>
                {item}
              </div>
            ))}
          </div>
        </section>

        <section className={styles.testimonialSection}>
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>Social proof</span>
            <h2>Copy blocks that help the page feel product-led, not generic</h2>
          </div>

          <div className={styles.testimonialGrid}>
            {page.testimonials.map((testimonial) => (
              <article key={testimonial.name} className={styles.testimonialCard}>
                <p>&ldquo;{testimonial.quote}&rdquo;</p>
                <strong>{testimonial.name}</strong>
                <span>{testimonial.role}</span>
              </article>
            ))}
          </div>
        </section>

        <section className={styles.faqSection} id="faq">
          <div className={styles.sectionHeading}>
            <span className={styles.eyebrow}>FAQ</span>
            <h2>Questions a client or dev team will actually ask</h2>
          </div>

          <div className={styles.faqList}>
            {page.faqs.map((faq) => (
              <details key={faq.question} className={styles.faqItem}>
                <summary>{faq.question}</summary>
                <p>{faq.answer}</p>
              </details>
            ))}
          </div>
        </section>

        <section className={styles.ctaSection} id="cta">
          <div>
            <span className={styles.eyebrow}>Final CTA</span>
            <h2>Ready for client handoff and front-end iteration</h2>
            <p>
              This route is already packaged as source code, so the next step is
              feature work rather than reverse-engineering a static export.
            </p>
          </div>
          <div className={styles.ctaActions}>
            <a className={styles.primaryButton} href={page.primaryCta.href}>
              {page.primaryCta.label}
            </a>
            <Link className={styles.secondaryButton} href="/" prefetch={false}>
              View all routes
            </Link>
          </div>
        </section>
      </section>
    </main>
  );
}
