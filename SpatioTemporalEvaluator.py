from parsers.SpatioTemporalFormulaParser import tokenize, SpatioTemporalParser
import copy


def generate_trace(trace_model, grid_size):
    empty_grid = [[[] for _ in range(0, grid_size[1])] for _ in range(0, grid_size[0])]
    trace_length = len(trace_model[0][0].split(";"))

    trace = [copy.deepcopy(empty_grid) for _ in range(0, trace_length)]

    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            point_time_evolution = trace_model[i][j].split(";")

            for k in range(0, trace_length):
                if point_time_evolution[k] == "":
                    trace[k][i][j] = []
                else:
                    trace[k][i][j] = point_time_evolution[k].split(",")
    return trace


if __name__ == '__main__':
    INPUT_FORMULA = " G g"
    GRID_SIZE = (3,3)
    TRACE_MODEL =[[";;", "g;g;a,g", ";;"],
            [";;", ";a;b", ";;"],
            [";;", "a;b;", "b;;"]]
    TRACE = generate_trace(TRACE_MODEL, GRID_SIZE)
    POINT = (0,1)

    parsed_formula = SpatioTemporalParser(tokenize(INPUT_FORMULA)).parse()

    print(parsed_formula.evaluate(TRACE, POINT))


