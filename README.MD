# Key Bot Presseer
Simple CLI program that presses sequence of keys when activated.

#### Parameters
JSON file should have the following parameters:
- "key": list of keys to be pressed. If not specified, action will be skipped automatically.
- "duration": how long keys will be pressed. Default: 0.1.
- "delay": delay between letting go of each key in list. Use this if for example, you need to charge a jump in game, so you have to hold jump key and direction key, but after letting go of jump key you still need to keep direction button pressed for a little while. Default: 0.0.
- "wait_time": wait time until next keypress. Default: 0.0.

Example JSON file is included in `configs` directory.