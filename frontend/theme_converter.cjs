const fs = require('fs');
const path = require('path');

const dirs = [
  'src/components/school',
  'src/components/univ'
];

const colorReplacements = [
  // Tailwind default color ranges
  { regex: /(bg|text|border|ring)-(emerald|green|purple|yellow|orange|red|teal|cyan|pink)-([1-9]00|50)/g, replacement: '$1-blue-$3' },

  // Hex colors - Backgrounds
  { regex: /bg-\[#F6A6C1\]/g, replacement: 'bg-blue-300' },
  { regex: /bg-\[#B4F94C\]/g, replacement: 'bg-blue-500' },
  { regex: /bg-\[#34D399\]/g, replacement: 'bg-blue-500' },
  { regex: /bg-\[#F4A6C9\]/g, replacement: 'bg-blue-200' },
  { regex: /bg-\[#F5A8D0\]/g, replacement: 'bg-blue-200' },
  { regex: /bg-\[#FFE4EE\]/g, replacement: 'bg-blue-50' },
  { regex: /bg-\[#FFDF6B\]/g, replacement: 'bg-blue-200' },
  
  // Hex colors - Text
  { regex: /text-\[#4d7014\]/g, replacement: 'text-blue-800' },
  { regex: /text-\[#6d942a\]/g, replacement: 'text-blue-700' },
  { regex: /text-\[#F59E0B\]/g, replacement: 'text-blue-400' },
  { regex: /text-\[#FFD166\]/g, replacement: 'text-blue-300' },

  // Dark grays/blacks to Dark Blues
  { regex: /bg-\[#050505\]/g, replacement: 'bg-blue-950' },
  { regex: /bg-\[#1E1E1E\]/g, replacement: 'bg-blue-900' },
  { regex: /bg-\[#1F1E1E\]/g, replacement: 'bg-blue-900' },
  { regex: /bg-\[#2A2A2A\]/g, replacement: 'bg-blue-800' },
  { regex: /bg-\[#222222\]/g, replacement: 'bg-blue-950' },
  { regex: /bg-\[#333131\]/g, replacement: 'bg-blue-800' },
  { regex: /border-\[#333333\]/g, replacement: 'border-blue-800' },
  { regex: /bg-\[#2A2726\]/g, replacement: 'bg-blue-700' },
  
  // Grays to light blues (for text on dark backgrounds)
  { regex: /text-\[#A3A3A3\]/g, replacement: 'text-blue-200' },
  { regex: /text-gray-400/g, replacement: 'text-blue-200' },
  { regex: /text-gray-500/g, replacement: 'text-blue-300' },
  
  // Additional text colors found in search
  { regex: /text-\[#0cc270\]/g, replacement: 'text-blue-500' },
  { regex: /bg-\[#0cc270\]/g, replacement: 'bg-blue-500' }
];

function processDirectory(directory) {
  const files = fs.readdirSync(directory);
  for (const file of files) {
    const fullPath = path.join(directory, file);
    if (fs.statSync(fullPath).isDirectory()) {
      processDirectory(fullPath);
    } else if (fullPath.endsWith('.tsx') || fullPath.endsWith('.ts')) {
      let content = fs.readFileSync(fullPath, 'utf8');
      let original = content;
      
      for (const rule of colorReplacements) {
        content = content.replace(rule.regex, rule.replacement);
      }
      
      if (content !== original) {
        fs.writeFileSync(fullPath, content, 'utf8');
        console.log(`Updated ${fullPath}`);
      }
    }
  }
}

for (const dir of dirs) {
  if (fs.existsSync(dir)) {
    processDirectory(dir);
  }
}

console.log("Done applying blue theme replacements.");
