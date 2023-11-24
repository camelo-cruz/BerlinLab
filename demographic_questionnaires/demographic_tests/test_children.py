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
     'Completed': bool,
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
     'Trial_ID': int,
     'Trial_Nr': int,
     'b_birth_country_state': str,
     'b_birth_month': int,
     'b_birth_year': int,
     'b_language_difficulties_hearing': bool,
     'b_language_difficulties_speaking': bool,
     'b_language_native_speaking_start': int,
     'b_n_family_members_living_with_child': int,
     'b_nursery_attended': bool,
     'b_nursery_country_state': str,
     'b_nursery_duration_months': int,
     'b_preschool_daycare_language': str,
     'b_preschool_daycare_years': int,
     'b_residence_arrival_age_month': int,
     'b_residence_arrival_age_years': int,
     'b_residence_country_state': str,
     'b_sex': str,
     'b_siblings_additional': int,
     'c_language_exposure_list': str,
     'date_of_consent': str,
     'parental_consent': bool,
     'participant_id': str}
    
    placeholder_variables = {'lang{number}_speaking_and_understanding': bool,
     'a_guardian{number1}_education_level': str, #shouldn't it be int?
     'lang{number}_context_03_siblings': int,
     'lang{number}_exposure_age': int,
     'lang{number}_context_10_videogames': int,
     'a_guardian{number1}_lang{number2}': str,
     'lang{number}_context_02_father': int,
     'lang{number}_context_08_stories': int,
     'lang{number}': str,
     'a_guardian{number1}_lang{number2}_level': int,
     'lang{number}_understanding_only': bool,
     'a_guardian{number1}_education_years': int,
     'b_sibling{number}_age': int,
     'lang{number}_context_07_other_conversations': int,
     'lang{number}_context_01_mother': int,
     'lang{number}_exposure_place': str,
     'lang{number}_context_05_school': int,
     'lang{number}_context_06_nonrelatives': int,
     'a_guardian{number1}_birthplace': str,
     'lang{number}_context_04_other_relatives': int,
     'b_sibling{number}_sex': str,
     'lang{number}_context_09_TV': int}
    
    number_variables = {}
    for i in range(1, 3):
        for j in range(1, 4):
            for k in range(1, 5):
                for var, var_type in placeholder_variables.items():
                    replaced_var = (var.replace("{number}", str(k)).
                                    replace("{number1}", str(i)).
                                    replace("{number2}", str(j)))
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



