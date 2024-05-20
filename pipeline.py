from midi2audio import FluidSynth
from music21 import converter, corpus, instrument, midi, note, chord, pitch, stream
import glob
import os
from time import time
from essentia.standard import MonoLoader, TensorflowPredictEffnetDiscogs, TensorflowPredict2D
from chord_extractor.extractors import Chordino
import configparser
import json
import argparse
import numpy as np
import mido

def get_mtg_tags(embeddings,tag_model,tag_json,max_num_tags=5,tag_threshold=0.01):

    with open(tag_json, 'r') as json_file:
        metadata = json.load(json_file)
    predictions = tag_model(embeddings)
    mean_act=np.mean(predictions,0)
    ind = np.argpartition(mean_act, -max_num_tags)[-max_num_tags:]
    tags=[]
    confidence_score=[]
    for i in ind:
        print(metadata['classes'][i] + str(mean_act[i]))
        if mean_act[i]>tag_threshold:
            tags.append(metadata['classes'][i])
            confidence_score.append(mean_act[i])
    ind=np.argsort(-np.array(confidence_score))
    tags = [tags[i] for i in ind]
    confidence_score=np.round((np.array(confidence_score)[ind]).tolist(),4).tolist()

    return tags, confidence_score

def process_midi(file):
    fs = FluidSynth('/666/midiproject/usr/share/soundfonts/FluidR3_GM.sf2',sample_rate=16000)
    #check for duration, do not synthesize files over 15 mins long...
    try:
        mid = mido.MidiFile(file)
        if mid.length>900:
            return None
    except Exception as e:
        print(e)
        return None

    prefix = os.path.dirname(file)
    suffix = os.path.basename(file).split('.')[0]
    audio_file=os.path.join(prefix,suffix+'.wav')
    fs.midi_to_audio(file, audio_file)
    return audio_file

def get_final_inst_list(midi_file_path):
    # Dictionary to store instrument durations
    instrument_durations = defaultdict(float)
    instrument_names=[]
    instrument_channels=[]
    instrument_change_times=[]
    # Parse MIDI file
    midi = mido.MidiFile(midi_file_path)
    # Iterate through each track
    for track in midi.tracks:
        # Dictionary to store note-on events for each instrument
        active_notes = defaultdict(float)
        last_event_time = 0
        # Iterate through each event in the track
        for msg in track:
            # Update the time since the last event
            delta_time = msg.time
            last_event_time += delta_time
            if msg.type=='program_change':
                prog=msg.program
                chan=msg.channel
                # if chan==9 and prog==0:
                if chan==9 and not 111<prog<120:
                    prog=128
                if chan in instrument_channels:
                    instrument_names[instrument_channels.index(chan)]=prog #replace the existing instrument in this channel, no ambiguity!!!
                else:
                    instrument_names.append(prog)
                    instrument_channels.append(chan)
                instrument_change_times.append(msg.time)
                # print(msg.time)
            # If it's a note-on or note-off event
            if msg.type == 'note_on' or msg.type == 'note_off':
                # Extract the instrument (channel) and note number
                channel = msg.channel
                note = msg.note
                # Calculate the duration since the last event
                duration = last_event_time - active_notes[(channel, note)]
                active_notes[(channel, note)] = last_event_time
                # Accumulate the duration for this instrument
                instrument_durations[channel] += duration
    new_dict=sorted(instrument_durations.items(), key=lambda x:x[1],reverse=True)
    if len(instrument_names)>20:
        print('too many instruments in this one!')
        print(midi_file_path)
        return [], []
    sorted_instrument_list=[]
    how_many=min(5,len(set(instrument_names)))
    if how_many==0:
        return []
    add_drums=False
    if 9 not in instrument_channels:
        for rr in new_dict:
            if 9 in rr:
                add_drums=True
                break
            else:
                add_drums=False
    if add_drums:
        instrument_names.append(128)
        instrument_channels.append(9)
    for i in range(len(new_dict)):
        try:
            sorted_instrument_list.append(instrument_names[instrument_channels.index(new_dict[i][0])])
        except Exception as e:
            print(e)
            print(midi_file_path)
            return sorted_instrument_list
    return sorted_instrument_list

def read_midi(path):
    mf = midi.MidiFile()
    mf.open(path)
    mf.read()
    mf.close()
    return midi.translate.midiFileToStream(mf)

def get_keys(midi):
    keys = midi.analyze('keys')
    return keys

def get_time_signature(midi):
    timeSignature = midi.getTimeSignatures()[0]
    return timeSignature

def get_tempo(midifile):
    mid = mido.MidiFile(midifile)
    try:
        for msg in mid:
            if msg.type == 'set_tempo':
                tempo = mido.tempo2bpm(msg.tempo)
                return tempo
    except:
        return None
    return None

def get_duration(file):
    try:
        mid = mido.MidiFile(file)
        return mid.length
    except:
        return-1
    
def main():
    parser = argparse.ArgumentParser(description="Extract tags from a dataset.")
    parser.add_argument(
        "--goon", action="store_true", 
        default=True,help="How many splits we're using."
        )
    parser.add_argument(
        '--config', type=str, 
        help='Path to the configuration file'
        )
    args = parser.parse_args()
    config = configparser.ConfigParser()
    if args.config:
        config.read(args.config)
    else:
        config.read('config.cfg')  # default config file
    goon=args.goon
    t=time()
    genre_model=config['DEFAULT'].get('genre_model',None)
    genre_metadata=config['DEFAULT'].get('genre_metadata',None)
    mood_model=config['DEFAULT'].get('mood_model',None)
    mood_metadata=config['DEFAULT'].get('mood_metadata',None)
    emb_model=config['DEFAULT'].get('emb_model',None)
    instrumentmap=config['DEFAULT'].get('instrumentmap',None)
    embedding_model = TensorflowPredictEffnetDiscogs(graphFilename=emb_model, output="PartitionedCall:1")
    genmodel = TensorflowPredict2D(graphFilename=genre_model)
    moodmodel = TensorflowPredict2D(graphFilename=mood_model)
    chord_estimator = Chordino()
    location_file=config['DEFAULT'].get('location_file',None)
    output_json_file=config['DEFAULT'].get('output_json_file',None)
    file_list=[]
    with open(location_file,'r') as jsonfile:
        for row in jsonfile:
            a=json.loads(row)
            file_list.append(a['name'])
    if goon:
        auxilary_json_file=output_json_file[0:-5]+'aux'+'.json'
        current_file_list=[]
        print('continuing from where we left off!')
        with open(output_json_file, 'r') as jsonfile:
            with open(auxilary_json_file,'w') as aux_jsonfile:
                for row in jsonfile:
                    a=json.loads(row)
                    current_file_list.append(a)
                    aux_jsonfile.write(json.dumps(a) + '\n')
        how_many=len(current_file_list)-5
    i=0
    with open(output_json_file,'w') as out_json:
        if goon:
            i=how_many
            file_list = file_list[how_many:]
            with open(auxilary_json_file, 'r') as aux_json:
                hh=0
                for row in aux_json:
                    if hh==how_many:
                        goon_from_this_file=json.loads(row)
                        break
                    else:
                        a=json.loads(row)
                        out_json.write(json.dumps(a) + '\n')
                        hh+=1
        for file in file_list:
            midi = read_midi(file)
            if goon:
                if file==goon_from_this_file['name']:
                    goon=False
                else:
                    continue           
            #AUDIO PART
            audio_file=process_midi(file)
            if audio_file is None:
                continue
            if os.path.exists(audio_file):
                audio = MonoLoader(filename=audio_file, sampleRate=16000, resampleQuality=1)()
                if len(audio)<48000: #remove samples less than 3 seconds long...
                    continue
                embeddings = embedding_model(audio)
                mood_tags, mood_cs = get_mtg_tags(embeddings,moodmodel,mood_metadata,max_num_tags=5,tag_threshold=0.02)
                genre_tags, genre_cs = get_mtg_tags(embeddings,genmodel,genre_metadata,max_num_tags=4,tag_threshold=0.05)               
                chords = chord_estimator.extract(audio_file)
                os.remove(audio_file) #remove the audio file after synthesis, otherwise it takes too much space!
                #MIDI PART
                #instruments
                try:
                    fulllist=get_final_inst_list(file)
                except Exception as e:
                    print(e)
                    print('skipped instruments')
                    i+=1
                    print(i)
                    fulllist=[]
                #instrument mapping and summary
                with open (instrumentmap,'r') as csvf:
                    csv_reader=csv.reader(csvf)
                    data = [row for row in csv_reader]
                out_inst_list=[]
                for inst in fulllist:
                    out_inst_list.append(data[inst][3])
                #instruments summary - only add one instance of each instrument, then keep top 5
                out_inst_sum_list=[]
                for rr in out_inst_list:
                    if rr not in out_inst_sum_list:
                        out_inst_sum_list.append(rr)
                how_many=np.min((5,len(out_inst_sum_list)))
                out_inst_sum_list=out_inst_sum_list[0:how_many]
                #key
                try:
                    res_key = get_keys(midi)
                    key = res_key.tonic.name + " " + res_key.mode
                except:
                    key = None
                #key postprocessing
                if key is None:
                    key=key
                elif '-' in key:
                    key=key.replace('-','b')
                else:
                    key=key
                #time signature
                try:
                    time_sig = get_time_signature(midi)
                    time_signature = str(time_sig.numerator)+'/'+str(time_sig.denominator)
                except:
                    time_signature = None
                #tempo
                try:
                    tempo = get_tempo(file)
                except: 
                    tempo = None
                #tempo postprocessing
                bpm=np.round(bpm)
                if np.isnan(bpm):
                    cap=''
                    bpm=''
                else:
                    bpm=int(bpm)
                    dice=np.random.randint(0,2)
                    if dice==0:
                        tempo_marks=np.array((40, 60, 70, 90, 110, 140, 160, 210))
                        tempo_caps=['Grave', 'Largo', 'Adagio', 'Andante', 'Moderato', 'Allegro', 'Vivace', 'Presto', 'Prestissimo']
                        index=np.sum(bpm>tempo_marks)
                        tempo_cap=tempo_caps[index]
                    else:
                        tempo_marks=np.array((80, 120, 160))
                        tempo_caps=['Slow', 'Moderate tempo', 'Fast', 'Very fast']
                        index=np.int(np.sum(bpm>tempo_marks))
                        tempo_cap=tempo_caps[index]
                #duration
                    try:
                        duration = get_duration(file)
                    except:
                        duration = None
                #duration postprocessing
                dur_marks=np.array((30, 120, 300))
                dur_caps=['Short fragment', 'Short song', 'Song', 'Long piece']
                dur=int(np.round(duration))
                index=np.int(np.sum(dur>dur_marks))
                dur_cap=dur_caps[index]
                #sort nicely
                new_row={}
                new_row['name']=file
                new_row['chords']=[(x.chord, x.timestamp) for x in chords[1:-1]]
                new_row['genre']=[genre_tags, genre_cs]
                new_row['mood']=[mood_tags, mood_cs]
                new_row['tempo']=[bpm,tempo_cap]
                new_row['duration']=[dur,dur_cap]
                new_row['key']=key
                new_row['time_signature'] = time_signature
                new_row['tempo'] = tempo
                new_row['sorted_instruments']=fulllist
                new_row['mapped_instruments']=out_inst_list
                new_row['mapped_instruments_summary']=out_inst_sum_list
                out_json.write(json.dumps(new_row) + '\n')
                print(i)
                i+=1
            else:
                continue
    print(str(time()-t))

if __name__ == "__main__":
    main()  
