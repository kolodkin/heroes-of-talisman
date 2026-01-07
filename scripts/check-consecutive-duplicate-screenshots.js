#!/usr/bin/env node

/**
 * Consecutive Duplicate Screenshot Detection for Playwright Reports
 *
 * PURPOSE:
 * Detects consecutive identical screenshots within the same test, which indicates
 * redundant screenshots that should be removed (no UI change between captures).
 *
 * HOW IT WORKS:
 * 1. Parses results.json to get screenshot order per test
 * 2. Uses perceptual hashing (via sharp) to compare consecutive screenshots
 * 3. Reports only consecutive duplicates within the same test as errors
 *
 * EXIT CODES:
 * - 0: No consecutive duplicates found
 * - 1: Consecutive duplicate screenshots found (requires fixing)
 *
 * Usage: node scripts/check-consecutive-duplicate-screenshots.js [report-dir]
 */

import { createHash } from "crypto";
import { readFileSync, existsSync } from "fs";
import { join } from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";
import sharp from "sharp";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = dirname(__dirname);

// Configuration
const REPORT_DIR = process.argv[2] || join(projectRoot, "playwright-report");
const REPORT_PORT = process.env.PLAYWRIGHT_REPORT_PORT || "9323";

/**
 * Compute perceptual hash of an image buffer using sharp.
 * This creates a hash based on the visual structure of the image,
 * tolerating minor pixel differences from anti-aliasing, subpixel
 * rendering, and compression artifacts.
 */
async function computePerceptualHashFromBuffer(buffer) {
  try {
    // Resize to 16x16 grayscale for perceptual comparison
    const { data } = await sharp(buffer)
      .resize(16, 16, { fit: "fill" })
      .grayscale()
      .raw()
      .toBuffer({ resolveWithObject: true });

    // Calculate mean brightness
    let sum = 0;
    for (let i = 0; i < data.length; i++) {
      sum += data[i];
    }
    const mean = sum / data.length;

    // Create binary hash: 1 if pixel > mean, 0 otherwise
    let hash = "";
    for (let i = 0; i < data.length; i++) {
      hash += data[i] > mean ? "1" : "0";
    }

    // Convert binary string to hex for compact representation
    let hexHash = "";
    for (let i = 0; i < hash.length; i += 4) {
      const nibble = hash.substring(i, i + 4);
      hexHash += parseInt(nibble, 2).toString(16);
    }

    return hexHash;
  } catch (err) {
    // Fallback to content hash if sharp fails
    return createHash("sha256").update(buffer).digest("hex");
  }
}

/**
 * Parse Playwright results.json to extract ordered screenshots per test.
 * Returns array of tests, each with ordered screenshot attachments.
 */
function parseTestScreenshots() {
  const tests = [];
  const jsonPath = join(REPORT_DIR, "results.json");

  if (!existsSync(jsonPath)) {
    console.log("⚠️  No results.json found in report (run tests with JSON reporter)");
    return tests;
  }

  try {
    const content = readFileSync(jsonPath, "utf-8");
    const data = JSON.parse(content);
    extractTestScreenshots(data, tests);
  } catch (err) {
    console.log(`⚠️  Error parsing results.json: ${err.message}`);
  }

  return tests;
}

/**
 * Recursively extract tests with their ordered screenshot attachments
 */
function extractTestScreenshots(data, tests, context = {}) {
  if (!data || typeof data !== "object") return;

  // Track test context
  if (data.title && data.file) {
    context = {
      ...context,
      testTitle: data.title,
      testFile: data.file,
    };
  }

  // Capture testId if present
  if (data.testId) {
    context = { ...context, testId: data.testId };
  }

  // Handle suites
  if (data.suites && Array.isArray(data.suites)) {
    for (const suite of data.suites) {
      extractTestScreenshots(suite, tests, context);
    }
  }

  // Handle specs
  if (data.specs && Array.isArray(data.specs)) {
    for (const spec of data.specs) {
      extractTestScreenshots(spec, tests, {
        ...context,
        testTitle: spec.title,
      });
    }
  }

  // Handle tests array
  if (data.tests && Array.isArray(data.tests)) {
    for (const test of data.tests) {
      extractTestScreenshots(test, tests, context);
    }
  }

  // Handle results - this is where attachments live
  if (data.results && Array.isArray(data.results)) {
    for (const result of data.results) {
      if (result.attachments && Array.isArray(result.attachments)) {
        // Extract only image attachments in order
        const screenshots = result.attachments
          .filter((att) => att.body && att.contentType?.startsWith("image/"))
          .map((att) => {
            const imageBuffer = Buffer.from(att.body, "base64");
            return {
              name: att.name,
              buffer: imageBuffer,
            };
          });

        if (screenshots.length > 0) {
          tests.push({
            testTitle: context.testTitle,
            testFile: context.testFile,
            testId: context.testId,
            screenshots,
          });
        }
      }
    }
  }
}

/**
 * Find consecutive duplicate screenshots within each test.
 * Returns array of duplicate pairs with test context.
 */
async function findConsecutiveDuplicates(tests) {
  const duplicates = [];
  let totalScreenshots = 0;

  for (const test of tests) {
    const { testTitle, testFile, testId, screenshots } = test;
    totalScreenshots += screenshots.length;

    if (screenshots.length < 2) continue;

    // Compute hashes for all screenshots in this test
    const hashes = await Promise.all(screenshots.map((s) => computePerceptualHashFromBuffer(s.buffer)));

    // Compare consecutive screenshots
    for (let i = 0; i < screenshots.length - 1; i++) {
      if (hashes[i] === hashes[i + 1]) {
        duplicates.push({
          testTitle,
          testFile,
          testId,
          first: screenshots[i].name,
          second: screenshots[i + 1].name,
          hash: hashes[i],
          position: i + 1, // 1-indexed position of the duplicate
        });
      }
    }
  }

  return { duplicates, totalScreenshots, totalTests: tests.length };
}

/**
 * Generate Playwright report URL for a test (search by title)
 */
function getReportUrl(testTitle) {
  if (!testTitle) return null;
  return `http://localhost:${REPORT_PORT}/#?q=${encodeURIComponent(testTitle)}`;
}

/**
 * Format duplicate report
 */
function formatDuplicateReport(duplicates, totalScreenshots, totalTests) {
  const lines = [];

  lines.push("");
  lines.push("╔════════════════════════════════════════════════════════════════════╗");
  lines.push("║     🚨 CONSECUTIVE DUPLICATE SCREENSHOTS FOUND 🚨                  ║");
  lines.push("╚════════════════════════════════════════════════════════════════════╝");
  lines.push("");

  for (let i = 0; i < duplicates.length; i++) {
    const dupe = duplicates[i];
    const reportUrl = getReportUrl(dupe.testTitle);

    lines.push(`┌─────────────────────────────────────────────────────────────────────┐`);
    lines.push(`│ 🚨 ERROR ${i + 1} of ${duplicates.length}`);
    lines.push(`├─────────────────────────────────────────────────────────────────────┤`);
    lines.push(`│ Test: ${dupe.testTitle}`);
    lines.push(`│ File: ${dupe.testFile}`);
    lines.push(`│`);
    lines.push(`│ 📸 Screenshot ${dupe.position}: "${dupe.first}"`);
    lines.push(`│ 📸 Screenshot ${dupe.position + 1}: "${dupe.second}"`);
    lines.push(`│`);
    lines.push(`│ These consecutive screenshots are identical.`);
    lines.push(`│ Remove one or add a UI change between them.`);
    if (reportUrl) {
      lines.push(`│`);
      lines.push(`│ 🔗 ${reportUrl}`);
    }
    lines.push(`└─────────────────────────────────────────────────────────────────────┘`);
    lines.push("");
  }

  lines.push("═══════════════════════════════════════════════════════════════════════");
  lines.push("");
  lines.push("💡 Recommended actions:");
  lines.push("   1. Review the test flow - is the second screenshot needed?");
  lines.push("   2. Ensure a visible UI change happens between screenshots");
  lines.push("   3. Remove the redundant screenshot (preferably the FIRST occurrence)");
  lines.push("");
  lines.push(`📊 Run 'npm run e2p' or visit http://localhost:${REPORT_PORT} to view the full report`);
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════════════════════");
  lines.push("");
  lines.push("🗑️  SCREENSHOTS TO DELETE (first occurrences):");
  lines.push("");
  for (const dupe of duplicates) {
    lines.push(`   • "${dupe.first}" in ${dupe.testFile} (test: "${dupe.testTitle}")`);
  }
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════════════════════");

  return lines.join("\n");
}

/**
 * Main function
 */
async function main() {
  console.log("🔍 Checking for consecutive duplicate screenshots in Playwright report...");
  console.log(`📁 Report directory: ${REPORT_DIR}`);
  console.log("");

  // Check if report directory exists
  if (!existsSync(REPORT_DIR)) {
    console.log("⚠️  Report directory does not exist. Skipping duplicate check.");
    console.log("   This is expected if no tests have been run yet.");
    process.exit(0);
  }

  // Parse test screenshots from results.json
  const tests = parseTestScreenshots();

  if (tests.length === 0) {
    console.log("⚠️  No test screenshots found. Exiting.");
    process.exit(0);
  }

  // Find consecutive duplicates
  console.log("🔬 Computing perceptual hashes and comparing consecutive screenshots...");
  const { duplicates, totalScreenshots, totalTests } = await findConsecutiveDuplicates(tests);

  console.log(`📊 Analyzed ${totalScreenshots} screenshots across ${totalTests} tests`);
  console.log("");

  if (duplicates.length === 0) {
    console.log("✅ No consecutive duplicate screenshots detected!");
    console.log(`   All ${totalScreenshots} screenshots are visually distinct from their neighbors.`);
    process.exit(0);
  }

  // Report duplicates
  const report = formatDuplicateReport(duplicates, totalScreenshots, totalTests);
  console.error(report);

  console.log("");
  console.log(`❌ FAILED: Found ${duplicates.length} consecutive duplicate(s)`);
  console.log(`   Total screenshots: ${totalScreenshots}`);
  console.log(`   Total tests: ${totalTests}`);
  console.log("");
  process.exit(1);
}

// Run
main().catch((err) => {
  console.error("Error:", err);
  process.exit(1);
});
