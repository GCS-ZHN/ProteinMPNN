#!/work/home/zhanghongning/software/ProteinMPNN/8907e66/.conda/bin/python3
import argparse
import json

from typing import Iterable

def parse_position_str(position: str) -> list:
    res = []
    for chain_pos in position.split(','):
        chain_pos = chain_pos.strip()
        res.append([])
        for pos in chain_pos.split():
            pos_range = pos.split("-")
            pos_start = int(pos_range[0])
            pos_end = int(pos_range[-1])
            res[-1].extend(range(pos_start, pos_end + 1))
    return res


def read_jsonl(jsonl_path: str) -> Iterable[dict]:
    with open(jsonl_path, 'r') as f:
        for line in f:
            yield json.loads(line)


def query_motif(motif_list, structure_name: str):
    for motif in motif_list:
        if structure_name in motif:
            return {k: list(map(int, v.split(','))) for k, v in motif[structure_name]['motif'].items()}
    return None


def main(args):
    import numpy as np

    json_list = list(read_jsonl(args.input_path))
    motif_list = list(read_jsonl(args.motif)) if args.motif else []
    fixed_list = parse_position_str(args.position_list)
    global_designed_chain_list = [str(item) for item in args.chain_list.split()]
    my_dict = {}
    
    if not args.specify_non_fixed:
        for result in json_list:
            structure_name = result['name']
            motif = query_motif(motif_list, structure_name)
            all_chain_list = [item[-1:] for item in list(result) if item[:9]=='seq_chain']
            fixed_position_dict = {}
            for i, chain in enumerate(global_designed_chain_list):
                fixed_position_dict[chain] = fixed_list[i]
                if motif is not None and chain in motif:
                    fixed_position_dict[chain] += motif[chain]
                    fixed_position_dict[chain] = sorted(list(set(fixed_position_dict[chain])))

            for chain in all_chain_list:
                if chain not in global_designed_chain_list:       
                    fixed_position_dict[chain] = []
            my_dict[result['name']] = fixed_position_dict
    else:
        for result in json_list:
            structure_name = result['name']
            motif = query_motif(motif_list, structure_name)
            all_chain_list = [item[-1:] for item in list(result) if item[:9]=='seq_chain']
            fixed_position_dict = {}   
            for chain in all_chain_list:
                seq_length = len(result[f'seq_chain_{chain}'])
                all_residue_list = (np.arange(seq_length)+1).tolist()
                if chain not in global_designed_chain_list:
                    fixed_position_dict[chain] = all_residue_list
                else:
                    idx = np.argwhere(np.array(global_designed_chain_list) == chain)[0][0]
                    fixed_position_dict[chain] = list(set(all_residue_list)-set(fixed_list[idx]))
                    if motif is not None and chain in motif:
                        fixed_position_dict[chain] += motif[chain]
                        fixed_position_dict[chain] = sorted(list(set(fixed_position_dict[chain])))
            my_dict[result['name']] = fixed_position_dict

    with open(args.output_path, 'w') as f:
        f.write(json.dumps(my_dict) + '\n')

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument("--input_path", type=str, help="Path to the parsed PDBs")
    argparser.add_argument("--output_path", type=str, help="Path to the output dictionary")
    argparser.add_argument("--chain_list", type=str, default='', help="List of the chains that need to be fixed")
    argparser.add_argument("--position_list", type=str, default='', help="Position lists, e.g. 11 12 14 18, 1 2 3 4 for first chain and the second chain")
    argparser.add_argument("--specify_non_fixed", action="store_true", default=False, help="Allows specifying just residues that need to be designed (default: false)")
    argparser.add_argument("--motif", type=str, help="File of motif to be fixed")
    args = argparser.parse_args()
    main(args)

