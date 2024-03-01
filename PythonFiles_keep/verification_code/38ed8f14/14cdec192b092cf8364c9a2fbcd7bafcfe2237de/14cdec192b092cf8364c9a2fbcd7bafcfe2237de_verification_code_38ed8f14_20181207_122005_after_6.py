from verifycode.generator import Generator

g = Generator(is_hash_filename=True)
g.generate("123567")
g.save("./testdata")