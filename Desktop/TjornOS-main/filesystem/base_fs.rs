pub struct FileSystem {
    root: Directory,
    current_dir: Directory,
}

impl FileSystem {
    pub fn new() -> Self {
        let root = Directory::new("/");
        FileSystem {
            root: root.clone(),
            current_dir: root,
        }
    }

    pub fn create_file(&mut self, name: &str, content: Vec<u8>) -> Result<(), Error> {
        let file = File::new(name, content);
        self.current_dir.add_file(file)
    }

    pub fn create_directory(&mut self, name: &str) -> Result<(), Error> {
        let dir = Directory::new(name);
        self.current_dir.add_directory(dir)
    }
} 