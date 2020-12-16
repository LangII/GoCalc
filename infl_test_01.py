
import random
import pandas
from copy import deepcopy

from calculate.calcfuncs import applyScale, applySkew, applyClamp

GLOBAL_MIN = 0.0
GLOBAL_MAX = 100.0

CALIBRATOR = None
CALIBRATIONS = {}

GENERATOR = None

CONTROLLERS = {}
RAW_NODES = [{}]
NODES = {}

TITANIC_TARGETS = pandas.read_csv('https://storage.googleapis.com/tf-datasets/titanic/train.csv')
print(TITANIC_TARGETS.columns)
exit()

####################################################################################################

def main():

    global GLOBAL_MIN, GLOBAL_MAX, CALIBRATOR, CALIBRATIONS, GENERATOR, CONTROLLERS, RAW_NODES
    global NODES

    CALIBRATOR = Calibrator()
    GENERATOR = Generator()

    """'''''''''''''''''''''''''
    '''   CREATE RAW NODES   '''
    '''''''''''''''''''''''''"""
    RAW_NODES[0]['sex_factor'] = FactorNode(name='sex_factor', ref='sex', output=0.0)
    RAW_NODES[0]['age_factor'] = FactorNode(name='age_factor', ref='age', output=0.0)
    RAW_NODES[0]['nfamily_factor'] = FactorNode(name='nfamily_factor', ref='nfamily', output=0.0)
    RAW_NODES[0]['parch_factor'] = FactorNode(name='parch_factor', ref='parch', output=0.0)
    RAW_NODES[0]['fare_factor'] = FactorNode(name='fare_factor', ref='fare', output=0.0)
    RAW_NODES[0]['class_factor'] = FactorNode(name='class_factor', ref='class', output=0.0)
    RAW_NODES[0]['deck_factor'] = FactorNode(name='deck_factor', ref='deck', output=0.0)
    RAW_NODES[0]['embark_factor'] = FactorNode(name='embark_factor', ref='embark', output=0.0)
    RAW_NODES[0]['alone_factor'] = FactorNode(name='alone_factor', ref='alone', output=0.0)
    RAW_NODES += [{}] # Create a new RAW_NODES layer.
    RAW_NODES[1]['price_scale'] = ScaleNode(
        name='price_scale',
        ref='price',
        input_nodes='price_factor',
        scale_from_min=1.00,
        scale_from_max=0.10
    )
    RAW_NODES[1]['looks_scale'] = ScaleNode(
        name='looks_scale',
        ref='looks',
        input_nodes='looks_factor',
        scale_from_min=0.0,
        scale_from_max=10.0
    )
    RAW_NODES[1]['size_scale'] = ScaleNode(
        name='size_scale',
        ref='size',
        input_nodes='size_factor',
        scale_from_min=0.0,
        scale_from_max=10.0
    )

    """'''''''''''''''''''''''''''''''''''''
    '''   CREATE CONTROLLERS AND NODES   '''
    '''''''''''''''''''''''''''''''''''''"""
    CONTROLLERS['PLS_infl'] = InflCtrl(
        name='PLS_infl',
        ref='PLS',
        infls=['price', 'looks', 'size']
    )
    NODES['PLS_infl'] = InflNode(
        name='PLS_infl',
        ref='PLS',
        input_nodes=['price_scale', 'looks_scale', 'size_scale'],
        controllers='PLS_infl',
    )

    """'''''''''''''''''''''''''''''''
    '''   GENERATE AND CALIBRATE   '''
    '''''''''''''''''''''''''''''''"""
    GENERATOR.genAllRawNodeOutputs() # generate all raw node outputs.
    CALIBRATOR.regenNodeCtrlOutputs('PLS_infl') # Calibrate 'PLS_infl' node control outputs.
    NODES['PLS_infl'].genOutput() # Generate 'PLS_infl' node output.


    """''''''''''''''''''''''
    '''   PRINT REPORTS   '''
    ''''''''''''''''''''''"""
    NODES['PLS_infl'].printOutput()

    """'''''''''''''''''''''''''''
    '''   UNDER CONSTRUCTION   '''
    '''''''''''''''''''''''''''"""
    print("\nUNDER CONSTRUCTION\n")
    CALIBRATOR.loadNodeCalibrations(node=NODES['PLS_infl'], targets=APPLE_TARGET_OPTIONS)
    for cal in CALIBRATIONS.items():  print(cal)

    exit()

####################################################################################################

class Calibrator:
    def __init__(self):
        pass

    def regenCtrlOutput(self, ctrl):
        if isinstance(ctrl, str):  ctrl = CONTROLLERS[ctrl]
        ctrl.calOutput()

    def regenNodeCtrlOutputs(self, node):
        if isinstance(node, str):  node = NODES[node]
        for ctrl in node.controllers.values():  ctrl.regenOutput()

    def regenAllCtrlOutputs(self):
        for ctrl in CONTROLLERS.values():  ctrl.regenOutput()

    """'''''''''''''''''''''''''''
    '''   UNDER CONSTRUCTION   '''
    '''''''''''''''''''''''''''"""
    def loadNodeCalibrations(self, node=None, targets=[], iter=100):

        global CALIBRATIONS

        """ Prep CALIBRATIONS. """
        for ctrl_name in node.controllers.keys():
            if ctrl_name not in CALIBRATIONS.keys():
                if ctrl_name.endswith('_infl'):
                    for infl in CONTROLLERS[ctrl_name].infls:
                        CALIBRATIONS[f"{ctrl_name}_{infl}"] = []
                else:
                    CALIBRATIONS[ctrl_name] = []

        """ Loop through each target. """
        targets_tbl = []
        for target in targets:

            """ Update FactorNode outputs (associated with node). """
            for factor, factor_value in target.items():  RAW_NODES[0][factor].output = factor_value

            """ Update all raw node outputs. """
            GENERATOR.genAllRawNodeOutputs()
            # GENERATOR.printAllRawNodeOutputs()

            """ Loop through calibration iterations. """
            cal_iter_tbl = []
            for i in range(iter):
                self.regenNodeCtrlOutputs(node)
                node.genOutput()
                output_row = {}
                for ctrl_name, ctrl in node.controllers.items():
                    # print(ctrl.output)
                    output_row[ctrl_name] = deepcopy(ctrl.output)

                output_row['node_output'] = node.output
                cal_iter_tbl += [ output_row ]
            cal_iter_tbl = sorted(cal_iter_tbl, key=lambda x: x['node_output'], reverse=True)
            # for row in cal_iter_tbl:  print(row)

            best_cal_iter = cal_iter_tbl[0]
            targets_tbl += [best_cal_iter]

            # print(best_cal_iter)
            del best_cal_iter['node_output']

            """ Load CALIBRATIONS. """
            for ctrl_name, cal in best_cal_iter.items():
                if ctrl_name.endswith('_infl'):
                    for infl in CONTROLLERS[ctrl_name].infls:
                        CALIBRATIONS[f"{ctrl_name}_{infl}"] += [ cal[infl] ]
                else:
                    CALIBRATIONS[ctrl_name] += [ cal ]

            # print(CALIBRATIONS)

        # for row in targets_tbl:  print(row)
        # print("iter =", iter)

        # exit()
    """'''''''''''''''''''''''''''
    '''   UNDER CONSTRUCTION   '''
    '''''''''''''''''''''''''''"""

####################################################################################################

class Generator:
    def __init__(self):
        pass

    def genNodeOutput(self, node):
        node.genOutput()

    def genAllRawNodeOutputs(self):
        for node_layer in RAW_NODES:
            for node in node_layer.values():  node.genOutput()

    def printAllRawNodeOutputs(self):
        print_tbl = []
        for layer_i, node_layer in enumerate(RAW_NODES):
            for node in node_layer.values():
                print_tbl += [ { 'layer': layer_i, 'node': node, 'output': node.output } ]
        print("\nraw node outputs:")
        print(pandas.DataFrame(print_tbl).to_string(index=False))

####################################################################################################

class Controller:
    def __init__(self, name='', ref='', output=GLOBAL_MIN):
        self.name = name
        self.ref = ref
        self.output = output

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"



class NumCtrl (Controller):
    def __init__(self, output_min=GLOBAL_MIN, output_max=GLOBAL_MAX, **kwargs):
        super(NumCtrl, self).__init__(**kwargs)
        self.output_min = output_min
        self.output_max = output_max

    def regenOutput(self):
        self.output = random.uniform(self.output_min, self.output_max)



class InflCtrl (NumCtrl):
    def __init__(self, infls=[], **kwargs):
        super(InflCtrl, self).__init__(**kwargs)
        self.infls = infls
        self.int_ctrls = self.initIntCtrls() # InflCtrl requires private internal Controllers.
        self.output = self.initOutput()

    def initIntCtrls(self):
        int_ctrls_ = {}
        for infl in self.infls:
            int_ctrls_[infl] = NumCtrl(
                name=f"{infl}_{self.name}intctrl",
                output_min=self.output_min,
                output_max=self.output_max
            )
        return int_ctrls_

    def initOutput(self):
        return { infl: self.output_min for infl in self.infls }

    def regenIntCtrlOutputs(self):
        for int_ctrl in self.int_ctrls.values():  int_ctrl.regenOutput()

    def regenOutput(self):
        self.regenIntCtrlOutputs()
        trans = self.output_max / sum([ int_ctrl.output for int_ctrl in self.int_ctrls.values() ])
        for name in self.infls:
            self.output[name] = self.int_ctrls[name].output * trans

    def printOutput(self):
        print(f"\n{self} output:")
        print(pandas.DataFrame([self.output]).to_string(index=False))

####################################################################################################

class Node:
    def __init__(self, name='', ref='', input_nodes=[], controllers=[], output=GLOBAL_MIN):
        self.name = name
        self.ref = ref
        self.input_nodes = self.initInputNodes(input_nodes)
        self.controllers = self.initControllers(controllers)
        self.output = output

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def initInputNodes(self, input_nodes):
        if not input_nodes:  return input_nodes
        if isinstance(input_nodes, str):  input_nodes = [input_nodes]
        input_nodes_ = {}
        for input_node in input_nodes:
            for layer in range(len(RAW_NODES)):
                for raw_node_name, raw_node in RAW_NODES[layer].items():
                    if input_node == raw_node_name:  input_nodes_[raw_node_name] = raw_node
        return input_nodes_

    def initControllers(self, controllers):
        if not controllers:  return controllers
        if isinstance(controllers, str):  controllers = [controllers]
        return { ctrl: CONTROLLERS[ctrl] for ctrl in controllers }

    def getRootName(self, name=''):
        if not name:  name = self.name
        if '_' not in name:  return name
        else:  return name[:name.rfind('_')]

    def getInputNodeByRootName(self, root_name):
        for input_node in self.input_nodes.values():
            if input_node.name.startswith(root_name):  return input_node

    def getInputNodesRootNames(self):
        return [ self.getRootName(name) for name in self.input_nodes.keys() ]



class FactorNode (Node):
    def __init__(self, **kwargs):
        super(FactorNode, self).__init__(**kwargs)

    def genOutput(self):
        """ Need to setup extraction of environmental input data (options). """
        return



class ScaleNode (Node):
    def __init__(
        self, scale_from_min=0.0, scale_from_max=0.0, scale_to_min=GLOBAL_MIN,
        scale_to_max=GLOBAL_MAX, **kwargs
    ):
        super(ScaleNode, self).__init__(**kwargs)
        self.scale_from_min = scale_from_min
        self.scale_from_max = scale_from_max
        self.scale_to_min = scale_to_min
        self.scale_to_max = scale_to_max

        if len(self.input_nodes) > 1:  exit("ScaleNode.input_nodes only accepts 1 node.")

    def genOutput(self):
        input_node_output = list(self.input_nodes.values())[0].output
        self.output = applyScale(
            input_node_output,
            [self.scale_from_min, self.scale_from_max],
            [self.scale_to_min, self.scale_to_max]
        )



class InflNode (Node):
    def __init__(self, output_min=GLOBAL_MIN, output_max=GLOBAL_MAX, **kwargs):
        super(InflNode, self).__init__(**kwargs)
        self.output_min = output_min
        self.output_max = output_max
        self.scores = self.initScores()

    def initScores(self):
        return { node.getRootName(): self.output_min for node in self.input_nodes.values() }

    def genScores(self):
        ctrl = list(self.controllers.values())[0]
        for input_node in self.input_nodes.values():
            root_name = input_node.getRootName()
            score_mult = ctrl.output[root_name] / self.output_max
            self.scores[root_name] = input_node.output * score_mult

    def genOutput(self):
        self.genScores()
        self.output = sum(list(self.scores.values()))

    def printOutput(self):
        print_tbl = []
        for input_node in self.input_nodes.values():
            root_name = self.getRootName(input_node.name)
            print_tbl += [ {
                'root_name': root_name,
                'input_node_values':  input_node.output,
                'ctrl_infl':  list(self.controllers.values())[0].output[root_name],
                'scores':  self.scores[root_name],
            } ]
        print(f"\n{self} output report:")
        print(pandas.DataFrame(print_tbl).to_string(index=False))
        print(f"output: {self.output}")


    # def printInflReport(self):
    #     print_tbl = []
    #     for input_node in self.input_nodes.values():
    #         root_name = self.getRootName(input_node.name)
    #         print_tbl += [ {
    #             'root_name': root_name,
    #             'input_node_output':  input_node.output,
    #             'infl_value':  self.all_infl_values[root_name],
    #             'output_value': self.all_output_values[root_name],
    #         } ]
    #     print(f"\n{self} influence report:")
    #     print(pandas.DataFrame(print_tbl).to_string(index=False))
    #     print("output =", self.output)

####################################################################################################

main()

####################################################################################################

""" main() """
# pls_infl_node.regenInflValues()
#
# print([ var.value for var in pls_infl_node.variables.values() ])
# print(sum([ var.value for var in pls_infl_node.variables.values() ]))
#
# new_values = [ random.uniform(0.0, 100.0) for _ in range(5) ]
# trans = 100.0 / sum(new_values)
# new_values = [ x * trans for x in new_values ]
# print(new_values)
# print(sum(new_values))
#
# print_rows = []
# for i in range(10):
#     var_dict = {}
#     for name, var in VARIABLES.items():
#         var.regenValue()
#         var_dict[name] = var.value
#     print_rows += [ var_dict ]
# print(pandas.DataFrame(print_rows))

""" Node() """
# def printFacVals(self):
#     if not self.factors:  print(f"\n{self} has no factors") ; return
#     print_tbl = []
#     for fac in self.factors.values():
#         print_tbl += [ {'name': fac.name, 'value': fac.value} ]
#     print(f"\n{self} factors:")
#     print(pandas.DataFrame(print_tbl))
#
# def printCtrlVals(self):
#     if not self.controllers:  print(f"\n{self} has no controllers") ; return
#     print_tbl = []
#     for ctrl in self.controllers.values():
#         print_tbl += [ {
#             'name': ctrl.name, 'value': ctrl.value, 'value_min': ctrl.value_min,
#             'value_max': ctrl.value_max
#         } ]
#     print(f"\n{self} controllers:")
#     print(pandas.DataFrame(print_tbl))
#
# def initFactors(self, factors):
#     return { fac.name: fac for fac in factors }
#
# def initChildren(self, children):
#     return { child.name: child for child in children }

""" main() """
# class Factor:
#     def __init__(self, name, output=GLOBAL_MIN):
#         self.name = name
#         self.output = output
#         FACTORS[self.name] = self

""" InflNode() """
# def genInflueces(self):
#     translator = GLOBAL_MAX / sum([ ctrl.output for ctrl in self.controllers.values() ])
#     for infl_name in self.influences.keys():
#         self.influences[infl_name] = self.controllers[infl_name].output * translator
#
# def genValues(self):
#     for value in self.values.keys():
#         root_name = self.getRootName(value)
#         child_name = f"{root_name}_scl"
#         infl_name = f"{root_name}_infl"
#         infl_temp = self.influences[infl_name] / GLOBAL_MAX
#         self.values[value] = self.children[child_name].output * infl_temp
#
# def genValue(self):
#     self.genInflueces()
#     self.genValues()
#     self.value = sum(self.values.values())

""" Calibrator() """
# print_tbl = []
# for i in range(iter):
#     self.regenNodeCtrlOutputs('PLS_infl')
#     NODES['PLS_infl'].genOutput()
#     print_tbl += [ {
#         'iteration': i + 1,
#         'price_infl_ctrl': CONTROLLERS['PLS_infl'].output['price'],
#         'looks_infl_ctrl': CONTROLLERS['PLS_infl'].output['looks'],
#         'size_infl_ctrl': CONTROLLERS['PLS_infl'].output['size'],
#         'score': node.output
#     } ]
# print_tbl = sorted(print_tbl, key=lambda x: x['score'], reverse=True)
# print("\ncalibration regeneration report:")
# print(pandas.DataFrame(print_tbl).to_string(index=False))
