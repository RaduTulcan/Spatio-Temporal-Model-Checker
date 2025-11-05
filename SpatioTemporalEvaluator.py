from parsers.SpatioTemporalFormulaParser import tokenize, SpatioTemporalParser

if __name__ == '__main__':
    INPUT_FORMULA = "G (a U b)"

    parsed_formula = SpatioTemporalParser(tokenize(INPUT_FORMULA)).parse()

    print(parsed_formula)

