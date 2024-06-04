# MidiCaps - A Large-scale Dataset of Caption-annotated MIDI Files
<p align="center">
<div align="center">
<a href="https://arxiv.org/abs/placeholder">Paper</a>,
<a href="https://huggingface.co/datasets/amaai-lab/MidiCaps">Dataset</a>
</div>

In this repository, we provide the pipeline to extract a comprehensive set of music-specific features extracted from MIDI files. These features succinctly characterize the musical content, encompassing tempo, chord progression, time signature, instrument presence, genre, and mood. Consecutively we provide the script to generate captions from your own collection of MIDI files. 

To directly download the MidiCaps dataset, please visit our huggingface dataset page: [<img src="imgs/hf-logo.png" alt="dataset" width= "5%" class="center" >](https://huggingface.co/datasets/amaai-lab/MidiCaps). 

The below code will help you extract captions from your own collection of MIDI files. If you use this model or dataset, please cite our paper (see below). 

## Installation Guide
```bash
git clone https://github.com/AMAAI-Lab/MidiCaps.git
cd MidiCaps
conda create -n midicaps python=3.9
pip install -r requirements.txt
```
## User Guide
```bash
python pipeline.py --config config.cfg
```
Output of this will be `all_files_output.json`. We generate `test.json` from this to do in-context learning for [claude 3](https://www.anthropic.com/news/claude-3-family). We provide a sample `test.json` and a basic script to run claude 3. Users have to add claude 3 key as environment variable `ANTHROPIC_API_KEY`.
```bash
export ANTHROPIC_API_KEY=<your claude 3 key>
python captions_claude.py
```
Please change line 59 in caption_claude.py for your preferred location. 

## Citation
If you find our work useful, please cite our paper:

'''
@article{Melechovsky2024,
  author    = {Jan Melechovsky and Abhinaba Roy and Dorien Herremans},
  title     = {MidiCaps - A Large-scale MIDI Dataset with Text Captions},
  year      = {2024},
}
'''

APA: Jan Melechovsky, Abhinaba Roy, Dorien Herremans, 2024, MidiCaps - A large-scale MIDI dataset with text captions.
