export type WorkspaceExample = {
  id: string;
  subject: string;
  level: string;
  marks: string;
  topic: string;
  prompt: string;
  reasoning: string[];
  answer: string;
  variants: string[];
};

export const workspaceExamples: WorkspaceExample[] = [
  {
    id: "maths",
    subject: "Mathematics",
    level: "GCSE · Edexcel",
    marks: "4 marks",
    topic: "Quadratics",
    prompt: "Solve x^2 - 5x + 6 = 0 and explain why the factor method works.",
    reasoning: [
      "Find two numbers that multiply to +6 and add to -5.",
      "Rewrite the quadratic as (x - 2)(x - 3) = 0.",
      "Use the zero-product rule to show x = 2 or x = 3."
    ],
    answer: "x = 2 or x = 3",
    variants: [
      "Solve x^2 - 7x + 12 = 0.",
      "Solve x^2 - 9x + 20 = 0.",
      "Solve x^2 - 11x + 28 = 0."
    ]
  },
  {
    id: "physics",
    subject: "Physics",
    level: "A-Level · AQA",
    marks: "2 marks",
    topic: "Elastic potential energy",
    prompt:
      "A spring with spring constant 40 N/m is extended by 0.3 m. Calculate the elastic potential energy stored.",
    reasoning: [
      "Use E = 1/2 kx^2 for energy stored in a spring.",
      "Substitute k = 40 and x = 0.3 into the equation.",
      "Calculate 0.5 x 40 x 0.3^2 to get 1.8 J."
    ],
    answer: "1.8 J",
    variants: [
      "A 60 N/m spring stretches by 0.2 m. Find the elastic energy stored.",
      "A 25 N/m spring stretches by 0.4 m. Calculate the energy stored.",
      "A 50 N/m spring stretches by 0.15 m. What energy is stored?"
    ]
  },
  {
    id: "chemistry",
    subject: "Chemistry",
    level: "IB · Higher Level",
    marks: "3 marks",
    topic: "Moles and masses",
    prompt:
      "Calculate the number of moles in 9.8 g of sulfuric acid, H2SO4, and state the formula you used.",
    reasoning: [
      "Use the formula moles = mass / molar mass.",
      "Find the molar mass of H2SO4 as 98 g/mol.",
      "Compute 9.8 / 98 to get 0.10 mol."
    ],
    answer: "0.10 mol",
    variants: [
      "Find the moles in 18 g of water, H2O.",
      "Calculate the moles in 4.4 g of carbon dioxide, CO2.",
      "Find the moles in 29.25 g of sodium chloride, NaCl."
    ]
  }
];

export const routeCards = [
  {
    href: "/school",
    label: "School Student",
    title: "I'm at school",
    accent: "school",
    description:
      "Ace GCSE, A-Level, IGCSE, and IB questions with step-by-step AI explanations and unlimited practice variations.",
    tags: ["GCSE", "A-Level", "IGCSE", "IB"],
    image: "/boostai/images/school-demo.webp",
    cta: "Go to school website"
  },
  {
    href: "/uni",
    label: "University Student",
    title: "I'm at university",
    accent: "uni",
    description:
      "Turn dense lectures, readings, and past papers into revision prompts, worked answers, and next-step study plans.",
    tags: ["Undergraduate", "Postgraduate"],
    image: "/boostai/images/university-demo.webp",
    cta: "Go to university website"
  }
] as const;

export type PersonaLandingData = {
  slug: "school" | "uni";
  eyebrow: string;
  title: string;
  accentWord: string;
  description: string;
  image: string;
  imageAlt: string;
  primaryCta: {
    label: string;
    href: string;
  };
  secondaryCta: {
    label: string;
    href: string;
  };
  stats: string[];
  featureCards: Array<{
    title: string;
    description: string;
  }>;
  steps: Array<{
    title: string;
    description: string;
  }>;
  proof: Array<{
    value: string;
    label: string;
  }>;
  testimonials: Array<{
    name: string;
    role: string;
    quote: string;
  }>;
  faqs: Array<{
    question: string;
    answer: string;
  }>;
  workspaceHighlights: string[];
  palette: {
    accent: string;
    accentStrong: string;
    accentSoft: string;
  };
};

export const schoolLanding: PersonaLandingData = {
  slug: "school",
  eyebrow: "BoostAI School",
  title: "Solve and generate school questions at lightning speed",
  accentWord: "lightning speed",
  description:
    "Built for students who want clear method, fast repetition, and exam-style practice without waiting around for a heavy app to load.",
  image: "/boostai/images/school-demo.webp",
  imageAlt: "BoostAI School dashboard preview",
  primaryCta: {
    label: "Start with school mode",
    href: "#cta"
  },
  secondaryCta: {
    label: "Back to route chooser",
    href: "/"
  },
  stats: ["GCSE", "A-Level", "IGCSE", "IB"],
  featureCards: [
    {
      title: "Instant worked solutions",
      description:
        "Paste a question and see the reasoning, method, and final answer in a format students can actually learn from."
    },
    {
      title: "Unlimited similar questions",
      description:
        "Turn one exam prompt into a full practice set so revision becomes repetition with purpose instead of guesswork."
    },
    {
      title: "Exam-board context",
      description:
        "Keep the flow anchored to the wording and structure students expect from real exam boards."
    },
    {
      title: "Feedback on weak spots",
      description:
        "Use guided feedback to spot where the method slipped and what needs practising next."
    }
  ],
  steps: [
    {
      title: "Paste the question",
      description:
        "Start from a worksheet, screenshot, or past-paper question and move straight into the workspace."
    },
    {
      title: "See the method clearly",
      description:
        "BoostAI breaks the solution into digestible steps instead of dropping a final answer without context."
    },
    {
      title: "Generate fresh practice",
      description:
        "Spin up new variations at the same difficulty so the skill sticks after the first attempt."
    },
    {
      title: "Lock in the topic",
      description:
        "Keep drilling until the pattern feels automatic and revision turns into confidence."
    }
  ],
  proof: [
    { value: "4", label: "exam pathways supported on the landing page" },
    { value: "3", label: "core STEM subjects showcased in the workspace" },
    { value: "1", label: "flow from question to practice to answer" }
  ],
  testimonials: [
    {
      name: "Maya",
      role: "Year 11 student",
      quote:
        "The best part is that it explains the method first, then gives me another question before I forget how it works."
    },
    {
      name: "Daniel",
      role: "A-Level Physics student",
      quote:
        "I use it when I need five more versions of the same style of question, not another vague summary."
    },
    {
      name: "Sara",
      role: "Parent",
      quote:
        "Revision feels calmer because there is finally a clear next step instead of jumping between random resources."
    }
  ],
  faqs: [
    {
      question: "Is this only for maths?",
      answer:
        "No. The landing page presents maths, physics, and chemistry examples, while the source structure makes it easy to extend into more subjects."
    },
    {
      question: "Can I adapt it for a real login flow?",
      answer:
        "Yes. The CTA buttons are clean placeholders, so your development team can connect them to Supabase, Clerk, or another auth provider."
    },
    {
      question: "Does the project include editable source code?",
      answer:
        "Yes. This deliverable is a full React and Next.js source project with reusable components, route files, styles, and local assets."
    }
  ],
  workspaceHighlights: [
    "Question-first workflow",
    "Method before answer",
    "New variations in one click"
  ],
  palette: {
    accent: "#2f68ff",
    accentStrong: "#2450d6",
    accentSoft: "rgba(47, 104, 255, 0.12)"
  }
};

export const universityLanding: PersonaLandingData = {
  slug: "uni",
  eyebrow: "BoostAI University",
  title: "Turn course materials into faster revision",
  accentWord: "faster revision",
  description:
    "Made for undergraduates and postgraduates who need to simplify dense material, generate practice from their own notes, and keep momentum across demanding modules.",
  image: "/boostai/images/university-demo.webp",
  imageAlt: "BoostAI University dashboard preview",
  primaryCta: {
    label: "Open university mode",
    href: "#cta"
  },
  secondaryCta: {
    label: "Back to route chooser",
    href: "/"
  },
  stats: ["Undergraduate", "Postgraduate", "Lecture notes", "Past papers"],
  featureCards: [
    {
      title: "Upload your own material",
      description:
        "Frame the product around lectures, readings, and past papers so the revision context stays personal and specific."
    },
    {
      title: "Generate practice from notes",
      description:
        "Convert content-heavy modules into focused questions, prompts, and short-answer checks."
    },
    {
      title: "AI feedback inside one workspace",
      description:
        "Keep the question, reasoning, answer, and next task in a single flow instead of scattered tools."
    },
    {
      title: "Plan the next study move",
      description:
        "Surface the follow-up concept, reading, or practice set that should come next while context is still fresh."
    }
  ],
  steps: [
    {
      title: "Drop in lectures or readings",
      description:
        "Start from the actual material your module uses rather than generic summaries built for someone else."
    },
    {
      title: "Ask BoostAI to unpack it",
      description:
        "Turn dense pages into clearer explanations, checkpoints, and revision prompts."
    },
    {
      title: "Create practice from your module",
      description:
        "Generate questions and model answers grounded in the source material you uploaded."
    },
    {
      title: "Revise with momentum",
      description:
        "Use the workspace to keep pushing from understanding into application instead of stopping at a summary."
    }
  ],
  proof: [
    { value: "2", label: "core university routes on the landing page" },
    { value: "1", label: "workspace for notes, questions, and feedback" },
    { value: "0", label: "need for a static export-only handoff" }
  ],
  testimonials: [
    {
      name: "Priya",
      role: "Biochemistry undergraduate",
      quote:
        "It helps me turn messy lecture slides into actual practice instead of just rereading the same PDF."
    },
    {
      name: "Noah",
      role: "Law postgraduate",
      quote:
        "The useful part is not that it is AI. It is that the next action is obvious once the explanation finishes."
    },
    {
      name: "Elena",
      role: "Economics student",
      quote:
        "I like that it can move from notes to application fast, which is usually the gap during revision season."
    }
  ],
  faqs: [
    {
      question: "Is this designed for only STEM modules?",
      answer:
        "No. The visuals are STEM-friendly, but the content architecture is generic enough for humanities, law, business, and social science modules too."
    },
    {
      question: "Can developers swap in real upload and auth logic later?",
      answer:
        "Yes. The current project keeps those flows as clean integration points so the front-end source remains easy to extend."
    },
    {
      question: "Does this include a university redirect path as well?",
      answer:
        "Yes. The project includes both /uni and a /university redirect so the public routing matches the existing site expectations."
    }
  ],
  workspaceHighlights: [
    "Lecture-note ingestion",
    "Practice generated from your material",
    "Feedback and next-step prompts"
  ],
  palette: {
    accent: "#7c5cfc",
    accentStrong: "#6437ff",
    accentSoft: "rgba(124, 92, 252, 0.12)"
  }
};

