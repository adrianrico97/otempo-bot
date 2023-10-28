
# Install dependencies

```bash
python -m pip install -r requirements.txt
```

Generate the `requirements.txt` file using:
```bash
python -m pip freeze > requirements.txt
```

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

# Examples

Aemet XML URL examples:

* Daily prediction in A Coruña: https://www.aemet.es/xml/municipios/localidad_15030.xml
* Hourly prediction in A Coruña: https://www.aemet.es/xml/municipios_h/localidad_h_15030.xml

# python-telegram-bot

**python-telegram-bot** is the library used to manage the Telegram connection. You can find the documentation [here](https://python-telegram-bot.readthedocs.io/en/stable/) and the wiki [here](https://github.com/python-telegram-bot/python-telegram-bot/wiki).
