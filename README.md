
# Pipenv
To check if your virtual environment is activated, you can look at your terminal prompt. If your virtual environment is activated, you should see the name of the virtual environment in parentheses before your terminal prompt.

For example, if your virtual environment is named `myenv`, your terminal prompt might look like this:

```bash
(myenv) user@hostname:~/project$
```

If you don't see the name of your virtual environment in parentheses before your terminal prompt, your virtual environment is not activated. You can activate it by running the following command:

```bash
pipenv shell
```

This will activate the virtual environment and change your terminal prompt to indicate that you're now working inside the virtual environment.

Use *pipenv install* to install all the dependencies:
```bash
pipenv install
```
You can add a new package to your Pipfile using the following command:
```bash
pipenv install <package>
```
* https://pipenv-es.readthedocs.io/es/latest/basics.html

# Run the project
The following command will start the bot:
```bash
TELEGRAM_BOT_TOKEN=<telegram bot here> python bot.py
```

# Debugger
You can debugger the bot using the following library:
```python
import pdb

pdb.set_trace()
```