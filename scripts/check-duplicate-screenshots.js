#!/usr/bin/env node

/**
 * Script to detect duplicate screenshots in Playwright HTML report.
 *
 * This script:
 * 1. Scans the playwright-report directory for images
 * 2. Computes SHA256 hashes to detect duplicates
 * 3. Extracts test/screenshot metadata from report data
 * 4. Reports duplicates with detailed information
 * 5. Exits with code 1 if duplicates are found
 *
 * Usage: node scripts/check-duplicate-screenshots.js [report-dir]
 */

import { createHash } from "crypto";
import { readFileSync, readdirSync, existsSync, statSync } from "fs";
import { join, basename, extname, relative } from "path";
import { fileURLToPath } from "url";
import { dirname } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = dirname(__dirname);

// Configuration
const REPORT_DIR = process.argv[2] || join(projectRoot, "playwright-report");
const IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".dat"];
const MIN_IMAGE_SIZE = 1000; // Skip tiny images (likely icons)

// Image magic bytes for detection
const IMAGE_SIGNATURES = {
  png: Buffer.from([0x89, 0x50, 0x4e, 0x47]), // PNG
  jpg: Buffer.from([0xff, 0xd8, 0xff]), // JPEG
  webp: Buffer.from("RIFF"), // WebP (starts with RIFF)
};

/**
 * Check if a file is an image by reading its magic bytes
 */
function isImageFile(filePath) {
  try {
    const fd = readFileSync(filePath);
    if (fd.length < 12) return false;

    // Check PNG signature
    if (fd.subarray(0, 4).equals(IMAGE_SIGNATURES.png)) return true;

    // Check JPEG signature
    if (fd.subarray(0, 3).equals(IMAGE_SIGNATURES.jpg)) return true;

    // Check WebP signature (RIFF....WEBP)
    if (fd.subarray(0, 4).equals(IMAGE_SIGNATURES.webp) && fd.subarray(8, 12).toString() === "WEBP") return true;

    return false;
  } catch {
    return false;
  }
}

/**
 * Recursively find all image files in a directory
 */
function findImageFiles(dir, images = []) {
  if (!existsSync(dir)) {
    return images;
  }

  const entries = readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = join(dir, entry.name);

    if (entry.isDirectory()) {
      findImageFiles(fullPath, images);
    } else if (entry.isFile()) {
      const ext = extname(entry.name).toLowerCase();
      if (IMAGE_EXTENSIONS.includes(ext)) {
        const stats = statSync(fullPath);
        if (stats.size >= MIN_IMAGE_SIZE) {
          // For .dat files, verify they're actually images
          if (ext === ".dat" && !isImageFile(fullPath)) {
            continue;
          }
          images.push({
            path: fullPath,
            relativePath: relative(REPORT_DIR, fullPath),
            name: entry.name,
            size: stats.size,
          });
        }
      }
    }
  }

  return images;
}

/**
 * Compute SHA256 hash of a file
 */
function computeFileHash(filePath) {
  const content = readFileSync(filePath);
  return createHash("sha256").update(content).digest("hex");
}

/**
 * Parse Playwright report data to extract test metadata
 */
function parseReportData() {
  const testMetadata = new Map();
  const dataDir = join(REPORT_DIR, "data");

  if (!existsSync(dataDir)) {
    console.log("⚠️  No data directory found in report");
    return testMetadata;
  }

  const dataFiles = readdirSync(dataDir).filter((f) => f.endsWith(".json") || f.endsWith(".zip"));

  for (const file of dataFiles) {
    try {
      const filePath = join(dataDir, file);

      // Skip zip files, only process JSON
      if (file.endsWith(".zip")) continue;

      const content = readFileSync(filePath, "utf-8");
      const data = JSON.parse(content);

      // Extract attachment information from test results
      extractAttachmentMetadata(data, testMetadata);
    } catch (err) {
      // Skip files that can't be parsed
    }
  }

  return testMetadata;
}

/**
 * Recursively extract attachment metadata from report data
 */
function extractAttachmentMetadata(data, metadata, context = {}) {
  if (!data || typeof data !== "object") return;

  // Track test context
  if (data.title && data.file) {
    context = {
      ...context,
      testTitle: data.title,
      testFile: data.file,
      fullTitle: data.titlePath ? data.titlePath.join(" > ") : data.title,
    };
  }

  // Handle suites
  if (data.suites && Array.isArray(data.suites)) {
    for (const suite of data.suites) {
      extractAttachmentMetadata(suite, metadata, context);
    }
  }

  // Handle specs
  if (data.specs && Array.isArray(data.specs)) {
    for (const spec of data.specs) {
      extractAttachmentMetadata(spec, metadata, {
        ...context,
        testTitle: spec.title,
        testId: spec.id,
      });
    }
  }

  // Handle tests array
  if (data.tests && Array.isArray(data.tests)) {
    for (const test of data.tests) {
      extractAttachmentMetadata(test, metadata, context);
    }
  }

  // Handle results
  if (data.results && Array.isArray(data.results)) {
    for (const result of data.results) {
      extractAttachmentMetadata(result, metadata, {
        ...context,
        status: result.status,
        duration: result.duration,
        retry: result.retry,
      });
    }
  }

  // Handle attachments
  if (data.attachments && Array.isArray(data.attachments)) {
    for (const attachment of data.attachments) {
      if (attachment.path) {
        const attachmentPath = attachment.path;
        // The path in attachment could be relative or contain hash
        const attachmentName = basename(attachmentPath);

        metadata.set(attachmentName, {
          name: attachment.name,
          contentType: attachment.contentType,
          testTitle: context.testTitle,
          testFile: context.testFile,
          fullTitle: context.fullTitle,
          status: context.status,
          retry: context.retry,
        });

        // Also store by the path if it's a hash-based path
        if (attachmentPath.includes("/")) {
          const pathParts = attachmentPath.split("/");
          const hashName = pathParts[pathParts.length - 1];
          metadata.set(hashName, {
            name: attachment.name,
            contentType: attachment.contentType,
            testTitle: context.testTitle,
            testFile: context.testFile,
            fullTitle: context.fullTitle,
            status: context.status,
            retry: context.retry,
          });
        }
      }
    }
  }
}

/**
 * Find duplicates by comparing hashes
 */
function findDuplicates(images) {
  const hashMap = new Map();
  const duplicates = [];

  for (const image of images) {
    const hash = computeFileHash(image.path);
    image.hash = hash;

    if (hashMap.has(hash)) {
      const existing = hashMap.get(hash);

      // Check if this hash already has duplicates recorded
      const existingDupe = duplicates.find((d) => d.hash === hash);
      if (existingDupe) {
        existingDupe.images.push(image);
      } else {
        duplicates.push({
          hash,
          images: [existing, image],
        });
      }
    } else {
      hashMap.set(hash, image);
    }
  }

  return duplicates;
}

/**
 * Format duplicate report with detailed information
 */
function formatDuplicateReport(duplicates, testMetadata) {
  const lines = [];

  lines.push("");
  lines.push("╔════════════════════════════════════════════════════════════════════╗");
  lines.push("║          🚨 DUPLICATE SCREENSHOTS DETECTED 🚨                      ║");
  lines.push("╚════════════════════════════════════════════════════════════════════╝");
  lines.push("");

  for (let i = 0; i < duplicates.length; i++) {
    const dupe = duplicates[i];

    lines.push(`┌─────────────────────────────────────────────────────────────────────┐`);
    lines.push(`│ Duplicate Group ${i + 1} of ${duplicates.length}`);
    lines.push(`│ Hash: ${dupe.hash.substring(0, 16)}...`);
    lines.push(`│ Image count: ${dupe.images.length} identical images`);
    lines.push(`├─────────────────────────────────────────────────────────────────────┤`);

    for (let j = 0; j < dupe.images.length; j++) {
      const img = dupe.images[j];
      const meta = testMetadata.get(img.name) || {};

      lines.push(`│`);
      lines.push(`│ 📸 Image ${j + 1}:`);
      lines.push(`│   File: ${img.relativePath}`);
      lines.push(`│   Size: ${(img.size / 1024).toFixed(2)} KB`);

      if (meta.name) {
        lines.push(`│   Screenshot Name: ${meta.name}`);
      }
      if (meta.fullTitle) {
        lines.push(`│   Test: ${meta.fullTitle}`);
      } else if (meta.testTitle) {
        lines.push(`│   Test: ${meta.testTitle}`);
      }
      if (meta.testFile) {
        lines.push(`│   Test File: ${meta.testFile}`);
      }
      if (meta.status) {
        lines.push(`│   Status: ${meta.status}`);
      }
      if (meta.retry !== undefined && meta.retry > 0) {
        lines.push(`│   Retry: ${meta.retry}`);
      }
    }

    lines.push(`└─────────────────────────────────────────────────────────────────────┘`);
    lines.push("");
  }

  lines.push("═══════════════════════════════════════════════════════════════════════");
  lines.push("");
  lines.push("⚠️  Duplicate screenshots may indicate:");
  lines.push("   • Tests that are not properly interacting with the UI");
  lines.push("   • Screenshots taken at wrong timing (before state changes)");
  lines.push("   • Missing test assertions or actions");
  lines.push("   • Flaky tests that need investigation");
  lines.push("");
  lines.push("💡 Recommended actions:");
  lines.push("   1. Review the tests taking these screenshots");
  lines.push("   2. Ensure proper waitFor* calls before screenshots");
  lines.push("   3. Verify UI state changes are being captured correctly");
  lines.push("");
  lines.push("═══════════════════════════════════════════════════════════════════════");

  return lines.join("\n");
}

/**
 * Main function
 */
function main() {
  console.log("🔍 Checking for duplicate screenshots in Playwright report...");
  console.log(`📁 Report directory: ${REPORT_DIR}`);
  console.log("");

  // Check if report directory exists
  if (!existsSync(REPORT_DIR)) {
    console.log("⚠️  Report directory does not exist. Skipping duplicate check.");
    console.log("   This is expected if no tests have been run yet.");
    process.exit(0);
  }

  // Find all images
  const images = findImageFiles(REPORT_DIR);
  console.log(`📊 Found ${images.length} images in report`);

  if (images.length === 0) {
    console.log("✅ No images found to check. Exiting.");
    process.exit(0);
  }

  // Parse test metadata
  const testMetadata = parseReportData();
  console.log(`📋 Extracted metadata for ${testMetadata.size} attachments`);

  // Find duplicates
  const duplicates = findDuplicates(images);

  if (duplicates.length === 0) {
    console.log("");
    console.log("✅ No duplicate screenshots detected!");
    console.log("   All images in the report are unique.");
    process.exit(0);
  }

  // Report duplicates
  const totalDuplicateImages = duplicates.reduce((sum, d) => sum + d.images.length, 0);

  console.log("");
  console.error(formatDuplicateReport(duplicates, testMetadata));

  console.log("");
  console.log(`❌ FAILED: Found ${duplicates.length} group(s) of duplicate screenshots`);
  console.log(`   Total duplicate images: ${totalDuplicateImages}`);
  console.log("");

  // Exit with error code
  process.exit(1);
}

// Run
main();
