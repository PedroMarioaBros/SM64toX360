#!/usr/bin/env python3
"""Patch pinned acceleration/xex2 to support Basic-compressed PE replacement.

Design choice for SM64toX360:
- Basic output uses one (data_size, zero_size=0) block.
- This favors correctness and a simple loader contract over file-size savings.
- xex2 still rebuilds page descriptors, image/header hashes and the devkit signature.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / "acceleration"
compress = root / "crates/xex2/src/compress.rs"
assemble = root / "crates/xex2/src/assemble.rs"
rebuild = root / "crates/xex2/src/rebuild.rs"

c = compress.read_text()
needle = """/// Synthesize the FileFormatInfo optional-header blob for an uncompressed
/// stream. Layout: `u32 info_size | u16 encryption_type | u16 compression_type=None`.
pub fn file_format_info_blob_none"""
insert = """/// Synthesize the FileFormatInfo optional-header blob for a Basic-compressed
/// stream containing one literal data block followed by an optional zero fill.
///
/// Layout:
///   u32 info_size | u16 encryption_type | u16 compression_type=Basic
///   | u32 data_size | u32 zero_size
pub fn file_format_info_blob_basic(
    encryption_type: crate::header::EncryptionType,
    data_size: u32,
    zero_size: u32,
) -> Vec<u8> {
    let mut blob = Vec::with_capacity(16);
    blob.extend_from_slice(&16u32.to_be_bytes());
    blob.extend_from_slice(&(encryption_type as u16).to_be_bytes());
    blob.extend_from_slice(&(crate::header::CompressionType::Basic as u16).to_be_bytes());
    blob.extend_from_slice(&data_size.to_be_bytes());
    blob.extend_from_slice(&zero_size.to_be_bytes());
    blob
}

/// Synthesize the FileFormatInfo optional-header blob for an uncompressed
/// stream. Layout: `u32 info_size | u16 encryption_type | u16 compression_type=None`.
pub fn file_format_info_blob_none"""
if needle not in c:
    raise SystemExit("compress.rs insertion point not found")
compress.write_text(c.replace(needle, insert, 1))

a = assemble.read_text()
old = """		TargetCompression::Basic => {
			return Err(Xex2Error::RebuildTransformNotImplemented.into_report());
		}
"""
new = """		TargetCompression::Basic => {
			// A single literal block is valid Basic compression and is ideal for
			// deterministic replacement of the already-mapped SM64 basefile.
			let blob = compress::file_format_info_blob_basic(encryption, image_size, 0);
			let data = match session_key {
				Some(key) => crate::crypto::encrypt_data(&pe, &key),
				None => pe,
			};
			(data, blob)
		}
"""
if old not in a:
    raise SystemExit("assemble.rs Basic arm not found")
assemble.write_text(a.replace(old, new, 1))

r = rebuild.read_text()
start = r.index("	pub fn is_supported(&self) -> bool {")
end = r.index("\n\t/// Produce the", start)
replacement = """	pub fn is_supported(&self) -> bool {
		// Basic compression is supported by the SM64toX360 extension using a
		// deterministic single literal block. Delta/XEXP remains unsupported.
		if let Ok(ff) = self.xex.header.file_format_info() {
			if ff.compression_type == crate::header::CompressionType::Delta {
				return false;
			}
		}
		true
	}
"""
rebuild.write_text(r[:start] + replacement + r[end:])

print("Patched acceleration/xex2 for Basic PE replacement")
