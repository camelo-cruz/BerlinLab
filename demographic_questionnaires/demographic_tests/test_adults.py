#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 12:31:44 2023

@author: alejandracamelocruz
"""

import logging
import os
import numpy as np
import pandas as pd


logging.basicConfig(filename='children_demography.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG,
                    force=True)

logger=logging.getLogger() 


def get_test_vars():
    test_variables = {}
    cwd = os.getcwd()
    cwd = os.path.abspath(cwd)
    for file in os.listdir(cwd):
        filename = os.fsdecode(file)
        if filename.endswith('.csv'):
            data = pd.read_csv(filename)
    columns = list(data.columns)
    for column in columns:
        try:
            value = data[column].iloc[0]
            if isinstance(value, np.generic):
                value = value.item()
            test_variables[column] = type(value)
        except IndexError:
                test_variables[column] = None
    
    return test_variables


def get_correct_vars():
    single_variables = {'Block_Name': str,
     'Block_Nr': int,
     'End_Time_Local': str,
     'Exp_Subject_Id': int,
     'Group_Name': str,
     'Group_Nr': int,
     'Rec_Session_Id': int,
     'Session_Name': str,
     'Session_Nr': int,
     'Start_Time_Local': str,
     'Subject_Code': str,
     'Subject_Nr': int,
     'Task_Name': str,
     'Task_Nr': int,
     'Trial_Id': int,
     'Trial_Nr': int,
     'a_birth_place': str,
     'a_birth_year': int,
     'a_language_difficulties_hearing': bool,
     'a_language_difficulties_speaking': bool,
     'a_language_native_speaking_start': int,
     'a_residence_arrival_age_month': int,
     'a_residence_arrival_age_years': int,
     'a_residence_country_state': str,
     'a_sex': str,
     'b_education_currently_enrolled': bool,
     'b_education_currently_enrolled_level': str,
     'b_education_currently_enrolled_years': int,
     'b_education_level': str,
     'b_education_years': int,
     'c_first_language_of_literacy': str,
     'c_instructed_in_only_one_language': bool,
     'c_languages_favourite': str,
     'c_languages_of_counting': str,
     'c_languages_of_thinking': str,
     'c_languages_of_instruction': str,
     'date_of_consent': str,
     'participant_id': str,
     'participant_consent': bool,
     }
    
    placeholder_variables = {
        'lang{number}': str,
        'lang{number}_ability_listening': int,
        'lang{number}_ability_reading': int,
        'lang{number}_ability_writing': int,
        'lang{number}_ability_speaking': int,
        'lang{number}_context_01_school_university': int,
        'lang{number}_context_02_work': int,
        'lang{number}_context_03_family': int,
        'lang{number}_context_04_social_activities': int,
        'lang{number}_context_05_other_activities': int,
        'lang{number}_exposure_age': int,
        'lang{number}_exposure_how_long_in_country_of_language': int,
        'lang{number}_exposure_literacy_age': int,
        'lang{number}_exposure_place': str
    }
    
    number_variables = {} 
    for i in range(1, 4):
        for var, var_type in placeholder_variables.items():
                replaced_var = (var.replace("{number}", str(i)))
                number_variables[replaced_var] = var_type
    
    correct_variables = single_variables.copy()
    correct_variables.update(number_variables)
    

    return correct_variables


to_test = get_test_vars()
correct_variables = get_correct_vars()


def test_variables():
    logger.info('*********** variables ***********')
    num = 0
    bad_recorded = []
    
    for var in to_test:
        if var not in correct_variables:
            num += 1
            logger.error(f'{num} {var} is wrong')
            bad_recorded.append(var)
    for var in correct_variables:
        if var not in to_test:
            logger.error(f'{var} should be recorded')
            
    assert all(element in to_test for element in correct_variables)


def test_types():
    
    logger.info('*********** types ***********')
    for var, vartype in to_test.items():
        if var in correct_variables:
            if correct_variables[var] != vartype:
                logger.error(f'incorrect type for {var}. It should be {correct_variables[var]} '+
                              f'but it is {vartype}')
    for var, vartype in to_test.items():
        assert correct_variables[var] == vartype
