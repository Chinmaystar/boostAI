const fs = require('fs');
const path = require('path');

function processDir(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            processDir(fullPath);
        } else if (fullPath.endsWith('.tsx')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            let originalContent = content;

            // Replace bg-white in top-level containers
            content = content.replace(/className="w-full bg-white/g, 'className="w-full');
            content = content.replace(/className="min-h-screen bg-white/g, 'className="min-h-screen');

            if (content !== originalContent) {
                fs.writeFileSync(fullPath, content, 'utf8');
                console.log(`Updated ${fullPath}`);
            }
        }
    }
}

processDir(path.join(__dirname, 'src', 'pages'));
processDir(path.join(__dirname, 'src', 'components', 'school'));
processDir(path.join(__dirname, 'src', 'components', 'univ'));
