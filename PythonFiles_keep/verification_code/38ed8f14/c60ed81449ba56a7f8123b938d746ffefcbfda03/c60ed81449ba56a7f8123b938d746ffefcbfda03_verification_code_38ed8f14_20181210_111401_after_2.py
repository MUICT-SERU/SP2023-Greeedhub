from verifycode.generator import Generator

g = Generator(is_hash_filename=True, width=200, height=80, fonttype="fonts/Courier.dfont", fontsize=60)
g.generate("123567")
g.save("./testdata")

# g2 = Generator(fonttype="fonts/STHeiti Light.ttc")
# g.generate("123566")
# g.save("./testdata")