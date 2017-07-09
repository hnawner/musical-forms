#!/usr/bin/env python

import os
import numpy as np
from sklearn.model_selection import train_test_split as tts

def read_files(folder):
    files = os.listdir(folder)

    mels = []

    offsets = { "C":0, "C-sharp":1, "D-flat":1, "D":2, "D-sharp":3, "E-flat":3,
                "E":4, "E-sharp":5, "F-flat":4, "F":5, "F-sharp":6, "G-flat":6,
                "G":7, "G-sharp":8, "A-flat":8, "A":9,
                "A-sharp":10, "B-flat":10, "B":11, "B-sharp":0, "C-flat":11 }

    for f in files:
        path = folder + "/" + f
        offset = 0 # offset from key of C
        with open(path, 'r', 0) as f:
            mel = []
            for line in f:
                parsed = line.split() # delimiter as spaces

                if parsed[0] == "Info" and parsed[1] == "key":
                    offset = offsets[parsed[2]]

                elif parsed[0] == "Note":
                    pitch = int(parsed[3]) - offset
                    mel.append(pitch)

            mels.append(mel)
    
    return mels
    
def read_files_rhythm(folder, r_dict = None):
    files = os.listdir(folder)

    mels = []

    for f in files:
        path = folder + "/" + f
        with open(path, 'r', 0) as f:
            mel = []
            f = [line for line in f]
            for i in range(len(f)):
                parsed = f[i].split("\t")
                
                if parsed[0] == "Note":
                    length = None
                    if f[i+1].split()[0] == "Note":
                        length = int(f[i+1].split()[1]) - int(parsed[1])
                    else:
                        length = int(parsed[2]) - int(parsed[1])
                    
                    r_approx = [v for (k, v) in r_dict.items() 
                            if abs(length - k) < 5]
                    rhythm = r_approx[0]
                    mel.append(rhythm)
            mels.append(mel)
                            
    return mels
    
    
def build_rhythm_dict(folder):
    data = os.listdir(folder)
    
    rhythms = []
    
    for f in data:
        #if ".txt" in f:
            f_path = folder + "/" + f
            with open(f_path, 'r', 0) as f:
            	f = [line for line in f]
                for i in range(len(f)):
                    parsed = f[i].split("\t")

                    if parsed[0] == "Note":
                        length = None
                        if f[i+1].split()[0] == "Note":
                            length = int(f[i+1].split()[1]) - int(parsed[1])
                        else:
                            length = int(parsed[2]) - int(parsed[1])
                            
                        diffs = [abs(r - length) for r in rhythms]
                        if diffs != [] and min(diffs) < 5:
                            continue
                        else: rhythms.append(length)
                                
    rhythms.sort()
    r_dict = {}
    for i in range(len(rhythms)):
        r_dict[(rhythms[i])] = i
                            
    return r_dict


def make_ngrams(seqs, n):
    grams = []
    for seq in seqs:
        prevs = seq[:(n-1)]
        for index in range((n-1), len(seq)):
            prevs += [ (seq[index]) ]
            grams.append(prevs)
            prevs = prevs[1:]
    return grams


def one_hot_ngram_PCandOctave(grams):
    vecs_list = []
    targets = []
    for gram in grams:
        vecs = []
        for index in range(len(gram) - 1):
            pc_vec = [0] * 12
            octave_vec = [0] * 8
            pc_vec[(gram[index] % 12)] = 1
            octave_vec[(gram[index] / 12)] = 1
            vecs += pc_vec
            vecs += octave_vec
        target = gram[-1]
        vecs_list.append(vecs)
        targets.append(target)

    return vecs_list, targets


def one_hot_ngram(grams):
    vecs_list = []
    targets = []
    for gram in grams:
        vecs = []
        for index in range(len(gram) - 1):
            vec = [0] * 88
            vec[(gram[index])] = 1
            vecs += vec
        target = gram[-1]
        vecs_list.append(vecs)
        targets.append(target)

    return vecs_list, targets


def one_hot_ngram_AbsAndPc(grams):
    vecs_list = []
    targets = []
    for gram in grams:
        vecs = []
        for index in range(len(gram) - 1):
            absvec = [0] * 88
            pcvec = [0] * 12
            absp = gram[index]
            pc = int(absp % 12)
            absvec[absp] = 1
            pcvec[pc] = 1
            absvec += pcvec
            vecs += absvec
        target = gram[-1]
        vecs_list.append(vecs)
        targets.append(target)

    return vecs_list, targets


def one_hot_ngram_CNN(grams, n):
    vecs_list = []
    targets = []
    for gram in grams:
        vecs = []
        for index in range(len(gram) - 1):
            vec = np.array([0] * 88)
            vec[(gram[index])] = 1
            vecs.append(vec)
        vecs = np.reshape(np.array((vecs), ndmin = 3), [1, 88, (n-1)])
        target = np.array(gram[-1])
        vecs_list.append(vecs)
        targets.append(target)

    return np.array(vecs_list), np.array(targets)

        
def setup_ngrams(folder, n, encoder):
    mels = read_files(folder)
    grams = make_ngrams(mels, n)
    X, y = encoder(grams, n)
    return tts(X, y, test_size = 0.2)


