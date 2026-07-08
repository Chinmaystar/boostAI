import type { Variant } from '../models/reviewSession';

export const MOCK_VARIANTS: Record<string, Variant[]> = {
  q1: [
    { id: 'v-q1-a', label: 'A', text: 'Solve 5x + 4 = 29', difficulty: 'similar', templateId: 'templ-linear-01', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q1-b', label: 'B', text: 'Solve 9x + 6 = 42', difficulty: 'similar', templateId: 'templ-linear-02', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q1-c', label: 'C', text: 'Solve 8x + 9 = 33', difficulty: 'similar', templateId: 'templ-linear-03', estimatedTime: 60, hasDiagram: false, isFavorite: false },
  ],
  q2: [
    { id: 'v-q2-a', label: 'A', text: 'Factorise x² + 7x + 12', difficulty: 'similar', templateId: 'templ-factor-01', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q2-b', label: 'B', text: 'Factorise x² + 8x + 15', difficulty: 'harder', templateId: 'templ-factor-02', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q2-c', label: 'C', text: 'Factorise x² - x - 6', difficulty: 'harder', templateId: 'templ-factor-03', estimatedTime: 120, hasDiagram: false, isFavorite: false },
  ],
  q3: [
    { id: 'v-q3-a', label: 'A', text: 'Calculate the area of a circle with radius 5 cm. Give your answer in terms of π.', difficulty: 'similar', templateId: 'templ-circle-01', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q3-b', label: 'B', text: 'Calculate the area of a circle with diameter 12 cm. Give your answer in terms of π.', difficulty: 'harder', templateId: 'templ-circle-02', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q3-c', label: 'C', text: 'Calculate the area of a circle with radius 3.5 cm. Give your answer to 3 significant figures.', difficulty: 'harder', templateId: 'templ-circle-03', estimatedTime: 120, hasDiagram: false, isFavorite: false },
  ],
  q4: [
    { id: 'v-q4-a', label: 'A', text: 'A bag contains 4 red balls, 4 blue balls and 2 green balls. A ball is chosen at random. What is the probability that it is red?', difficulty: 'similar', templateId: 'templ-prob-01', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q4-b', label: 'B', text: 'A bag contains 6 red balls, 2 blue balls and 2 yellow balls. A ball is chosen at random. What is the probability that it is not red?', difficulty: 'similar', templateId: 'templ-prob-02', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q4-c', label: 'C', text: 'A bag contains 8 red balls, 3 blue balls, and some green balls. The probability of choosing a green ball is 1/3. How many green balls are there?', difficulty: 'harder', templateId: 'templ-prob-03', estimatedTime: 180, hasDiagram: false, isFavorite: false },
  ],
  q5: [
    { id: 'v-q5-a', label: 'A', text: 'Solve the simultaneous equations:\n3x + y = 10\nx - y = 2', difficulty: 'similar', templateId: 'templ-simul-01', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q5-b', label: 'B', text: 'Solve the simultaneous equations:\n2x + 3y = 7\nx - 2y = 0', difficulty: 'harder', templateId: 'templ-simul-02', estimatedTime: 180, hasDiagram: false, isFavorite: false },
    { id: 'v-q5-c', label: 'C', text: 'Solve the simultaneous equations:\n4x + y = 11\n2x - 3y = 9', difficulty: 'harder', templateId: 'templ-simul-03', estimatedTime: 180, hasDiagram: false, isFavorite: false },
  ],
  q6: [
    { id: 'v-q6-a', label: 'A', text: 'Expand and simplify (x + 5)(x - 2)', difficulty: 'similar', templateId: 'templ-expand-01', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q6-b', label: 'B', text: 'Expand and simplify (2x + 3)(x - 1)', difficulty: 'harder', templateId: 'templ-expand-02', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q6-c', label: 'C', text: 'Expand and simplify (x + 4)(x - 4)', difficulty: 'similar', templateId: 'templ-expand-03', estimatedTime: 60, hasDiagram: false, isFavorite: false },
  ],
  q7: [
    { id: 'v-q7-a', label: 'A', text: 'The diagram shows a right-angled triangle with legs 6 cm and 8 cm. Calculate the length of the hypotenuse.', difficulty: 'similar', templateId: 'templ-pythag-01', estimatedTime: 90, hasDiagram: true, isFavorite: false },
    { id: 'v-q7-b', label: 'B', text: 'The diagram shows a right-angled triangle with legs 5 cm and 12 cm. Calculate the length of the hypotenuse.', difficulty: 'similar', templateId: 'templ-pythag-02', estimatedTime: 90, hasDiagram: true, isFavorite: false },
    { id: 'v-q7-c', label: 'C', text: 'The diagram shows a right-angled triangle with hypotenuse 13 cm and one leg 5 cm. Calculate the length of the other leg.', difficulty: 'harder', templateId: 'templ-pythag-03', estimatedTime: 120, hasDiagram: true, isFavorite: false },
  ],
  q8: [
    { id: 'v-q8-a', label: 'A', text: 'Differentiate y = 4x² + 3x - 7 with respect to x.', difficulty: 'similar', templateId: 'templ-diff-01', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q8-b', label: 'B', text: 'Differentiate y = 5x² - 2x + 1 with respect to x.', difficulty: 'similar', templateId: 'templ-diff-02', estimatedTime: 90, hasDiagram: false, isFavorite: false },
    { id: 'v-q8-c', label: 'C', text: 'Differentiate y = 2x³ + 3x² - x + 4 with respect to x.', difficulty: 'harder', templateId: 'templ-diff-03', estimatedTime: 120, hasDiagram: false, isFavorite: false },
  ],
  q9: [
    { id: 'v-q9-a', label: 'A', text: 'A car travels 150 miles in 3 hours. Calculate its average speed in miles per hour.', difficulty: 'similar', templateId: 'templ-speed-01', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q9-b', label: 'B', text: 'A cyclist travels 45 miles at an average speed of 15 mph. How long does the journey take?', difficulty: 'similar', templateId: 'templ-speed-02', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q9-c', label: 'C', text: 'A train travels 240 km at an average speed of 96 km/h. It then travels a further 120 km at 80 km/h. Calculate the average speed for the whole journey.', difficulty: 'harder', templateId: 'templ-speed-03', estimatedTime: 180, hasDiagram: false, isFavorite: false },
  ],
  q10: [
    { id: 'v-q10-a', label: 'A', text: 'Solve the inequality 3x - 5 ≤ x + 7', difficulty: 'similar', templateId: 'templ-ineq-01', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q10-b', label: 'B', text: 'Solve the inequality 5x + 3 > 2x - 9', difficulty: 'similar', templateId: 'templ-ineq-02', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q10-c', label: 'C', text: 'Solve the inequality 6 ≤ 2x + 4 < 14', difficulty: 'harder', templateId: 'templ-ineq-03', estimatedTime: 120, hasDiagram: false, isFavorite: false },
  ],
  q11: [
    { id: 'v-q11-a', label: 'A', text: 'The graph of y = f(x) is shown on the grid. Sketch the graph of y = f(2x).', difficulty: 'harder', templateId: 'templ-graph-01', estimatedTime: 120, hasDiagram: true, isFavorite: false },
    { id: 'v-q11-b', label: 'B', text: 'The graph of y = f(x) is shown on the grid. Sketch the graph of y = f(x) + 3.', difficulty: 'easier', templateId: 'templ-graph-02', estimatedTime: 90, hasDiagram: true, isFavorite: false },
    { id: 'v-q11-c', label: 'C', text: 'The graph of y = f(x) is shown on the grid. Sketch the graph of y = -f(x).', difficulty: 'similar', templateId: 'templ-graph-03', estimatedTime: 90, hasDiagram: true, isFavorite: false },
  ],
  q12: [
    { id: 'v-q12-a', label: 'A', text: 'Prove that the sum of any four consecutive integers is even.', difficulty: 'harder', templateId: 'templ-proof-01', estimatedTime: 180, hasDiagram: false, isFavorite: false },
    { id: 'v-q12-b', label: 'B', text: 'Prove that the sum of any five consecutive integers is a multiple of 5.', difficulty: 'similar', templateId: 'templ-proof-02', estimatedTime: 150, hasDiagram: false, isFavorite: false },
    { id: 'v-q12-c', label: 'C', text: 'Prove that the sum of any three consecutive even numbers is a multiple of 6.', difficulty: 'harder', templateId: 'templ-proof-03', estimatedTime: 180, hasDiagram: false, isFavorite: false },
  ],
  q13: [
    { id: 'v-q13-a', label: 'A', text: 'A sequence has nth term = 2n² + 1. Find the first three terms of the sequence.', difficulty: 'similar', templateId: 'templ-seq-01', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q13-b', label: 'B', text: 'A sequence has nth term = n² - 3. Find the first three terms of the sequence.', difficulty: 'easier', templateId: 'templ-seq-02', estimatedTime: 60, hasDiagram: false, isFavorite: false },
    { id: 'v-q13-c', label: 'C', text: 'A sequence has nth term = 2n² - n. Find the first four terms of the sequence.', difficulty: 'similar', templateId: 'templ-seq-03', estimatedTime: 90, hasDiagram: false, isFavorite: false },
  ],
  q14: [
    { id: 'v-q14-a', label: 'A', text: 'Calculate the volume of a cylinder with radius 4 cm and height 10 cm. Give your answer to 3 significant figures.', difficulty: 'similar', templateId: 'templ-cyl-01', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q14-b', label: 'B', text: 'Calculate the volume of a cylinder with diameter 10 cm and height 6 cm. Give your answer in terms of π.', difficulty: 'harder', templateId: 'templ-cyl-02', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q14-c', label: 'C', text: 'A cylinder has volume 200π cm³ and height 8 cm. Calculate its radius.', difficulty: 'harder', templateId: 'templ-cyl-03', estimatedTime: 150, hasDiagram: false, isFavorite: false },
  ],
  q15: [
    { id: 'v-q15-a', label: 'A', text: 'A Venn diagram shows 12 students study French, 8 study Spanish, and 4 study both. Find P(F ∪ S).', difficulty: 'similar', templateId: 'templ-venn-01', estimatedTime: 90, hasDiagram: true, isFavorite: false },
    { id: 'v-q15-b', label: 'B', text: 'A Venn diagram shows 15 students study Biology, 10 study Chemistry, and 5 study both. Find P(B ∩ C).', difficulty: 'easier', templateId: 'templ-venn-02', estimatedTime: 60, hasDiagram: true, isFavorite: false },
    { id: 'v-q15-c', label: 'C', text: 'A Venn diagram shows 20 students study History, 12 study Geography. 6 study both and 4 study neither. Find the total number of students.', difficulty: 'harder', templateId: 'templ-venn-03', estimatedTime: 150, hasDiagram: true, isFavorite: false },
  ],
  q16: [
    { id: 'v-q16-a', label: 'A', text: 'f(x) = 3x² - 6x + 1. Find the coordinates of the turning point of f(x).', difficulty: 'similar', templateId: 'templ-turn-01', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q16-b', label: 'B', text: 'f(x) = x² - 8x + 5. Find the coordinates of the turning point of f(x).', difficulty: 'similar', templateId: 'templ-turn-02', estimatedTime: 120, hasDiagram: false, isFavorite: false },
    { id: 'v-q16-c', label: 'C', text: 'f(x) = 4x² + 4x - 3. Find the coordinates of the turning point of f(x) and state whether it is a maximum or minimum.', difficulty: 'harder', templateId: 'templ-turn-03', estimatedTime: 150, hasDiagram: false, isFavorite: false },
  ],
};
