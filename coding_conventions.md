# Variables
## Global
Pascal casing.

ExampleVariable

## Local
Camel case.

exampleVariable

# Classes
Pascal casing.

ExampleClass

# Functions
All functions must have a descriptor showing arguments, returns and what the function does.
This is the template for the descriptor:
```
    """Function explanation.

    Args:
        Name (Type): Explanation of the argument.

    Returns:
        Type: Explanation of the returned object. 
```` 
Example descriptor:
```
    """This serves as an example descriptor.

    Args:
        example_argument (int): Example integer argument.

    Returns:
        int: Example integer return. 
```` 
## Public
Lowercase, underscores as spaces.

example_function()

## Private
Lowercase, underscores as space, prefaced with underscore.

_example_function()

## Parameters
Lowercase, underscores as spaces.

example_function(example_parameter)