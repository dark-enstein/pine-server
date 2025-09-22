import torch
import re

from fuse.data.tokenizers.modular_tokenizer.op import ModularTokenizerOp
from mammal.examples.protein_solubility.task import ProteinSolubilityTask
from mammal.keys import CLS_PRED, SCORES, ENCODER_INPUTS_STR, ENCODER_INPUTS_TOKENS, ENCODER_INPUTS_ATTENTION_MASK
from mammal.model import Mammal
from mammal.examples.carcinogenicity.task import CarcinogenicityTask

import datamodels.pyd_models

class MammalCore:
    def __init__(self):
        """
        Initialize all the model parameters for all the predictions supported
        """
        # self.var_solubility = "solubility"
        # self.var_ppi = "proteinproteininteractions"
        # self.models = self.init_models()
        # self.tokenizers = self.init_tokenizers()

    def init_models(self) -> {}:
        models = {}
        models[self.var_solubility] = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")
        models[self.var_ppi] = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m")

        return models

    def init_tokenizers(self) -> {}:
        tokenizers = {}

        tokenizers[self.var_solubility] = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")
        tokenizers[self.var_ppi] = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m")

        return tokenizers
    def echo(self):
        return "Calling model module"

    def solubility(self, params: datamodels.pyd_models.SolubilityParams):
        print(f"Initiating Protein Solubility prediction using values: {params}")
        model = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")
        model.eval()

        # Load Tokenizer
        tokenizer_op = ModularTokenizerOp.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")

        protein_seq = params.seq
        print(f"input prot seq: {protein_seq}")

        sample_dict = {"protein_seq": protein_seq}
        sample_dict = ProteinSolubilityTask.data_preprocessing(
            sample_dict=sample_dict,
            protein_sequence_key="protein_seq",
            tokenizer_op=tokenizer_op,
            device=model.device,
        )

        # running in generate mode
        batch_dict = model.generate(
            [sample_dict],
            output_scores=True,
            return_dict_in_generate=True,
            max_new_tokens=5,
        )

        # Post-process the model's output
        ans = ProteinSolubilityTask.process_model_output(
            tokenizer_op=tokenizer_op,
            decoder_output=batch_dict[CLS_PRED][0],
            decoder_output_scores=batch_dict[SCORES][0],
        )

        label_map = {0:"non-soluble", 1:"soluble"}

        return {"pred": label_map[ans["pred"]]}

    def prot_prot_interactions(self, params: datamodels.pyd_models.ProtProtInteraction):
        # Load Model
        model = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m")
        # Set model to evaluation mode
        model.eval()

        # Load Tokenizer
        tokenizer_op = ModularTokenizerOp.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m")

        # Prepare Input Prompt
        protein_seq_1 = params.seq_1
        protein_seq_2 = params.seq_2

        # Create and load sample
        sample_dict = dict()
        # Formatting prompt to match pre-training syntax
        sample_dict[
            ENCODER_INPUTS_STR] = f"<@TOKENIZER-TYPE=AA><BINDING_AFFINITY_CLASS><SENTINEL_ID_0><MOLECULAR_ENTITY><MOLECULAR_ENTITY_GENERAL_PROTEIN><SEQUENCE_NATURAL_START>{protein_seq_1}<SEQUENCE_NATURAL_END><MOLECULAR_ENTITY><MOLECULAR_ENTITY_GENERAL_PROTEIN><SEQUENCE_NATURAL_START>{protein_seq_2}<SEQUENCE_NATURAL_END><EOS>"

        # Tokenize
        tokenizer_op(
            sample_dict=sample_dict,
            key_in=ENCODER_INPUTS_STR,
            key_out_tokens_ids=ENCODER_INPUTS_TOKENS,
            key_out_attention_mask=ENCODER_INPUTS_ATTENTION_MASK,
        )
        sample_dict[ENCODER_INPUTS_TOKENS] = torch.tensor(sample_dict[ENCODER_INPUTS_TOKENS])
        sample_dict[ENCODER_INPUTS_ATTENTION_MASK] = torch.tensor(sample_dict[ENCODER_INPUTS_ATTENTION_MASK])

        # Generate Prediction
        batch_dict = model.generate(
            [sample_dict],
            output_scores=True,
            return_dict_in_generate=True,
            max_new_tokens=5,
        )

        # Get output
        # full_output = tokenizer_op._tokenizer.decode(batch_dict[CLS_PRED])
        # score = batch_dict["model.out.scores"][0][1][batch_dict.positive_token_id(model_holder)].item()
        generated_output = tokenizer_op._tokenizer.decode(batch_dict[CLS_PRED][0])

        label_map = {"<0>": "non-interacting", "<1>": "interacting"}
        tokens = re.findall(r"<[^>]+>", generated_output)
        prediction = None
        for t in tokens:
            if t in label_map:
                prediction = label_map[t]
                break

        return prediction