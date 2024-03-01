from utf8_codepoint import CodePoint

# unicode symbol for European currency
euro_money = "U+20AC"

# create instance object
cp = CodePoint(euro_money)

# get representation integer of the Unicode Code Point
print(cp.to_int())
print(cp.to_hex())
print(cp.to_string())
print(cp.to_list())


#cp.bprint()

print(cp.get_all(True))
