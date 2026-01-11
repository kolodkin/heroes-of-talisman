#!/usr/bin/env node

/**
 * Parse Playwright results.json and generate enhanced summary with test context
 * Usage: node parse-test-results.js <results-json-path> <screenshots-dir>
 */

import { readFileSync, readdirSync, existsSync } from "fs";
import { join, basename } from "path";
import { createHash } from "crypto";

const resultsJsonPath = process.argv[2];
const screenshotsDir = process.argv[3];

if (!resultsJsonPath || !screenshotsDir) {
  console.error("Usage: node parse-test-results.js <results-json-path> <screenshots-dir>");
  process.exit(1);
}

if (!existsSync(resultsJsonPath)) {
  console.log("⚠️  results.json not found. Cannot extract test context.");
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
          .filter((att) => att.body && att.contentType?.startsWith("image/"))
          .map((att) => {
            // Compute hash to match with .dat/.png filenames
            const imageBuffer = Buffer.from(att.body, "base64");
            const hash = createHash("sha256").update(imageBuffer).digest("hex");
            return {
              name: att.name,
              hash: hash.substring(0, 20), // Match Playwright's hash length
            };
          });

        if (screenshots.length > 0) {
          tests.push({
            testTitle: context.testTitle || context.suiteTitle || "Unknown Test",
            testFile: context.testFile || "Unknown File",
            status: result.status,
            duration: result.duration,
            screenshots,
          });
        }
      }
    }
  }

  return tests;
}

try {
  const content = readFileSync(resultsJsonPath, "utf-8");
  const data = JSON.parse(content);
  const tests = extractTestInfo(data);

  if (tests.length === 0) {
    console.log("⚠️  No test screenshots found in results.json");
    process.exit(0);
  }

  // Get actual screenshot files
  const screenshotFiles = existsSync(screenshotsDir)
    ? readdirSync(screenshotsDir).filter(f => f.endsWith(".png"))
    : [];

  console.log("\n═══════════════════════════════════════════════════════════════");
  console.log("📊 TEST RESULTS WITH SCREENSHOTS");
  console.log("═══════════════════════════════════════════════════════════════\n");

  let totalTests = 0;
  let totalScreenshots = 0;
  let passedTests = 0;
  let failedTests = 0;

  for (const test of tests) {
    totalTests++;
    totalScreenshots += test.screenshots.length;

    const statusIcon = test.status === "passed" ? "✅" : test.status === "failed" ? "❌" : "⚠️";
    if (test.status === "passed") passedTests++;
    if (test.status === "failed") failedTests++;

    console.log(`${statusIcon} ${test.testTitle}`);
    console.log(`   File: ${test.testFile}`);
    console.log(`   Status: ${test.status}`);
    console.log(`   Duration: ${Math.round(test.duration)}ms`);
    console.log(`   Screenshots (${test.screenshots.length}):`);

    for (const screenshot of test.screenshots) {
      // Try to find matching file
      const matchingFile = screenshotFiles.find(f => f.includes(screenshot.hash));
      if (matchingFile) {
        console.log(`      • ${screenshot.name} → ${matchingFile}`);
      } else {
        console.log(`      • ${screenshot.name} (hash: ${screenshot.hash})`);
      }
    }
    console.log("");
  }

  console.log("═══════════════════════════════════════════════════════════════");
  console.log("📈 SUMMARY");
  console.log("═══════════════════════════════════════════════════════════════");
  console.log(`   Total Tests: ${totalTests}`);
  console.log(`   Passed: ✅ ${passedTests}`);
  console.log(`   Failed: ❌ ${failedTests}`);
  console.log(`   Total Screenshots: ${totalScreenshots}`);
  console.log(`   Screenshot Files: ${screenshotFiles.length}`);
  console.log("═══════════════════════════════════════════════════════════════\n");

} catch (err) {
  console.error(`⚠️  Error parsing results.json: ${err.message}`);
  process.exit(1);
}
