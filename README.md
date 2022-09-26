# Gerund
This package is responsible for compiling and running bash commands. 

## Install using pip
The package can be installed using the following command:
```bash
pip install git+https://github.com/OasisLMF/gerund.git
```

## Basic usage with environment variable
Gerund supports environment variables and chained commands out of the box. For instance, let us build a basic
script that gets environment variables and prints them out with the following:

```python
import os

print(os.environ.get('ONE'))
print(os.environ.get('TWO'))
```
We can call the script above ```run_test.py```. We can now run the following python code in another python
script:

```python
from gerund.commands.terminal_command import TerminalCommand

env_vars = {
    "ONE": "1",
    "TWO": "two",
    "THREE": "3"
}

test = TerminalCommand("python ./run_test.py", environment_variables=env_vars)
assert(['1', 'two'] == test.wait(capture_output=True))
```
what we can see is that outcomes are captured. If we set the ```capture_output``` to ```False``` the
outcome of the command will merely be printed out and nothing with be returned from the ```wait```
function. 

## Chaining commands
We can chain commands by passing in a list of commands like the code below:
```python
from gerund.commands.terminal_command import TerminalCommand

env_vars = {
    "ONE": "1",
    "TWO": "two",
    "THREE": "3"
}

test = TerminalCommand([f"python ./run_test.py", "echo 'test'"], environment_variables=env_vars)
assert(['1', 'two', 'test'] == test.wait(capture_output=True))
```
Here we can see that the python script has been executed first and the bash echo command have been executed
afterwards and also captured.

## Using variables from local storage
Gerund also supports storage throughout the running lifetime of the program. Let's say we load some variables
from a profile config file or something. We can make them available to all commands and reference them
in the command using the ```=>``` notation. An example of using local storage can be seen below:

```python
from gerund.commands.terminal_command import TerminalCommand
from gerund.components.local_variable_storage import LocalVariableStorage


env_vars = {
    "ONE": "1",
    "TWO": "two",
    "THREE": "3"
}
storage = LocalVariableStorage()
storage.update({
    "FOUR": "four",
    "SCRIPT_PATH": "./run_test.py"
})

test = TerminalCommand("python {=>SCRIPT_PATH}", environment_variables=env_vars)
assert(['1', 'two'] == test.wait(capture_output=True))
```
The very fact that the ```run_script.py``` runs at all is because the ```TerminalCommand``` understood
the ```{=>SCRIPT_PATH}``` notation and searched the ```LocalVariableStorage```. 

## Running commands on server
If we want to run a command on a server we can use the following parameters:
```python
from gerund.commands.terminal_command import TerminalCommand

env_vars = {
    "ONE": "1",
    "TWO": "two",
    "THREE": "3"
}

test = TerminalCommand('echo "test"', environment_variables=env_vars, ip_address="12345", 
                       username="ubuntu", key="./path/to/SomeKey.pem")
test.wait()
```

The ```username``` and ```key``` parameters are optional. If we do not define the ```username``` the default will be
"ubuntu". If we do not define a path to a key then the command will try and use the SSH agent. 
