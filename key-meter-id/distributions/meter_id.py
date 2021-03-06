#!/usr/bin/env python

from __future__ import division, print_function
import os, sys
import numpy as np
from math import log
from sklearn.model_selection import KFold
import utils
import math

def distribution(mels, keys):    
	# keys = [division, beat, pickup]
	# notes = [length]
	
	# Big beats
    meter_beat_sizes = [2, 3, 4] # duple, triple, other
    meter_beat_counts = [ [0] * m for m in meter_beat_sizes]
    meter_beat_totals = [0] * len(meter_beat_counts)
    
    # Subdivisions
    meter_div_sizes = [2, 3, 2] # simple, compound, other
    meter_div_counts = [ [0] * m for m in meter_div_sizes]
    meter_div_totals = [0] * len(meter_div_counts)
    

    for mel, key in zip(mels, keys):

    	beat_val = 1000 if key[0] == 0 else 1500
    	sub_val = 500
    	
    	# beat counts
        meter_beat_factor = (meter_beat_sizes[key[1]] * beat_val)
        cond_mel_beat = [ ((n - key[2]) % (meter_beat_factor)) / float(beat_val) for n in mel]
        reduce_mel_beat = [ n for n in cond_mel_beat if ((round(n) - n) == 0)]
        
        for note in reduce_mel_beat:
            meter_beat_counts[key[1]][int(note)] += 1
            meter_beat_totals[key[1]] += 1
    	
    	# div counts
        meter_div_factor = (meter_div_sizes[key[0]] * sub_val)
        cond_mel_div = [ ((n - key[2]) % (meter_div_factor)) / float(sub_val) for n in mel]
        reduce_mel_div = [ n for n in cond_mel_div if ((round(n) - n) == 0)]
        
        for note in reduce_mel_div:
            meter_div_counts[key[0]][int(note)] += 1
            meter_div_totals[key[0]] += 1

    # beat distribution
    beat_distr = [ [meter_beat_counts[i][k] / meter_beat_totals[i] 
        if meter_beat_totals[i] != 0 else 0
        for k in range(len(meter_beat_counts[i]))] 
        for i in range(len(meter_beat_totals))]
        
    # div distribution
    div_distr = [ [meter_div_counts[i][k] / meter_div_totals[i] 
        if meter_div_totals[i] != 0 else 0
        for k in range(len(meter_div_counts[i]))] 
        for i in range(len(meter_div_totals))]
        
    #print(beat_distr)
    #print(div_distr)
    
    #print(div_distr)
        
    return beat_distr, div_distr


def predict(test_X, test_y, beat_distr, div_distr):
	
    # Big beats
    meter_beat_sizes = [2, 3] # duple, triple
    
    # Subdivisions
    meter_div_sizes = [2, 3] # simple, compound
    
    # Offsets
    offsets = [0, 500, 1000]

    correct = 0
    div_correct = 0
    beat_correct = 0
    pickup_correct = 0
    predictions = 0
        

    for mel, key in zip(test_X, test_y):
    	offsets = [0, 500, 1000]
    	
    	#if key[0] == 2 or key[1] == 2: # irregular
    	#	continue

       
    	sub_val = 500
        
        # Division prediction
        max_div_val = 0
        max_div_pred = None
        for off in offsets:
            for div in range(0, len(meter_div_sizes)):
                cond_mel = [((n - off) % (meter_div_sizes[div] * sub_val)) / float(sub_val) for n in mel]
                reduce_mel = [n for n in cond_mel if ((round(n) - n) == 0)]
                counts = [0] * meter_div_sizes[div]
                for note in reduce_mel:
                    counts[int(note)] += 1
                mel_distr = [n / sum(counts) for n in counts]
                #print("mel_distr: ", mel_distr)
                #compare = np.dot(np.asarray(mel_distr), np.asarray(div_distr[div]))
                compare = sum([np.power((m-p), 2) for m, p in zip(mel_distr, div_distr[div])])
                if compare > max_div_val:
                    max_div_val = compare
                    max_div_pred = div
                    
        div_pred = max_div_pred
        
        
        beat_val = 1000 if div_pred == 0 else 1500
        offsets = [0, 500, 1000, 1500]
        #offsets = [(500 * i) for i in range(0, 5)]

        
        # Beat prediction
        max_beat_val = 0
        max_beat_pred = None
        for off in offsets:
            for beat in range(0, len(meter_beat_sizes)):
                cond_mel = [((n - off) % (meter_beat_sizes[beat] * beat_val)) / float(beat_val) for n in mel]
                reduce_mel = [n for n in cond_mel if ((round(n) - n) == 0)]
                #print("Reduce: ",reduce_mel)
                counts = [0] * meter_beat_sizes[beat]
                for note in reduce_mel:
                    counts[int(note)] += 1
                #print("Counts: ",counts)
                mel_distr = [n / sum(counts) if sum(counts) != 0 else 0 for n in counts ]
                #compare = np.dot(np.asarray(mel_distr), np.asarray(beat_distr[beat]))
                compare = sum([np.power((m-p), 2) for m, p in zip(mel_distr, beat_distr[beat])])
                if compare > max_beat_val:
                    max_beat_val = compare
                    max_beat_pred = [beat, off]
                    
                    
        beat_pred = max_beat_pred
        
        prediction = [div_pred, beat_pred[0], beat_pred[1]]
        
        #print(key)
        #print(prediction)

        if key[0] == prediction[0] and key[1] == prediction[1]:
            correct += 1
            
        if key[0] == prediction[0]:
            div_correct += 1

        if key[1] == prediction[1]:
            beat_correct += 1

        if key[2] == prediction[2]:
            pickup_correct += 1
        #print("k: ",key[2])
        #print(prediction[2])

        predictions += 1
        
        #print(key)
        #print(prediction)
    
    accuracy = correct / predictions
    print(div_correct, "/", predictions)
    
    d_acc = div_correct / predictions
    b_acc = beat_correct / predictions
    p_acc = pickup_correct / predictions

    #print("Total predictions: ", predictions)
    #print("Total correct predictions: ", correct)
    #print("Accuracy: ", accuracy, "\n")

    return accuracy, d_acc, b_acc, p_acc


def cv_test(mels, keys, length):
    print("Length ", length)
    accuracy = []
    d_accuracy = []
    b_accuracy = []
    p_accuracy = []
    splits = 10
    kf = KFold(n_splits=splits, shuffle=True)
    count = 1
    mels = np.asarray(mels)
    keys = np.asarray(keys)

    for train_index, test_index in kf.split(mels):
        train_X, test_X = mels[train_index], mels[test_index]
        train_y, test_y = keys[train_index], keys[test_index]
        
        beat_distr, div_distr = distribution(train_X, train_y)
        
        test_X, test_y = utils.make_id_data(test_X, test_y, length)
        
        #print("Test ", count)
        
        acc, d_acc, b_acc, p_acc = predict(test_X, test_y, beat_distr, div_distr)
        accuracy.append(acc)
        d_accuracy.append(d_acc)
        b_accuracy.append(b_acc)
        p_accuracy.append(p_acc)
        
        count += 1

    mean = np.mean(accuracy)
    std = np.std(accuracy)
    
    d_mean = np.mean(d_accuracy)
    b_mean = np.mean(b_accuracy)
    p_mean = np.mean(p_accuracy)

    print("**Overall**")

    print("Mean accuracy: ", mean)
    print("Standard deviation accuracy: ", std)
    print("Mean div accuracy: ", d_mean)
    print("Mean beat accuracy: ", b_mean)
    print("Mean pickup accuracy: ", p_mean)

def main():
    if len(sys.argv) != 2:
        print("Usage: folder containing mel files")
        return 1
        
    mels, keys = utils.read_files(sys.argv[1], "meter")
    
    
    print("_______Meter_ID_______")

    for l in range(20, 100):
        cv_test(mels, keys, l)

    print("Done.")
    return 0

if __name__ == '__main__':
    main()

