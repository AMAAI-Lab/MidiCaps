# MidiCaps - A Large-scale Dataset of Caption-annotated MIDI Files

<div align="center">
<a href="https://arxiv.org/abs/2406.02255">Paper</a>,
<a href="https://huggingface.co/datasets/amaai-lab/MidiCaps">MidiCaps Dataset</a>, 
<a href="https://amaai-lab.github.io/MidiCaps/">Examples</a>
<br/><br/>
  
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/amaai-lab/MidiCaps) [![arXiv](https://img.shields.io/badge/arXiv-2406.02255-brightgreen.svg)](https://arxiv.org/abs/2406.02255)
</div>

In this repository, we provide the pipeline to extract a comprehensive set of music-specific features extracted from MIDI files. These features succinctly characterize the musical content, encompassing tempo, chord progression, time signature, instrument presence, genre, and mood. Consecutively we provide the script to generate captions from your own collection of MIDI files. 

To directly download the MidiCaps dataset, please visit our huggingface dataset page: [![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/amaai-lab/MidiCaps). 

The below code will help you extract captions from your own collection of MIDI files, as per the framework described [in our paper](https://arxiv.org/abs/2406.02255). 

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
python caption_claude.py
```
Please change [line 59](https://github.com/AMAAI-Lab/MidiCaps/blob/7266065a121e21029a1b83b3122c9a0b0e310204/caption_claude.py#L59) in `caption_claude.py` for your preferred location. 

## Citation
If you find our work useful, please cite [our paper](https://arxiv.org/abs/2406.02255):

```
@article{Melechovsky2024,
  author    = {Jan Melechovsky and Abhinaba Roy and Dorien Herremans},
  title     = {MidiCaps - A Large-scale MIDI Dataset with Text Captions},
  year      = {2024},
  journal   = {arXiv:2406.02255}
}
```
