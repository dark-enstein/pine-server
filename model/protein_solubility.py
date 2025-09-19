import os

from fuse.data.tokenizers.modular_tokenizer.op import ModularTokenizerOp

from mammal.examples.protein_solubility.task import ProteinSolubilityTask
from mammal.keys import CLS_PRED, SCORES
from mammal.model import Mammal
from mammal.examples.carcinogenicity.task import CarcinogenicityTask

# Load Model
model = Mammal.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")
model.eval()

# Load Tokenizer
tokenizer_op = ModularTokenizerOp.from_pretrained("ibm/biomed.omics.bl.sm.ma-ted-458m.protein_solubility")

# protein_seq: FASTA sequence of a protein, input for the model to predict its solubility
# calmodulin
protein_seq = "CCCHCCHNCOCNCONCHCCCCONCHCCCOOCONCHCCCNOCONCHCSSCCHNCOCHNCOCHCONCOCHNCOCHCSSCCHNCOCHCCCCNCOCHCCCNCNNCOCHCCCNONCOCHCCNONCOCHNCOCHNCCCCCCCCCCCONCCONCHCOCONCHCCCNCNCONCHCCCCCONCHCCCCONCHCCCOOCONCHCCONCHCCCCCONCHCCCCCOCCCONCHCCCCCONCHCCCCONCHCSSCCHNCOCHCCCCCOCCNCOCHCCNONCOCHCCCOONCOCHCCCCNCOCHCCCNONCOCHCCCCCOCCNCOCHCCCCNCOCHCONCOCONCHCCNOCOOCONCCONCHCCCOOCONCHCCCNCNNCONCCONCHCCCCCCCCONCHCCCCCCCCONCHCCCCCOCCCONCHCHCOCONCCCCHCONCHCCCCNCONCHCHCOCOONCOCHCOCHCCC"

# convert to MAMMAL style
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

carcin = CarcinogenicityTask.process_model_output(
    tokenizer_op=tokenizer_op,
    decoder_output=batch_dict[CLS_PRED][0],
    decoder_output_scores=batch_dict[SCORES][0],
)

# Print prediction
# insoluble - 0
# soluble - 1
print(f"Calmodulin protein solubility pred: \n{ans=}")
print(f"Calmodulin protein carcinogenity pred: \n{ans=}")