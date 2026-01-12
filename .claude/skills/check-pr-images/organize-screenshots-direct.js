#!/usr/bin/env node

/**
 * Organize screenshots directly from Playwright report into test_filename/test_name/screenshot_name.png structure
 * Usage: node organize-screenshots-direct.js <results-json-path> <data-dir> <output-dir>
 */

import { readFileSync, existsSync, mkdirSync, copyFileSync, readdirSync, writeFileSync } from "fs";
import { join, basename } from "path";
import { createHash } from "crypto";

const resultsJsonPath = process.argv[2];
const dataDir = process.argv[3]; // Directory with .dat files
const outputDir = process.argv[4] || "./tmp/report/screenshots";

if (!resultsJsonPath || !dataDir) {
  console.error("Usage: node organize-screenshots-direct.js <results-json-path> <data-dir> [output-dir]");
  process.exit(1);
}

if (!existsSync(resultsJsonPath)) {
  console.error("⚠️  results.json not found");
  process.exit(1);
}

if (!existsSync(dataDir)) {
  console.error("⚠️  data directory not found");
  process.exit(1);
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
          .filter((att) => att.body && att.contentType?.startsWith("image/"))
          .map((att) => {
            // Compute full hash to match with .dat filenames
            const imageBuffer = Buffer.from(att.body, "base64");
            const hash = createHash("sha256").update(imageBuffer).digest("hex");
            return {
              name: att.name,
              hash: hash, // Full 64-char hex hash
              buffer: imageBuffer,
            };
          });

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
    console.error("⚠️  No test screenshots found in results.json");
    process.exit(1);
  }

  // Create output directory
  mkdirSync(outputDir, { recursive: true });

  let totalCopied = 0;
  let testCounter = {};

  for (const test of tests) {
    // Create test directory structure: test_filename/test_name/
    const testFile = sanitizeFilename(basename(test.testFile, '.spec.js'));
    const testName = sanitizeFilename(test.testTitle);

    // Handle duplicate test names by adding counter
    const testKey = `${testFile}/${testName}`;
    testCounter[testKey] = (testCounter[testKey] || 0) + 1;
    const testPath = testCounter[testKey] > 1
      ? `${testFile}/${testName}-${testCounter[testKey]}`
      : `${testFile}/${testName}`;

    const testDir = join(outputDir, testPath);
    mkdirSync(testDir, { recursive: true });

    for (const screenshot of test.screenshots) {
      // Find source .dat file by hash
      const datFile = join(dataDir, `${screenshot.hash}.dat`);

      if (existsSync(datFile)) {
        const destFile = join(testDir, `${screenshot.name}.png`);
        copyFileSync(datFile, destFile);
        totalCopied++;
      } else {
        // Fallback: write from buffer if .dat file not found
        const destFile = join(testDir, `${screenshot.name}.png`);
        writeFileSync(destFile, screenshot.buffer);
        totalCopied++;
      }
    }
  }

  console.log(`✅ Organized ${totalCopied} screenshots into ${Object.keys(testCounter).length} test directories`);
  process.exit(0);

} catch (err) {
  console.error(`⚠️  Error: ${err.message}`);
  process.exit(1);
}
