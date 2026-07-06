import fs from 'fs';

const svgContent = fs.readFileSync('C:\\Users\\jain2\\.gemini\\antigravity-ide\\brain\\153fd7cc-112b-4b93-8cfc-2054dcdb8848\\.system_generated\\steps\\39\\content.md', 'utf-8');

// Extract SVG
const match = svgContent.match(/<svg[\s\S]*?<\/svg>/);
if (!match) {
  console.error("No SVG found");
  process.exit(1);
}

let svg = match[0];

// Remove metadata
svg = svg.replace(/<metadata>[\s\S]*?<\/metadata>/g, '');
svg = svg.replace(/<defs\/>/g, '');
svg = svg.replace(/xml:space="preserve"/g, 'xmlSpace="preserve"');
svg = svg.replace(/fill-rule/g, 'fillRule');
svg = svg.replace(/clip-rule/g, 'clipRule');
svg = svg.replace(/stroke-linecap/g, 'strokeLinecap');
svg = svg.replace(/stroke-linejoin/g, 'strokeLinejoin');
svg = svg.replace(/vectornator:layerName="[^"]*"/g, '');
svg = svg.replace(/xmlns:vectornator="[^"]*"/g, '');
svg = svg.replace(/xmlns:xlink="[^"]*"/g, '');
svg = svg.replace(/fill="#[a-zA-Z0-9]+"/g, 'fill="currentColor"');
svg = svg.replace(/class="[^"]*"/g, '');

const componentCode = `import React from 'react';

export default function BoostLogo({ className = "" }: { className?: string }) {
  return (
    ${svg.replace('<svg ', '<svg className={className} ')}
  );
}
`;

fs.writeFileSync('src/components/shared/BoostLogo.tsx', componentCode);
console.log("Converted SVG and created src/components/shared/BoostLogo.tsx");
