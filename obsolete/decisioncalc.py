
"""

"""

import random
import pandas

####################################################################################################

def main():

    consider = {
        'price': {
            'type': 'numerical',
            'scale_to': [0.00, 100.00],
            'scale_from': [1.00, 0.80],
            'bias_point': 0,
            'bias_value': 0,
            'weight': 0.50,
        },
        'appearance': {
            'type': 'numerical',
            'scale_to': [0.00, 100.00],
            'scale_from': [0.00, 1.00],
            'bias_point': +50.00,
            'bias_value': 0.80,
            'weight': 0.50,
        }
    }

    calc = DecisionCalculator(consider)

    # Get apple_options
    apple_options = []
    num_of_apples = 10
    prices = [1.00, 0.90, 0.80]
    price_weights = [0.50, 0.25, 0.25]
    appearance_weight = 1.0
    for i in range(num_of_apples):
        apple = {}
        apple['name'] = f'apple{i:02d}'
        apple['price'] = random.choices(prices, weights=price_weights)[0]
        apple['appearance'] = 1 - (random.random() ** appearance_weight)
        apple_options += [ apple ]

    # apple_options = [
    #     {'price': 0.00, 'appearance': 0.00},
    #     {'price': 0.20, 'appearance': 0.20},
    #     {'price': 0.40, 'appearance': 0.40},
    #     {'price': 0.60, 'appearance': 0.60},
    #     {'price': 0.80, 'appearance': 0.80},
    #     {'price': 1.00, 'appearance': 1.00},
    # ]

    decision = calc.getDecisionMatrix(apple_options)

    print(pandas.DataFrame(decision))

    exit()

####################################################################################################



class DecisionCalculator:
    def __init__(self, consider={}):
        self.consider = {}
        self.setConsider(consider)
        self.calibrateWeights()



    def setConsider(self, consider):
        for id, considering in consider.items():
            considering = {**{'id': id}, **considering}
            self.consider[id] = Consider(self, **considering)



    def calibrateWeights(self):
        calibration = 1.00 / sum([ c.weight for c in self.consider.values() ])
        for id, considering in self.consider.items():
            self.consider[id].weight = considering.weight * calibration



    def getDecisionMatrix(self, options):
        decision_matrix = []
        for option in options:
            for id, considering in self.consider.items():
                option[f'{id}_score'] = considering.getScore(option[id])
            option['total_score'] = sum([ v for k, v in option.items() if k.endswith('score') ])
            decision_matrix += [ option ]
        decision_matrix = sorted(decision_matrix, key=lambda x: x['total_score'], reverse=True)
        return decision_matrix



####################################################################################################



class Consider:
    def __init__(
        self, calculator, id='', type='', scale_to=[], scale_from=[], bias_point=0, bias_value=0,
        weight=0
    ):
        """
        types:  'categorical', 'numerical'
        """
        self.calculator = calculator
        self.id = id
        self.type = type
        self.scale_to = scale_to
        self.scale_from = scale_from
        self.bias_point = bias_point
        self.bias_value = bias_value
        self.weight = weight



    def getScore(self, value):
        value = self.applyScaleToValue(value)
        value = self.applyBiasToValue(value)
        value = self.applyClampToValue(value)
        value = self.applyWeightToValue(value)
        return value



    # def getScoreDict(self, value):
    #     score_dict = {}
    #     score_dict['to_scale'] = self.applyScaleToValue(value)
    #     score_dict['with_bias'] = self.applyBiasToValue(score_dict['to_scale'])
    #     score_dict['clamped'] = self.applyClampToValue(score_dict['with_bias'])
    #     score_dict['weighted'] = self.applyWeightToValue(score_dict['clamped'])
    #     return score_dict



    def applyScaleToValue(self, value):
        to_scale = value - self.scale_from[0]
        adjust = self.scale_to[1] / (self.scale_from[1] - self.scale_from[0])
        return abs(to_scale * adjust)



    def applyBiasToValue(self, value):
        with_bias = value
        if self.bias_point:
            bias_less_than = self.bias_point < 0 and value < abs(self.bias_point)
            bias_greater_than = self.bias_point > 0 and value > abs(self.bias_point)
            if bias_less_than or bias_greater_than:  with_bias = value ** self.bias_value
        return with_bias



    def applyClampToValue(self, value):
        return max(self.scale_to[0], min(self.scale_to[1], value))



    def applyWeightToValue(self, value):
        return value * self.weight



####################################################################################################

main()

####################################################################################################



# """ EXAMPLE:  selecting best apple """
#
# # CALIBRATION FUNCTION
# global_low, global_high = 0.00, 100.00
# low, high = 2.0, 12.0
# nums = [2, 3, 5, 6, 9, 10.45]
# bias_point, bias_value = 50.0, 1.01
#
# def calibrate(num, low, high):
#     global global_low, global_high
#     num = num - low
#     transition = global_high / (high - low)
#     num = num * transition
#     if num > bias_point:  num = num ** bias_value
#     num = max(global_low, min(global_high, num))
#     return num
#     # return max(global_low, min(global_high, (num - low) * (global_high / (high - low))))
#
# calibrated = [ calibrate(num, low, high) for num in nums ]



# # get apples sample data
# apples = []
# num_of_apples = 10
# prices = [1.00, 0.90, 0.80]
# price_weights = [0.50, 0.25, 0.25]
# appearance_weight = 1.2
# for i in range(num_of_apples):
#     apple = {}
#     apple['name'] = f'apple{i:02d}'
#     apple['price'] = random.choices(prices, weights=price_weights)[0]
#     apple['appearance'] = 1 - (random.random() ** appearance_weight)
#     apples += [ apple ]



# print(f'global_low = {global_low} | global_high = {global_high}')
# print(f'       low = {low} |        high = {high}')
# for i, num in enumerate(nums):  print(f'{num:05.2f} ... {calibrated[i]:06.2f}')



# print(working_nums)
# print(next_working_nums)



# apples = sorted(apples, key=lambda x: x['price'], reverse=True)
# apples = sorted(apples, key=lambda x: x['appearance'], reverse=True)
# for apple in apples:
#     print('%s %07.5f' % (apple['price'], apple['appearance']))



# import pandas
# decision = pandas.DataFrame(calc.decide(apples)).sort_values(by='total_score', ascending=False)
# print(decision)



# for row in decision:  print(row)



# print(json.dumps(calc.factors, sort_keys=True, indent=4))
