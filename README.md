# LatencyGroove
Script to check the latency of trading bot sending API requests to exchange.

📊 Overview
This script is your latency watchdog 🐾! It fetches configuration settings from config.json, such as how often to schedule checks (scheduling_frequency_seconds), how many checks to run concurrently (number_of_checks), and which API endpoint to put to the test (api_endpoint).

It's a speedy little fella, running those latency checks in parallel using a thread pool 🚀, mimicking the lightning-fast operations of an HFT bot.

Once it's done its rounds, it doesn't just sit there twiddling its thumbs. Oh no! It crunches the numbers and logs fancy stats like average, median, and the 95th percentile of the latencies.

And guess what? It's also got a knack for handling errors 🛠️. If any requests fail, it makes a note of it and logs the details to a file.

But wait, there's more! It's not a one-time deal. Nope, it's in it for the long haul. The whole process loops at the frequency specified in the config file, tirelessly monitoring and logging latency over time.

📝 Note
Before you kick things off, make sure you've got the right gear installed. Just run pip install numpy requests to make sure you've got numpy and requests ready to roll 🛠️. And hey, feel free to tinker with config.json to tailor the setup to your specific needs or switch up the API endpoint for different kinds of latency tests.
