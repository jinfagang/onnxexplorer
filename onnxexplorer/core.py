"""

Core of onnxexplorer

"""
import onnxruntime as ort
from onnx import AttributeProto, TensorProto, GraphProto, ModelProto, NodeProto
from typing import Optional, cast, Text, IO
from google import protobuf
from colorama import init, Fore, Style, Back
import os
import sys
import numpy as np
from tabulate import tabulate


def load_onnx_model(f, proto):
    s = None
    if hasattr(f, 'read') and callable(cast(IO[bytes], f).read):
        s = cast(IO[bytes], f).read()
    else:
        with open(cast(Text, f), 'rb') as readable:
            s = readable.read()
    decoded = cast(Optional[int], proto.ParseFromString(s))
    if decoded is not None and decoded != len(s):
        raise protobuf.message.DecodeError(
            "Protobuf decoding consumed too few bytes: {} out of {}".format(
                decoded, len(s)))
    return proto


def search_nodes_by_type(model, type_name):
    """
    search all nodes that with Type
    :param model_proto:
    :param type_name:
    :return:
    """
    print(Style.BRIGHT + 'search node by op type: ' +
          Style.RESET_ALL + Fore.GREEN + type_name + Style.RESET_ALL)
    if isinstance(model, ModelProto):
        graph = model.graph
        i = 0
        for node in graph.node:
            if type_name in node.op_type:
                i += 1
                print(node)
        print(Style.BRIGHT + 'listed all {} {} nodes in detail.\n'.format(i,
                                                                          type_name) + Style.RESET_ALL)


def list_nodes(model):
    """
    print out all nodes
    :param model_proto:
    :return:
    """
    print(Style.BRIGHT + 'start list nodes names:' + Style.RESET_ALL)
    if isinstance(model, ModelProto):
        graph = model.graph
        i = 0
        for node in graph.node:
            i += 1
            print('{}. {}'.format(i, node.name))
        print(Style.BRIGHT + 'listed all {} nodes names.\n'.format(i) + Style.RESET_ALL)


def list_nodes_hl(model):
    print(Style.BRIGHT + 'start list nodes all:' + Style.RESET_ALL)
    if isinstance(model, ModelProto):
        graph = model.graph
        i = 0
        for node in graph.node:
            if len(node.attribute) > 0 and node.attribute[0].t.raw_data != None:
                data_type = node.attribute[0].t.data_type
                if data_type == 7:
                    raw_data = np.frombuffer(
                        node.attribute[0].t.raw_data, dtype=np.int64)
                elif data_type == 1:
                    raw_data = np.frombuffer(
                        node.attribute[0].t.raw_data, dtype=np.float32)
                else:
                    raw_data = np.frombuffer(
                        node.attribute[0].t.raw_data, dtype=np.int64)
                print('|raw data that encoded inside this node: {}|'.format(raw_data))
            print(node)
            i += 1
        print(Style.BRIGHT +
              'listed all {} nodes in detail.\n'.format(i) + Style.RESET_ALL)


def search_node_by_id(model, node_id):
    """
    print out specific node by ID
    :param model_proto:
    :param node_id:
    :return:
    """
    print(Style.BRIGHT + 'search node by ID: ' +
          Style.RESET_ALL + Fore.GREEN + node_id + Style.RESET_ALL)
    if isinstance(model, ModelProto):
        graph = model.graph
        i = 0
        for node in graph.node:
            if node_id in node.name:
                i += 1
                print(node)
        print(Style.BRIGHT +
              'listed all {} nodes in detail.\n'.format(i) + Style.RESET_ALL)


def get_all_used_op_types(model):
    if isinstance(model, ModelProto):
        graph = model.graph
        all_op_types = {}
        for node in graph.node:
            if node.op_type not in all_op_types.keys():
                all_op_types[node.op_type] = 1
            else:
                all_op_types[node.op_type] += 1
    return all_op_types


def summary(model_proto, model_p):
    if isinstance(model_proto, ModelProto):
        print(Fore.WHITE + Style.BRIGHT + 'ONNX model sum on: ' +
              Style.RESET_ALL + os.path.basename(model_p))
        print('\n')
        print('-------------------------------------------')
        print('ir version: {}'.format(model_proto.ir_version))

        for opi in model_proto.opset_import:
            print('opset_import: {} {}'.format(opi.version, opi.domain))
        print('producer_name: {}'.format(model_proto.producer_name))
        print('doc_string: {}'.format(model_proto.doc_string))
        all_ops = get_all_used_op_types(model_proto)
        print('all ops used: {}'.format(','.join(all_ops.keys())))
        print('-------------------------------------------\n')

        # using table to show
        stat_data = []
        a_nodes = 0
        for k, v in all_ops.items():
            stat_data.append([k, v])
            a_nodes += v
        print('\nStatistic table: ')
        print(tabulate(stat_data, headers=[
              'Op Name', 'Number'], tablefmt="grid"))
        print('Total {} kinds ops, {} nodes.'.format(len(stat_data), a_nodes))
