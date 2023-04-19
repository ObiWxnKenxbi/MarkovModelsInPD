# -*- coding: utf-8 -*-

# Pyext library only available within PD/pyext environment.
try:
    import pyext
except:
    raise ValueError("This script must be loaded by the PD/Max pyext external")

import random
import random
import numpy as np


def event_list_2_pdf(event_list):
    events, counts = np.unique(event_list, return_counts=True, axis=0)
    events = [tuple(x) for x in events]
    pdf = counts/sum(counts)
    return events, pdf


def train(input_sequence):
    observed_transitions = {}
    for i in range(len(input_sequence)-1):
        if input_sequence[i] in observed_transitions:
            observed_transitions[input_sequence[i]].append(input_sequence[i+1])
        else:
            observed_transitions[input_sequence[i]] = [input_sequence[i+1]]

    # now lets make compact verisons of the values
    # basically here we create how many times a specific tuple is occuring after our key and create a pdf of that,
    # also give us all the unique tuple that are occurring after that key
    pdf_dict = {}
    for key in observed_transitions:
        pdf_dict[key] = [event_list_2_pdf(observed_transitions[key])]

    list_unique_pair_sequence = []
    pdf_for_that_key = []
    for key in pdf_dict:
        # get unique pairs
        list_unique_pair_sequence.append(pdf_dict[key][0][0])
        # get pdf for the unique pairs
        pdf_for_that_key.append((pdf_dict[key][0][1]))

    pdf_for_that_key = [arr.tolist() for arr in pdf_for_that_key]

    return pdf_dict, list_unique_pair_sequence, pdf_for_that_key, observed_transitions


def steered_dict(pdf_dict_major, velocity):

    steered_dict_maj = {}
    for key, value in pdf_dict_major.items():
        new_value = []
        count = 0
        for tup, arr in value:
            # print("value is this ", value)
            new_arr = []
            for i, val in enumerate(arr):
                if tup[i][1] == velocity:
                    count += 1
            for i, val in enumerate(arr):
                if tup[i][1] == velocity:
                    new_arr.append(1/count)
                else:
                    new_arr.append(val*0)
            new_value.append((tup, np.array(new_arr)))

            #print("count and values", count, value)
        steered_dict_maj[key] = new_value
    return steered_dict_maj


def select_event_from_pdf(events, pdf):
    event_indexes = range(len(events))
    return events[np.random.choice(event_indexes, 1, p=pdf)[0]]


def generate_from_pdf(trained_pdf):
    output_sequence = []
    now = random.choice(list(trained_pdf.keys()))
    # print ("now", now)
    output_sequence.append(now)
    count = 0
    for x in range(4-1):
        next_events, next_pdf = trained_pdf[now][0]
        # print(sum(next_pdf))
        count += 1
        if sum(next_pdf) == 1:
            next = select_event_from_pdf(next_events, next_pdf)
            now = next
            output_sequence.append(now)

    return output_sequence

def generate_progression(self, scale_type, velocity_value):
    print(scale_type, velocity_value)
    if scale_type == "major":
        chords_integer_to_roman_maj = {'I': 1, 'ii': 2, 'iii': 3, 'IV': 4,
                                       'V': 5, 'vi': 6, 'viiD': 7, 'ii7': 8, 'V7': 9, 'iv': 10, 'VI': 11}
        gravity = ['I', 'IV', 'ii7', 'V7', 'I', 'IV', 'I',
                   'IV', 'ii', 'V', 'iv', 'V', 'VI', 'I', 'V']
        who_says = ['I', 'IV', 'vi', 'V', 'VI', 'iii', 'IV', 'V', 'I',
                    'IV', 'I', 'V', 'IV', 'I', 'V', 'IV', 'I', 'iii', 'vi', 'iii', 'V']
        major_prog = gravity + who_says

        major_prog_integer_with_random = []

        for chord in major_prog:
            chord_integer = chords_integer_to_roman_maj[chord]
            random_integer = random.randint(1, 3)
            major_prog_integer_with_random.append(
                (chord_integer, random_integer))

        pdf_dict_major, list_unique_pair_sequence_maj, pdf_for_that_key_maj, observed_transitions_maj = train(
            major_prog_integer_with_random)

        steered_dict_maj = steered_dict(pdf_dict_major, velocity_value)

        original_chords_generated = []

        while (len(original_chords_generated) != 4):
            aux_result = generate_from_pdf(steered_dict_maj)
            for element in aux_result:
                if element[1] == velocity_value:
                    original_chords_generated.append(element)
                if (len(original_chords_generated) == 4):
                    break

        original_chords_generated = original_chords_generated[:4]

        original_chords_generated_unpacked = []
        for x, y in original_chords_generated:
            original_chords_generated_unpacked.append(x)
            original_chords_generated_unpacked.append(y)

    elif scale_type == "natural minor":
        original_chords_generated_unpacked = [
            "Cm", "Dø", "E♭", "Fm", "Gm", "A♭", "B♭"]
    else:
        raise ValueError("Invalid scale type")

    return original_chords_generated_unpacked


class ChordProgression(pyext._class):
    _inlets = 2  # inlet1 to reset, #inlet 2 to give the desired velocity
    _outlets = 8  # 4 chords and there corresponding velocities to 8 outlets

    def __init__(self):
        self.scale_type = None
        self.velocity = 3  # set default length to 3

    def scale_1(self, scale_type):
        #print(scale_type)
        if scale_type == 1:
            self.scale_type = "major"
        elif scale_type == 2:
            self.scale_type = "natural minor"
        self.length = scale_type
        
    def velocity_2(self, velocity_value):
        print(velocity_value)
        if velocity_value == 1:
            self.velocity_value = 1
        if velocity_value == 2:
            self.velocity_value = 2
        if velocity_value == 3:
            self.velocity_value = 3

        original_chords_generated_unpacked = generate_progression(self, self.scale_type, self.velocity_value)
        for i, chord in enumerate(original_chords_generated_unpacked):
            self._outlet(i+1, chord)  # send each chord to a separate outlet
        print(original_chords_generated_unpacked)

