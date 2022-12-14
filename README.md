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

## Config files
Gerund handles config files when running a command. This is where we run a command that points to a config file which
has metadata and a chain of commands. For instance, we can define the following ```gerund.yml``` config file:

```yaml
output: "result.txt"
vars:
  one: 1
  two: two
env_vars:
  three: "3"
  four: four
commands:
  - "echo $three"
  - "echo $four"
  - "echo {=>one}"
```

We can then our config file with the following commands:

```bash
gerund --f path/to/gerund.yml
```

Because we have defined the ```output``` flat the output of the chain of commands will be captured and written to the
file defined. If the ```output``` field is not provided the output will merely be printed out to the console. We can
also define the following optional fields:

- **ip_address**: the IP address of where the command will run if provided
- **key**: path to the SSH pem key if running on a server
- **username**: username for the server if IP is provided

We can also provide the following file formats:

### Json

```json
{
  "output": "result.txt",
  "vars": {
    "one": 1,
    "two": "two"
  },
  "env_vars": {
    "three": "3",
    "four": "four"
  },
  "commands": [
    "echo $three",
    "echo $four",
    "echo {=>one}"
  ]
}
```

### txt

```
[meta]
output=result.txt

[vars]
one=1
two=two

[env_vars]
three=3
four=four

[commands]
echo $three
echo $four
echo {=>one}
```

## Bash scripts
Gerund supports bash scripts. You can either pass in a list of commands that will be written as a bash script, or you
can pass in a path to a bash script to be run. If the ```ip_address``` is passed in the bash script will be run on the
server belonging to the ```ip_address```. For instance, let us say that he has the following bash script:

```bash
#!/usr/bin/env bash

SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"
cd $SCRIPTPATH

ls
echo $ONE

if [ -d "/path/to/dir" ]
then
    echo "Directory /path/to/dir exists"
else
    echo "Directory /path/to/dir does not exist"
fi
```

we can point to this bash script and run it with the following code:

```python
from gerund.commands.bash_script import BashScript
from typing import Optional, List

example = BashScript(path="./path/to/script.sh")
outcome: Optional[List[str]] = example.wait()
```

The command version would take the following form:

```python
from gerund.commands.bash_script import BashScript
from typing import Optional, List

commands = [
            '#!/usr/bin/env bash',
            '',
            'SCRIPTPATH="$( cd "$(dirname "$0")" ; pwd -P )"',
            'cd $SCRIPTPATH',
            '',
            'ls',
            'echo $ONE',
            '',
            'if [ -d "/path/to/dir" ]',
            'then',
            '    echo "Directory /path/to/dir exists"',
            'else',
            '    echo "Directory /path/to/dir does not exist"',
            'fi',
            '',
            ''
        ]

example = BashScript(commands=commands)
outcome: Optional[List[str]] = example.wait()
```

The ```BashScript``` constructor supports the following inputs:

* **commands:** ```(Optional[List[str]])``` each element is a line in a bash script
* **path:** ```(Optional[str])``` path to bash script to be written or read
* **environment_variables:** ```(EnvVars)``` environment variables to be applied when running bash script
* **ip_address:** ```(Optional[str])``` IP address of the server to run the bash script if running on server
* **key:** ```(Optional[str])``` path to pem key if needed to be run on server
* **username:** ```(str)``` the username of the server which has a default of "ubuntu"
* **capture_output:** ```(bool)``` for the output to be captured with a default of False
