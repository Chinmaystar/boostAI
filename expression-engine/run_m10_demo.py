"""Manual demo: run the full BoostAI deterministic pipeline on one equation."""

import json
from src.integration import (
    PipelineOrchestrator, PipelineConfig, QuestionSource, DiagramSpec,
)
from src.generator import GeneratorConfig
from src.diagram_engine import (
    DiagramTemplateBuilder, Point, Line, Polygon, SVGRenderer,
)

# ── 1. Create the orchestrator ──────────────────────────────────────────
config = PipelineConfig(
    generator_config=GeneratorConfig(
        random_seed=42,
        require_validation=False,
    ),
)
orch = PipelineOrchestrator(config)

# ── 2. Define the question ─────────────────────────────────────────────
source = QuestionSource(
    text="2*x + 5 = 17",
    main_variable="x",
    diagram_specs=[
        DiagramSpec(
            type="triangle",
            properties={
                "points": [
                    {"id": "A", "x": 0, "y": 0, "label": "A"},
                    {"id": "B", "x": 100, "y": 0, "label": "B"},
                    {"id": "C", "x": 50, "y": 80, "label": "C"},
                ],
                "lines": [
                    {"id": "AB", "start": "A", "end": "B"},
                    {"id": "BC", "start": "B", "end": "C"},
                    {"id": "CA", "start": "C", "end": "A"},
                ],
                "polygon": {
                    "id": "tri",
                    "vertices": ["A", "B", "C"],
                },
            },
        ),
    ],
)

# ── 3. Run the pipeline ────────────────────────────────────────────────
pkg = orch.run(source)

# ── 4. Print results ───────────────────────────────────────────────────
print("=" * 60)
print("GENERATED QUESTION PACKAGE")
print("=" * 60)
print(f"  Question ID:    {pkg.question_id}")
print(f"  Template ID:    {pkg.template_id}")
print(f"  Valid:          {pkg.is_valid}")
print(f"  Rendered text:  {pkg.rendered_question}")
print(f"  Expected ans:   {pkg.expected_answer}")
print(f"  Variable asgn:  {pkg.variable_assignments}")
print(f"  Diagrams:       {len(pkg.rendered_svgs)}")
print(f"  Pipeline steps: {len(pkg.metadata.pipeline_steps)}")
print(f"  Total time:     {pkg.metadata.generation_time_ms:.1f} ms")
print()

# ── 5. Print pipeline steps ────────────────────────────────────────────
print("Pipeline steps:")
for s in pkg.metadata.pipeline_steps:
    status = "✓" if s.success else "✗"
    print(f"  {status} {s.name}: {s.duration_ms:.1f} ms")

# ── 6. Print first SVG (if any) ────────────────────────────────────────
if pkg.rendered_svgs:
    print(f"\nSVG output ({len(pkg.rendered_svgs[0])} chars):")
    print(pkg.rendered_svgs[0][:500] + "...")

# ── 7. Save full JSON output ───────────────────────────────────────────
json_path = "m10_output.json"
with open(json_path, "w") as f:
    json.dump(pkg.to_dict(), f, indent=2)
print(f"\nFull package saved to: {json_path}")

# ── 8. Save SVG to file ────────────────────────────────────────────────
if pkg.rendered_svgs:
    svg_path = "m10_output.svg"
    with open(svg_path, "w") as f:
        f.write(pkg.rendered_svgs[0])
    print(f"SVG diagram saved to:  {svg_path}")
