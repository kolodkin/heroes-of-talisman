#!/usr/bin/env node

/**
 * Organize screenshots by test name with descriptive filenames
 * Usage: node organize-screenshots.js <results-json-path> <screenshots-dir> <output-dir>
 */

import { readFileSync, existsSync, mkdirSync, copyFileSync, readdirSync } from "fs";
import { join, basename, dirname } from "path";
import { createHash } from "crypto";

const resultsJsonPath = process.argv[2];
const screenshotsDir = process.argv[3];
const outputDir = process.argv[4] || "./tmp/report/organized";

if (!resultsJsonPath || !screenshotsDir) {
  console.error("Usage: node organize-screenshots.js <results-json-path> <screenshots-dir> [output-dir]");
  process.exit(1);
}

if (!existsSync(resultsJsonPath)) {
  console.log("⚠️  results.json not found. Cannot organize screenshots.");
  process.exit(0);
}

/**
 * Recursively extract test information with screenshot mappings
 */
function extractTestInfo(data, tests = [], context = {}) {
  if (!data || typeof data !== "object") return tests;

  // Track suite/spec context
  if (data.title && data.file) {
    context = {
      ...context,
      suiteTitle: context.suiteTitle || data.title,
      testFile: data.file,
    };
  }

  // Handle suites
  if (data.suites && Array.isArray(data.suites)) {
    for (const suite of data.suites) {
      extractTestInfo(suite, tests, context);
    }
  }

  // Handle specs
  if (data.specs && Array.isArray(data.specs)) {
    for (const spec of data.specs) {
      extractTestInfo(spec, tests, {
        ...context,
        testTitle: spec.title,
      });
    }
  }

  // Handle tests array
  if (data.tests && Array.isArray(data.tests)) {
    for (const test of data.tests) {
      extractTestInfo(test, tests, context);
    }
  }

  // Handle results - this is where attachments live
  if (data.results && Array.isArray(data.results)) {
    for (const result of data.results) {
      if (result.attachments && Array.isArray(result.attachments)) {
        const screenshots = result.attachments
          .filter((att) => (att.body || att.path) && att.contentType?.startsWith("image/"))
          .map((att) => {
            // Get image buffer from body (base64) or path (external file)
            let imageBuffer;
            if (att.body) {
              imageBuffer = Buffer.from(att.body, "base64");
            } else if (att.path) {
              const reportDir = dirname(resultsJsonPath);
              const filePath = join(reportDir, att.path);
              imageBuffer = existsSync(filePath) ? readFileSync(filePath) : null;
            }
            if (!imageBuffer) return null;
            const hash = createHash("sha256").update(imageBuffer).digest("hex");
            return {
              name: att.name,
              hash: hash.substring(0, 20), // Match Playwright's hash length
            };
          })
          .filter(Boolean);

        if (screenshots.length > 0) {
          tests.push({
            testTitle: context.testTitle || context.suiteTitle || "Unknown Test",
            testFile: context.testFile || "Unknown File",
            screenshots,
          });
        }
      }
    }
  }

  return tests;
}

/**
 * Sanitize filename for filesystem
 */
function sanitizeFilename(name) {
  return name
    .replace(/[^a-zA-Z0-9-_ ]/g, '-')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .toLowerCase();
}

try {
  const content = readFileSync(resultsJsonPath, "utf-8");
  const data = JSON.parse(content);
  const tests = extractTestInfo(data);

  if (tests.length === 0) {
    console.log("⚠️  No test screenshots found in results.json");
    process.exit(0);
  }

  // Create output directory
  mkdirSync(outputDir, { recursive: true });

  console.log("📁 Organizing screenshots by test name...\n");

  let totalCopied = 0;
  let testCounter = {};

  for (const test of tests) {
    // Create unique test directory name
    const baseTestName = sanitizeFilename(test.testTitle);
    const testFile = basename(test.testFile, '.spec.js');

    // Handle duplicate test names by adding counter
    const testKey = `${testFile}-${baseTestName}`;
    testCounter[testKey] = (testCounter[testKey] || 0) + 1;
    const testDirName = testCounter[testKey] > 1
      ? `${testFile}/${baseTestName}-${testCounter[testKey]}`
      : `${testFile}/${baseTestName}`;

    const testDir = join(outputDir, testDirName);
    mkdirSync(testDir, { recursive: true });

    console.log(`📂 ${testDirName}`);

    for (const screenshot of test.screenshots) {
      // Find source file - try exact hash first, then wildcard pattern
      let sourceFile = join(screenshotsDir, `${screenshot.hash}.png`);

      if (!existsSync(sourceFile)) {
        // Try with wildcard for partial hash match
        const files = readdirSync(screenshotsDir);
        const matchingFile = files.find(f => f.startsWith(screenshot.hash));
        if (matchingFile) {
          sourceFile = join(screenshotsDir, matchingFile);
        }
      }

      if (existsSync(sourceFile)) {
        const destFile = join(testDir, `${screenshot.name}.png`);
        copyFileSync(sourceFile, destFile);
        console.log(`   ✓ ${screenshot.name}.png`);
        totalCopied++;
      } else {
        console.log(`   ✗ ${screenshot.name}.png (source not found: ${screenshot.hash}*.png)`);
      }
    }
    console.log();
  }

  console.log("═══════════════════════════════════════════════════════════════");
  console.log(`✅ Organized ${totalCopied} screenshots into ${Object.keys(testCounter).length} test directories`);
  console.log(`📂 Location: ${outputDir}`);
  console.log("═══════════════════════════════════════════════════════════════");

} catch (err) {
  console.error(`⚠️  Error: ${err.message}`);
  process.exit(1);
}
