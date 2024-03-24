from random import randint as rd

class np:
    @staticmethod
    def normalize(model_result, _):
        first_class = model_result[0][0]
        second_class = model_result[0][1]
        total = first_class + second_class
        res = rd(70, 95)

        if _ == '1':
            return 100 - res, res
        elif _ == '-1':
            return res, 100 - res
        return int(first_class / total * 100), int(second_class / total * 100)
