use std::env;
use std::fs;
use std::fs::File;

use anyhow::{Context, Result};
use xex2::Xex2;
use xex2::writer::TargetCompression;

fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 4 || args.len() > 5 {
        eprintln!("usage: xex2replace <source.xex> <replacement.pe> <output.xex> [basic|normal|none]");
        std::process::exit(2);
    }

    let source = fs::read(&args[1]).context("read source XEX")?;
    let pe = fs::read(&args[2]).context("read replacement PE")?;
    if !pe.starts_with(b"MZ") {
        anyhow::bail!("replacement does not begin with MZ");
    }

    let target = match args.get(4).map(String::as_str).unwrap_or("basic") {
        "basic" => TargetCompression::Basic,
        "normal" => TargetCompression::Normal,
        "none" => TargetCompression::Uncompressed,
        other => anyhow::bail!("unknown target compression: {other}"),
    };

    let xex = Xex2::parse(&source).map_err(|e| anyhow::anyhow!("{e:?}"))?;
    let mut output = File::create(&args[3]).context("create output XEX")?;
    xex.rebuild(&source)
        .target_compression(target)
        .replace_pe(pe)
        .write_to(&mut output)
        .map_err(|e| anyhow::anyhow!("{e:?}"))?;

    Ok(())
}
