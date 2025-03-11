# Создаем основную структуру каталогов
mkdir -p crates/{tjorn-core,tjorn-gui,tjorn-audio,tjorn-network,tjorn-security,tjorn-ai,tjorn-fs,tjorn-db,tjorn-virtualization,tjorn-containers,tjorn-drivers,tjorn-debug,tjorn-protocols,tjorn-crypto,tjorn-monitoring,tjorn-memory,tjorn-ai-ml,tjorn-vision,tjorn-speech,tjorn-physics,tjorn-render,tjorn-resources,tjorn-formats,tjorn-compression,tjorn-multimedia,tjorn-text}

# Создаем базовый Cargo.toml для каждого крейта
for crate in crates/*; do
    echo "[package]
name = \"$(basename $crate)\"
version = \"0.1.0\"
edition = \"2021\"
authors = [\"TjornOS Team\"]

[dependencies]
" > "$crate/Cargo.toml"

    # Создаем базовую структуру исходников
    mkdir -p "$crate/src"
    echo "pub fn init() {
    println!(\"Initializing {}\", \"$(basename $crate)\");
}" > "$crate/src/lib.rs"
done 