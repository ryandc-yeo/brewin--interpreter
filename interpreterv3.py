from classv3 import ClassDef, TemplateDef
from intbase import InterpreterBase, ErrorType
from bparser import BParser
from objectv3 import ObjectDef
from type_valuev3 import TypeManager

# need to document that each class has at least one method guaranteed

# Main interpreter class


class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.trace_output = trace_output
        self.template_index = {}

    # run a program, provided in an array of strings, one string per line of source code
    # usese the provided BParser class found in parser.py to parse the program into lists
    def run(self, program):
        status, parsed_program = BParser.parse(program)
        if not status:
            super().error(
                ErrorType.SYNTAX_ERROR, f"Parse error on program: {parsed_program}"
            )
        self.__add_all_class_types_to_type_manager(parsed_program)
        self.__map_class_names_to_class_defs(parsed_program)

        # instantiate main class
        invalid_line_num_of_caller = None
        self.main_object = self.instantiate(
            InterpreterBase.MAIN_CLASS_DEF, invalid_line_num_of_caller
        )

        # call main function in main class; return value is ignored from main
        self.main_object.call_method(
            InterpreterBase.MAIN_FUNC_DEF, [], False, invalid_line_num_of_caller
        )

        # program terminates!

    # user passes in the line number of the statement that performed the new command so we can generate an error
    # if the user tries to new an class name that does not exist. This will report the line number of the statement
    # with the new command
    def instantiate(self, class_name, line_num_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_num_of_statement,
            )
        class_def = self.class_index[class_name]
        obj = ObjectDef(
            self, class_def, None, self.trace_output
        )  # Create an object based on this class definition
        return obj

    # returns a ClassDef object
    def get_class_def(self, class_name, line_number_of_statement):
        if class_name not in self.class_index:
            super().error(
                ErrorType.TYPE_ERROR,
                f"No class named {class_name} found",
                line_number_of_statement,
            )
        return self.class_index[class_name]

    # returns a bool
    def is_valid_type(self, typename):
        return self.type_manager.is_valid_type(typename)

    # returns a bool
    def is_a_subtype(self, suspected_supertype, suspected_subtype):
        return self.type_manager.is_a_subtype(suspected_supertype, suspected_subtype)

    # typea and typeb are Type objects; returns true if the two type are compatible
    # for assignments typea is the type of the left-hand-side variable, and typeb is the type of the
    # right-hand-side variable, e.g., (set person_obj_ref (new teacher))
    def check_type_compatibility(self, typea, typeb, for_assignment=False):
        return self.type_manager.check_type_compatibility(typea, typeb, for_assignment)
    
    def create_template(self, template_name, params):
        if not self.template_index.get(template_name):
            super().error(
                ErrorType.NAME_ERROR,
                f"Template Name does not exist {template_name}",
            )
        name = InterpreterBase.TYPE_CONCAT_CHAR.join([template_name] + params)
        if not self.type_manager.is_valid_type(name):
            template = self.template_index[template_name]
            self.type_manager.add_class_type(name, None)
            class_source = template.get_class_source(params)
            self.class_index[name] = ClassDef(class_source, self)
    
    def __map_template_names_to_template_defs(self, item):
        template_name = item[1]
        self.template_index[template_name] = TemplateDef(item, self)
        # self.type_manager.add_class_type(template_name, None)

    def __map_class_names_to_class_defs(self, program):
        self.class_index = {}
        for item in program:
            if item[0] == InterpreterBase.CLASS_DEF:
                if item[1] in self.class_index:
                    super().error(
                        ErrorType.TYPE_ERROR,
                        f"Duplicate class name {item[1]}",
                        item[0].line_num,
                    )
                self.class_index[item[1]] = ClassDef(item, self)

    # [class classname inherits superclassname [items]]
    def __add_all_class_types_to_type_manager(self, parsed_program):
        self.type_manager = TypeManager()
        for item in parsed_program:
            if item[0] == InterpreterBase.CLASS_DEF:
                class_name = item[1]
                superclass_name = None
                if item[2] == InterpreterBase.INHERITS_DEF:
                    superclass_name = item[3]
                self.type_manager.add_class_type(class_name, superclass_name)
            elif item[0] == InterpreterBase.TEMPLATE_CLASS_DEF:
                self.__map_template_names_to_template_defs(item)



def main():
    # program = ['(class main',
# '(method void main ()',
# '(begin',
# '(while true',
# '(begin',
# '(print "only printed once")',
# '(throw "get me outta here!")',
# '(print "after throw")',
# ')',
# ')',
# '(print "after while")',
# ')',
# ')',
# ')']
    program = ['(class main',
'(method void bar ()',
'(throw "foo")',
')',
'(method void main ()',
'(try',
'(while (call me bar)',
'(print "this doesnt print")',
')',
'(print exception)',
')',
')',
')']

    interpreter = Interpreter()
    interpreter.run(program)

# TODO: current test case above is because when initializing the class -> field at the start
# or maybe even just work on exception because that has so many points to be earned
# main()
