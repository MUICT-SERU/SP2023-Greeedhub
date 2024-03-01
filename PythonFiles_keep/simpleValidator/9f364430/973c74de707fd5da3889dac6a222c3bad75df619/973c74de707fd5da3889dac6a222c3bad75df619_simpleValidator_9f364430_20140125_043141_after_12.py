# -*- coding: utf-8 -*-

""" 
    Simple Validator class with default validation rules, inspired by laravel

"""
import rules as rulefactory, i18n

class Validator:

    def __init__(self, **kwargs):
        
        self.rulefactory = rulefactory

        """ messages are optional, for i18n and whatever """
        self.error_messages = []
        self.error_rules = []

        if 'fields' in kwargs and 'rules' in kwargs:
            self.make(fields = kwargs.get('fields'), rules = kwargs.get('rules'), messages = kwargs.get('messages'))

        
    def make(self, **kwargs):

        fields = kwargs.get('fields')
        rules = kwargs.get('rules')
        messages = kwargs.get('messages')

        if not isinstance(fields, dict):
            raise ValueError('field data must be a dict')

        if not isinstance(rules, dict):
            raise ValueError('rules data must be a dict')

        if messages is not None and not isinstance(messages, dict):
            raise ValueError('custom error messages must be containend in a dict')

        self.fields = fields
        self.rules = rules 

        if messages:
            self.rulefactory.messages.update(messages)

        """ Routine to makesure that fields and rules and messages are consistent """
        self.verify_fields()
        self.validate()


    def extend(self, customrule):
        if not isinstance(customrule, dict):
            raise ValueError('custome rule must be a dict')

        for rule in customrule:
            setattr(self.rulefactory, rule, customrule[rule])

    def __call_rule(self, rule, **kwargs):
        return getattr(self.rulefactory, rule)(**kwargs)

    def validate(self):
        errors = []
        failed_rules = []
        
        for field in self.rules:
            ### Not elegant, but allows full compat py2/py3 :D
            rules = self.rules[field]
            rulelist = rules.split('|')
        
            for rule in rulelist:

                if ":" in rule:
                    rulevalue = rule.split(":")
                    callback = self.__call_rule(rule = rulevalue[0], value = self.fields[field], constraint = rulevalue[1])

                else:
                    rulevalue = [rule, rule]
                    callback = self.__call_rule(rule = rule, value = self.fields[field])

                if not callback:

                    if self.rulefactory.is_number(self.fields[field]) and rulevalue[1]:
                        errors.append(self.set_errors(rulevalue[0]+'d', field = field, constraint = rulevalue[1]))
                    
                    elif not self.rulefactory.is_number(self.fields[field]) and rulevalue[1]:
                        errors.append(self.set_errors(rulevalue[0], field = field, constraint = rulevalue[1]))
                    
                    else:
                        errors.append(self.rulefactory.messages[rule] % field)
                    failed_rules.append({field: rule})

        self.error_messages = errors
        self.error_rules = failed_rules
        return errors

    def set_errors(self, rule, **kwargs):
        ### we need to fetch the most current reference to gettext for translations ###
        _ = i18n.defaultlang.gettext

        if ',' in kwargs['constraint']:
            boundaries = kwargs['constraint'].split(',')
            return _(self.rulefactory.messages[rule]).format(kwargs['field'], boundaries[0], boundaries[1])


        return _(self.rulefactory.messages[rule]).format(kwargs['field'], kwargs['constraint'])

    def fails(self):
        return len(self.error_messages) > 0

    def failed(self):
        return self.error_rules

    def errors(self):
        return self.error_messages

    def verify_fields(self):

        """ 
            As rules can be optional (ie not explicitely enforced)
            We check that the rules exist in the field dict 
        """
        for rule in self.rules:
            if rule not in self.fields:
                raise ValueError('fields do not correspond to rules')

            #if self.messages is not None and rule not in self.messages:
            #    raise ValueError('messages do not correspond to fields')