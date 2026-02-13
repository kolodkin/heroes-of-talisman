#!/usr/bin/env node

/**
 * Extract embedded base64 images from Playwright results.json into separate files.
 *
 * Runs after Playwright tests to reduce results.json size before upload.
 * Replaces inline base64 `body` with `path` references to external files.
 *
 * Usage: node scripts/compress-result-json-images.js [report-dir]
 * Default report-dir: playwright-report
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "fs";
import { join } from "path";
import { createHash } from "crypto";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = dirname(__dirname);

const REPORT_DIR = process.argv[2] || join(projectRoot, "playwright-report");
const SCREENSHOTS_DIR = join(REPORT_DIR, "screenshots");
const RESULTS_JSON = join(REPORT_DIR, "results.json");

/**
 * Recursively walk the results.json tree and extract image attachments.
 * Replaces `body` (base64) with `path` (relative file path) in-place.
 * Returns the number of images extracted.
 */
function extractImages(data) {
  if (!data || typeof data !== "object") return 0;

  let count = 0;

  // Walk suites
  if (Array.isArray(data.suites)) {
    for (const suite of data.suites) {
      count += extractImages(suite);
    }
  }

  // Walk specs
  if (Array.isArray(data.specs)) {
    for (const spec of data.specs) {
      count += extractImages(spec);
    }
  }

  // Walk tests
  if (Array.isArray(data.tests)) {
    for (const test of data.tests) {
      count += extractImages(test);
    }
  }

  // Walk results — this is where attachments live
  if (Array.isArray(data.results)) {
    for (const result of data.results) {
      if (!Array.isArray(result.attachments)) continue;

      for (const att of result.attachments) {
        if (!att.body || !att.contentType?.startsWith("image/")) continue;

        const imageBuffer = Buffer.from(att.body, "base64");
        const hash = createHash("sha256").update(imageBuffer).digest("hex");

        // Determine file extension from contentType
        const ext = att.contentType === "image/png" ? "png" : "jpg";
        const filename = `${hash}.${ext}`;
        const filePath = join(SCREENSHOTS_DIR, filename);

        // Write image file (skip if identical hash already written)
        if (!existsSync(filePath)) {
          writeFileSync(filePath, imageBuffer);
        }

        // Replace body with path reference (relative to report dir)
        delete att.body;
        att.path = `screenshots/${filename}`;

        count++;
      }
    }
  }

  return count;
}

function main() {
  if (!existsSync(RESULTS_JSON)) {
    console.log("⚠️  No results.json found. Skipping image extraction.");
    process.exit(0);
  }

  console.log(`📦 Extracting images from results.json...`);
  console.log(`   Report dir: ${REPORT_DIR}`);

  // Read results.json
  const content = readFileSync(RESULTS_JSON, "utf-8");
  const originalSize = Buffer.byteLength(content);
  const data = JSON.parse(content);

  // Create screenshots directory
  mkdirSync(SCREENSHOTS_DIR, { recursive: true });

  // Extract images in-place
  const count = extractImages(data);

  if (count === 0) {
    console.log("   No embedded images found.");
    process.exit(0);
  }

  // Write back the smaller results.json
  const newContent = JSON.stringify(data);
  writeFileSync(RESULTS_JSON, newContent);
  const newSize = Buffer.byteLength(newContent);

  const savedMB = ((originalSize - newSize) / 1024 / 1024).toFixed(1);
  const originalMB = (originalSize / 1024 / 1024).toFixed(1);
  const newMB = (newSize / 1024 / 1024).toFixed(1);

  console.log(`   Extracted ${count} images to ${SCREENSHOTS_DIR}`);
  console.log(`   results.json: ${originalMB}MB → ${newMB}MB (saved ${savedMB}MB)`);
  console.log(`✅ Done`);
}

main();
